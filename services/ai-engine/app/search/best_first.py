"""Greedy Best-First Search implementation for capital allocation."""

import heapq
import time
from typing import Dict, Set, Tuple
from app.search.base import SearchAlgorithm, SearchNode, SearchResult
from app.domain.financial_problem import FinancialAllocationProblem


class BestFirstSearch(SearchAlgorithm):
    """Informed Greedy Best-First Search expanding nodes with minimal heuristic cost."""

    def __init__(self, max_states: int = 50000):
        super().__init__(name="Greedy Best-First Search")
        self.max_states = max_states

    def search(self, problem: FinancialAllocationProblem) -> SearchResult:
        start_time = time.perf_counter()
        
        # Priority queue ordered purely by heuristic cost h(n)
        h_init = problem.heuristic(problem.initial_state)
        root_node = SearchNode(
            state=problem.initial_state,
            path_cost=0.0,
            depth=0,
            heuristic_cost=h_init
        )

        frontier = []
        counter = 0
        heapq.heappush(frontier, (h_init, counter, root_node))
        
        explored: Set[Tuple] = set()
        states_explored = 0
        best_compliant_node = None

        while frontier and states_explored < self.max_states:
            _, _, current_node = heapq.heappop(frontier)
            states_explored += 1

            sig = current_node.state.state_signature()
            if sig in explored:
                continue
            explored.add(sig)

            # Goal test
            if problem.goal_test(current_node.state):
                best_compliant_node = current_node
                break

            for action, next_state in problem.successors(current_node.state):
                if next_state.state_signature() not in explored:
                    h_val = problem.heuristic(next_state)
                    # Add penalty if next state violates constraints
                    evals = problem.evaluate_constraints(next_state)
                    penalty = sum(e.penalty for e in evals if not e.satisfied)
                    
                    child = SearchNode(
                        state=next_state,
                        parent=current_node,
                        action=action,
                        path_cost=current_node.path_cost + 1.0,
                        depth=current_node.depth + 1,
                        heuristic_cost=h_val
                    )
                    counter += 1
                    priority = h_val + penalty * 0.05
                    heapq.heappush(frontier, (priority, counter, child))

        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        if best_compliant_node:
            final_st = best_compliant_node.state
            return SearchResult(
                algorithm=self.name,
                success=True,
                final_state=final_st,
                actions=best_compliant_node.get_path(),
                objective_value=final_st.utility_score(problem.risk_tolerance),
                expected_return=final_st.expected_return,
                risk_score=final_st.risk_score,
                liquidity_ratio=final_st.liquidity_ratio,
                states_explored=states_explored,
                execution_time_ms=elapsed_ms,
                depth=best_compliant_node.depth,
                metadata={"explored_states": len(explored)}
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
            metadata={"reason": "Greedy Best-First Search exhausted frontier without valid goal"}
        )
