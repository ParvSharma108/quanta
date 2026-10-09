"""Base classes and standardized interfaces for search algorithms."""

from __future__ import annotations
from abc import ABC, abstractmethod
import time
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, Field

from app.domain.financial_state import FinancialState
from app.domain.strategy import FinancialAction
from app.domain.financial_problem import FinancialAllocationProblem


class SearchResult(BaseModel):
    """Standardized search outcome returned by all search algorithms.
    
    Attributes:
        algorithm: Name of the executed algorithm.
        success: Boolean flag indicating if a valid goal state was reached.
        final_state: Resulting terminal financial state.
        actions: Sequence of actions executed from initial to final state.
        objective_value: Evaluated utility / fitness score.
        expected_return: Portfolio annual expected return fraction.
        risk_score: Portfolio normalized composite risk score [0, 1].
        liquidity_ratio: Portfolio weighted liquidity factor [0, 1].
        states_explored: Number of state nodes visited during search.
        execution_time_ms: Search wall-clock runtime in milliseconds.
        depth: Depth in search tree of final state.
        metadata: Diagnostic metrics (e.g. max_frontier_size, prune_count).
    """
    algorithm: str
    success: bool
    final_state: Optional[FinancialState] = None
    actions: List[FinancialAction] = Field(default_factory=list)
    objective_value: float = 0.0
    expected_return: float = 0.0
    risk_score: float = 0.0
    liquidity_ratio: float = 1.0
    states_explored: int = 0
    execution_time_ms: float = 0.0
    depth: int = 0
    metadata: Dict[str, Any] = Field(default_factory=dict)


class SearchNode:
    """Tree/Graph node for search algorithms encapsulating state and path history."""

    def __init__(
        self,
        state: FinancialState,
        parent: Optional[SearchNode] = None,
        action: Optional[FinancialAction] = None,
        path_cost: float = 0.0,
        depth: int = 0,
        heuristic_cost: float = 0.0
    ):
        self.state = state
        self.parent = parent
        self.action = action
        self.path_cost = path_cost  # g(n)
        self.depth = depth
        self.heuristic_cost = heuristic_cost  # h(n)
        self.total_cost = path_cost + heuristic_cost  # f(n)

    def get_path(self) -> List[FinancialAction]:
        """Reconstruct action sequence from root to current node."""
        actions: List[FinancialAction] = []
        curr: Optional[SearchNode] = self
        while curr and curr.action:
            actions.append(curr.action)
            curr = curr.parent
        return list(reversed(actions))

    def __lt__(self, other: SearchNode) -> bool:
        """Priority queue comparator for cost-based searches."""
        if self.total_cost == other.total_cost:
            return self.depth > other.depth  # Prefer deeper nodes on ties
        return self.total_cost < other.total_cost


class SearchAlgorithm(ABC):
    """Abstract base class for all informed and uninformed search strategies."""

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def search(self, problem: FinancialAllocationProblem) -> SearchResult:
        """Execute search on the provided financial problem."""
        pass
