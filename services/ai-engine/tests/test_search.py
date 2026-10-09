"""Unit tests for search algorithms on FinancialAllocationProblem."""

import pytest
from app.domain.asset import Asset, AssetType
from app.domain.liability import Liability
from app.domain.constraint import Constraint, ConstraintType
from app.domain.financial_problem import FinancialProblem, FinancialAllocationProblem
from app.search.bfs import BreadthFirstSearch
from app.search.dfs import DepthFirstSearch
from app.search.generate_and_test import GenerateAndTest
from app.search.hill_climbing import HillClimbingSearch
from app.search.best_first import BestFirstSearch
from app.search.astar import AStarSearch


@pytest.fixture
def standard_problem():
    assets = [
        Asset(id="gov_bond", name="Gov Bonds", asset_type=AssetType.GOV_BOND, expected_return=0.07, risk=0.05, liquidity=0.95),
        Asset(id="equity", name="Equity", asset_type=AssetType.EQUITY, expected_return=0.14, risk=0.40, liquidity=0.80),
    ]
    liabilities = [
        Liability(id="debt_1", name="Senior Debt", principal=10.0, interest_rate=0.08, priority=1, is_mandatory_reserve=True)
    ]
    constraints = [
        Constraint(
            id="c_min_liq",
            constraint_type=ConstraintType.MINIMUM_LIQUIDITY,
            parameters={"threshold": 0.20}
        ),
        Constraint(
            id="c_max_equity",
            constraint_type=ConstraintType.MAXIMUM_ASSET_TYPE_EXPOSURE,
            parameters={"asset_type": "equity", "max_fraction": 0.40}
        ),
    ]
    return FinancialProblem(
        capital=50.0,
        step_size=10.0,
        assets=assets,
        liabilities=liabilities,
        constraints=constraints,
        risk_tolerance=0.50,
        minimum_liquidity=0.20
    )


def test_bfs_search(standard_problem):
    search_problem = FinancialAllocationProblem(standard_problem)
    solver = BreadthFirstSearch()
    result = solver.search(search_problem)

    assert result.success
    assert result.final_state is not None
    assert result.final_state.reserved_for_debt >= 10.0
    assert result.states_explored > 0
    assert search_problem.is_state_compliant(result.final_state)


def test_dfs_search(standard_problem):
    search_problem = FinancialAllocationProblem(standard_problem)
    solver = DepthFirstSearch(max_depth=15)
    result = solver.search(search_problem)

    assert result.success
    assert result.final_state is not None
    assert search_problem.is_state_compliant(result.final_state)


def test_generate_and_test(standard_problem):
    search_problem = FinancialAllocationProblem(standard_problem)
    solver = GenerateAndTest()
    result = solver.search(search_problem)

    assert result.success
    assert result.final_state is not None
    assert search_problem.is_state_compliant(result.final_state)


def test_hill_climbing(standard_problem):
    search_problem = FinancialAllocationProblem(standard_problem)
    solver = HillClimbingSearch(num_restarts=3)
    result = solver.search(search_problem)

    assert result.success
    assert result.final_state is not None
    assert search_problem.is_state_compliant(result.final_state)


def test_best_first_search(standard_problem):
    search_problem = FinancialAllocationProblem(standard_problem)
    solver = BestFirstSearch()
    result = solver.search(search_problem)

    assert result.success
    assert result.final_state is not None
    assert search_problem.is_state_compliant(result.final_state)


def test_astar_search(standard_problem):
    search_problem = FinancialAllocationProblem(standard_problem)
    solver = AStarSearch()
    result = solver.search(search_problem)

    assert result.success
    assert result.final_state is not None
    assert result.final_state.reserved_for_debt >= 10.0
    assert search_problem.is_state_compliant(result.final_state)
    assert result.expected_return > 0.03  # Outperformed pure cash
