"""Search algorithms package."""

from app.search.base import SearchAlgorithm, SearchNode, SearchResult
from app.search.bfs import BreadthFirstSearch
from app.search.dfs import DepthFirstSearch
from app.search.generate_and_test import GenerateAndTest
from app.search.hill_climbing import HillClimbingSearch
from app.search.best_first import BestFirstSearch
from app.search.astar import AStarSearch

__all__ = [
    "SearchAlgorithm",
    "SearchNode",
    "SearchResult",
    "BreadthFirstSearch",
    "DepthFirstSearch",
    "GenerateAndTest",
    "HillClimbingSearch",
    "BestFirstSearch",
    "AStarSearch",
]
