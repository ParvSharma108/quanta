"""A* Search implementation for optimal capital allocation."""

import heapq
import time
from typing import Dict, Optional, Tuple
from app.search.base import SearchAlgorithm, SearchNode, SearchResult
from app.domain.financial_problem import FinancialAllocationProblem


class AStarSearch(SearchAlgorithm):
    """A* Search finding cost-optimal capital allocation via f(n) = g(n) + h(n)."""

    def __init__(self, max_states: int = 50000):
        super().__init__(name="A* Search")
        self.max_states = max_states

    def search(self, problem: FinancialAllocationProblem) -> SearchResult:
        start_time = time.perf_counter()
        
        h_root = problem.heuristic(problem.initial_state)
        root_node = SearchNode(
            state=problem.initial_state,
            path_cost=0.0,
            depth=0,
            heuristic_cost=h_root
        )

        frontier = []
        counter = 0
        heapq.heappush(frontier, (root_node.total_cost, counter, root_node))

        # cost_so_far maps state_signature -> lowest g(n) discovered
        cost_so_far: Dict[Tuple, float] = {problem.initial_state.state_signature(): 0.0}
        states_explored = 0
        best_compliant_node: Optional[SearchNode] = None

        while frontier and states_explored < self.max_states:
            f_score, _, current_node = heapq.heappop(frontier)
            states_explored += 1

            sig = current_node.state.state_signature()
            # If we found a cheaper path to this state already, skip
            if current_node.path_cost > cost_so_far.get(sig, float("inf")):
                continue

            # Goal test
            if problem.goal_test(current_node.state):
                best_compliant_node = current_node
                break

            for action, next_state in problem.successors(current_node.state):
                step_c = problem.step_cost(current_node.state, action, next_state)
                new_g = current_node.path_cost + step_c
                next_sig = next_state.state_signature()

                if new_g < cost_so_far.get(next_sig, float("inf")):
                    cost_so_far[next_sig] = new_g
                    h_score = problem.heuristic(next_state)
                    child = SearchNode(
                        state=next_state,
                        parent=current_node,
                        action=action,
                        path_cost=new_g,
                        depth=current_node.depth + 1,
                        heuristic_cost=h_score
                    )
                    counter += 1
                    heapq.heappush(frontier, (child.total_cost, counter, child))

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
                metadata={
                    "total_path_cost_g": best_compliant_node.path_cost,
                    "final_heuristic_h": best_compliant_node.heuristic_cost,
                    "closed_set_size": len(cost_so_far)
                }
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
            metadata={"reason": "A* search exhausted queue without finding compliant goal"}
        )
