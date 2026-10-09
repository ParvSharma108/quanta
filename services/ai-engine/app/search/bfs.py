"""Breadth-First Search (BFS) implementation for capital allocation."""

import collections
import time
from typing import Set, Tuple
from app.search.base import SearchAlgorithm, SearchNode, SearchResult
from app.domain.financial_problem import FinancialAllocationProblem


class BreadthFirstSearch(SearchAlgorithm):
    """Uninformed Breadth-First Search exploring shallowest allocation branches first."""

    def __init__(self, max_states: int = 50000):
        super().__init__(name="Breadth-First Search (BFS)")
        self.max_states = max_states

    def search(self, problem: FinancialAllocationProblem) -> SearchResult:
        start_time = time.perf_counter()
        
        root_node = SearchNode(state=problem.initial_state, path_cost=0.0, depth=0)
        if problem.goal_test(root_node.state):
            elapsed_ms = (time.perf_counter() - start_time) * 1000.0
            return SearchResult(
                algorithm=self.name,
                success=True,
                final_state=root_node.state,
                actions=[],
                objective_value=root_node.state.utility_score(problem.risk_tolerance),
                expected_return=root_node.state.expected_return,
                risk_score=root_node.state.risk_score,
                liquidity_ratio=root_node.state.liquidity_ratio,
                states_explored=1,
                execution_time_ms=elapsed_ms,
                depth=0,
                metadata={"queue_size": 0}
            )

        frontier = collections.deque([root_node])
        explored: Set[Tuple] = {root_node.state.state_signature()}
        states_explored = 0
        best_compliant_node = None
        best_utility = -float("inf")

        while frontier and states_explored < self.max_states:
            current_node = frontier.popleft()
            states_explored += 1

            # Check if this terminal / deployed state satisfies goal
            if problem.goal_test(current_node.state):
                util = current_node.state.utility_score(problem.risk_tolerance)
                if util > best_utility:
                    best_utility = util
                    best_compliant_node = current_node
                    # In standard BFS, the first found goal at shallowest depth can be returned or evaluated
                    break

            for action, next_state in problem.successors(current_node.state):
                sig = next_state.state_signature()
                if sig not in explored:
                    explored.add(sig)
                    child_node = SearchNode(
                        state=next_state,
                        parent=current_node,
                        action=action,
                        path_cost=current_node.path_cost + 1.0,
                        depth=current_node.depth + 1
                    )
                    frontier.append(child_node)

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
                metadata={"explored_signatures": len(explored), "frontier_remaining": len(frontier)}
            )
        
        # Fallback to root or unreached
        return SearchResult(
            algorithm=self.name,
            success=False,
            final_state=root_node.state,
            actions=[],
            objective_value=root_node.state.utility_score(problem.risk_tolerance),
            expected_return=root_node.state.expected_return,
            risk_score=root_node.state.risk_score,
            liquidity_ratio=root_node.state.liquidity_ratio,
            states_explored=states_explored,
            execution_time_ms=elapsed_ms,
            depth=0,
            metadata={"reason": "No valid compliant goal found within max_states budget"}
        )
