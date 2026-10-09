"""Depth-First Search (DFS) implementation for capital allocation."""

import time
from typing import List, Set, Tuple
from app.search.base import SearchAlgorithm, SearchNode, SearchResult
from app.domain.financial_problem import FinancialAllocationProblem


class DepthFirstSearch(SearchAlgorithm):
    """Uninformed Depth-First Search with depth bounding and cycle detection."""

    def __init__(self, max_depth: int = 50, max_states: int = 50000):
        super().__init__(name="Depth-First Search (DFS)")
        self.max_depth = max_depth
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
            )

        stack: List[SearchNode] = [root_node]
        explored: Set[Tuple] = set()
        states_explored = 0
        best_compliant_node = None

        while stack and states_explored < self.max_states:
            current_node = stack.pop()
            states_explored += 1

            sig = current_node.state.state_signature()
            if sig in explored:
                continue
            explored.add(sig)

            # Check goal test
            if problem.goal_test(current_node.state):
                best_compliant_node = current_node
                break

            if current_node.depth < self.max_depth:
                # Add successors to stack (LIFO)
                for action, next_state in problem.successors(current_node.state):
                    if next_state.state_signature() not in explored:
                        child = SearchNode(
                            state=next_state,
                            parent=current_node,
                            action=action,
                            path_cost=current_node.path_cost + 1.0,
                            depth=current_node.depth + 1
                        )
                        stack.append(child)

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
            final_state=root_node.state,
            actions=[],
            objective_value=root_node.state.utility_score(problem.risk_tolerance),
            expected_return=root_node.state.expected_return,
            risk_score=root_node.state.risk_score,
            liquidity_ratio=root_node.state.liquidity_ratio,
            states_explored=states_explored,
            execution_time_ms=elapsed_ms,
            depth=0,
            metadata={"reason": "DFS depth/state limit reached without finding compliant goal"}
        )
