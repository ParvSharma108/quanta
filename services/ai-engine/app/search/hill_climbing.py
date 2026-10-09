"""Hill Climbing local search implementation for portfolio optimization."""

import random
import time
from typing import List, Optional, Tuple
from app.search.base import SearchAlgorithm, SearchResult
from app.domain.financial_state import FinancialState
from app.domain.strategy import FinancialAction, FinancialActionType
from app.domain.financial_problem import FinancialAllocationProblem


class HillClimbingSearch(SearchAlgorithm):
    """Steepest-Ascent Hill Climbing with neighborhood rebalancing and restarts."""

    def __init__(self, max_iterations: int = 1000, num_restarts: int = 5):
        super().__init__(name="Hill Climbing (Steepest Ascent)")
        self.max_iterations = max_iterations
        self.num_restarts = num_restarts

    def _generate_neighborhood(
        self, state: FinancialState, problem: FinancialAllocationProblem
    ) -> List[Tuple[FinancialAction, FinancialState]]:
        """Generate neighboring states by shifting capital quanta between buckets."""
        neighbors: List[Tuple[FinancialAction, FinancialState]] = []
        step = problem.step_size

        # 1. Direct successors from current unallocated cash
        if state.cash >= (step - 1e-4):
            return problem.successors(state)

        # 2. Neighborhood shifts (Rebalancing between assets / cash)
        active_assets = [a_id for a_id, amt in state.allocations.items() if amt >= (step - 1e-4)]
        
        for from_asset_id in active_assets:
            for to_asset in problem.assets_list:
                if to_asset.id == from_asset_id:
                    continue
                
                # Check cap on target asset
                curr_target = state.allocations.get(to_asset.id, 0.0)
                if to_asset.max_investment is not None and (curr_target + step) > to_asset.max_investment:
                    continue

                # Create shifted candidate
                cloned = state.clone()
                cloned.allocations[from_asset_id] = round(cloned.allocations[from_asset_id] - step, 6)
                cloned.allocations[to_asset.id] = round(cloned.allocations.get(to_asset.id, 0.0) + step, 6)
                
                act = FinancialAction(
                    action_type=FinancialActionType.REBALANCE,
                    asset_id=to_asset.id,
                    amount=step,
                    reason=f"Shift ₹{step:.2f} Cr from {from_asset_id} to {to_asset.name}"
                )
                cloned.history.append(act)
                cloned.expected_return = cloned.calculate_expected_return(problem.assets_map)
                cloned.liquidity_ratio = cloned.calculate_liquidity(problem.assets_map)
                cloned.risk_score = cloned.calculate_risk(problem.assets_map)
                neighbors.append((act, cloned))

        return neighbors

    def _evaluate_state_fitness(self, state: FinancialState, problem: FinancialAllocationProblem) -> float:
        """Compute fitness with penalty for constraint violations."""
        base_util = state.utility_score(problem.risk_tolerance)
        evals = problem.evaluate_constraints(state)
        penalty = sum(e.penalty for e in evals if not e.satisfied)
        return base_util - penalty * 2.0

    def search(self, problem: FinancialAllocationProblem) -> SearchResult:
        start_time = time.perf_counter()
        
        best_global_state: Optional[FinancialState] = None
        best_global_fitness = -float("inf")
        states_explored = 0

        for restart_idx in range(self.num_restarts):
            # Phase 1: Construct an initial greedy or random feasible allocation
            current_state = problem.initial_state.clone()
            
            # Ensure debt reserve is met
            if problem.mandatory_debt_reserve > 0:
                act_debt = FinancialAction(
                    action_type=FinancialActionType.RESERVE_CAPITAL,
                    amount=problem.mandatory_debt_reserve,
                    reason="Initial debt reserve"
                )
                current_state = current_state.apply_action(act_debt, problem.assets_map)

            # Greedy initial fill
            while current_state.cash >= (problem.step_size - 1e-4):
                succs = problem.successors(current_state)
                if not succs:
                    break
                if restart_idx == 0:
                    # Pure greedy on first run
                    best_next = max(succs, key=lambda pair: self._evaluate_state_fitness(pair[1], problem))
                    current_state = best_next[1]
                else:
                    # Stochastic exploration on restarts
                    chosen = random.choice(succs)
                    current_state = chosen[1]
                states_explored += 1

            current_fitness = self._evaluate_state_fitness(current_state, problem)

            # Phase 2: Steepest Ascent Hill Climbing on neighborhood
            iterations = 0
            while iterations < self.max_iterations:
                iterations += 1
                neighbors = self._generate_neighborhood(current_state, problem)
                if not neighbors:
                    break

                states_explored += len(neighbors)
                
                # Find steepest improving neighbor
                best_neighbor_act, best_neighbor_state = max(
                    neighbors, key=lambda pair: self._evaluate_state_fitness(pair[1], problem)
                )
                best_neighbor_fitness = self._evaluate_state_fitness(best_neighbor_state, problem)

                if best_neighbor_fitness > current_fitness + 1e-5:
                    current_fitness = best_neighbor_fitness
                    current_state = best_neighbor_state
                else:
                    # Local peak reached
                    break

            if problem.is_state_compliant(current_state) and current_fitness > best_global_fitness:
                best_global_fitness = current_fitness
                best_global_state = current_state

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        if best_global_state:
            return SearchResult(
                algorithm=self.name,
                success=True,
                final_state=best_global_state,
                actions=best_global_state.history,
                objective_value=best_global_state.utility_score(problem.risk_tolerance),
                expected_return=best_global_state.expected_return,
                risk_score=best_global_state.risk_score,
                liquidity_ratio=best_global_state.liquidity_ratio,
                states_explored=states_explored,
                execution_time_ms=elapsed_ms,
                depth=len(best_global_state.history),
                metadata={"restarts_executed": self.num_restarts}
            )

        return SearchResult(
            algorithm=self.name,
            success=False,
            final_state=problem.initial_state,
            actions=[],
            objective_value=0.0,
            expected_return=0.0,
            risk_score=0.0,
            liquidity_ratio=1.0,
            states_explored=states_explored,
            execution_time_ms=elapsed_ms,
            depth=0,
            metadata={"reason": "Hill climbing could not find compliant local optimum"}
        )
