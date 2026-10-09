"""Generate-and-Test search implementation for capital allocation."""

import itertools
import time
from typing import Dict, List, Optional
from app.search.base import SearchAlgorithm, SearchResult
from app.domain.financial_state import FinancialState
from app.domain.strategy import FinancialAction, FinancialActionType
from app.domain.financial_problem import FinancialAllocationProblem


class GenerateAndTest(SearchAlgorithm):
    """Systematic Generate-and-Test exploring discrete portfolio partitions."""

    def __init__(self, max_candidates: int = 20000):
        super().__init__(name="Generate-and-Test")
        self.max_candidates = max_candidates

    def search(self, problem: FinancialAllocationProblem) -> SearchResult:
        start_time = time.perf_counter()
        
        step = problem.step_size
        total_quanta = int(round(problem.capital / step))
        num_assets = len(problem.assets_list)
        
        # Mandatory debt reserve quanta
        debt_quanta_req = int(round(problem.mandatory_debt_reserve / step))

        best_state: Optional[FinancialState] = None
        best_utility = -float("inf")
        states_explored = 0
        valid_candidates_count = 0

        # Assets + Debt Reserve + Cash remainder = total_quanta
        # We generate partitions of total_quanta into (num_assets + 2) buckets:
        # assets[0...num_assets-1], debt_reserve, cash_retained
        
        # To handle scale efficiently, we use recursive bounded generation
        def generate_partitions(remaining_quanta: int, index: int, current_alloc: List[int]):
            nonlocal states_explored, valid_candidates_count, best_state, best_utility
            if states_explored >= self.max_candidates:
                return

            if index == num_assets:
                # Earmark debt reserve and remaining cash
                for debt_q in range(debt_quanta_req, remaining_quanta + 1):
                    cash_q = remaining_quanta - debt_q
                    states_explored += 1

                    # Build candidate state
                    alloc_dict: Dict[str, float] = {}
                    for i, asset in enumerate(problem.assets_list):
                        alloc_dict[asset.id] = float(current_alloc[i] * step)

                    cand_state = FinancialState(
                        total_capital=problem.capital,
                        cash=float(cash_q * step),
                        allocations=alloc_dict,
                        liabilities=problem.liabilities_list,
                        reserved_for_debt=float(debt_q * step),
                        market_state=problem.problem.market_state,
                        history=[]
                    )
                    
                    # Update analytical metrics
                    cand_state.expected_return = cand_state.calculate_expected_return(problem.assets_map)
                    cand_state.liquidity_ratio = cand_state.calculate_liquidity(problem.assets_map)
                    cand_state.risk_score = cand_state.calculate_risk(problem.assets_map)

                    # TEST: Evaluate hard constraints
                    if problem.is_state_compliant(cand_state):
                        valid_candidates_count += 1
                        util = cand_state.utility_score(problem.risk_tolerance)
                        if util > best_utility:
                            best_utility = util
                            best_state = cand_state

                    if states_explored >= self.max_candidates:
                        return
                return

            # For asset at 'index', check individual max cap if present
            asset = problem.assets_list[index]
            max_q = remaining_quanta
            if asset.max_investment is not None:
                max_q = min(max_q, int(round(asset.max_investment / step)))

            for q in range(0, max_q + 1):
                generate_partitions(remaining_quanta - q, index + 1, current_alloc + [q])

        generate_partitions(total_quanta, 0, [])

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        if best_state:
            # Construct synthetic action list for history
            actions: List[FinancialAction] = []
            if best_state.reserved_for_debt > 0:
                actions.append(FinancialAction(
                    action_type=FinancialActionType.RESERVE_CAPITAL,
                    amount=best_state.reserved_for_debt,
                    reason="Mandatory debt reserve"
                ))
            for a_id, amt in best_state.allocations.items():
                if amt > 0:
                    actions.append(FinancialAction(
                        action_type=FinancialActionType.INVEST,
                        asset_id=a_id,
                        amount=amt,
                        reason=f"Allocated ₹{amt:.2f} Cr"
                    ))
            if best_state.cash > 0:
                actions.append(FinancialAction(
                    action_type=FinancialActionType.HOLD_CASH,
                    amount=best_state.cash,
                    reason="Retained cash buffer"
                ))
            best_state.history = actions

            return SearchResult(
                algorithm=self.name,
                success=True,
                final_state=best_state,
                actions=actions,
                objective_value=best_utility,
                expected_return=best_state.expected_return,
                risk_score=best_state.risk_score,
                liquidity_ratio=best_state.liquidity_ratio,
                states_explored=states_explored,
                execution_time_ms=elapsed_ms,
                depth=len(actions),
                metadata={"valid_compliant_candidates": valid_candidates_count}
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
            metadata={"reason": "No compliant candidate found in generated space"}
        )
