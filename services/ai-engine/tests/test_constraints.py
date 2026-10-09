"""Unit tests for constraint audits and CSP backtracking solver."""

import pytest
from app.domain.asset import Asset, AssetType
from app.domain.constraint import Constraint, ConstraintType, ConstraintSeverity
from app.domain.financial_state import FinancialState
from app.domain.financial_problem import FinancialProblem, FinancialAllocationProblem
from app.csp.model import CSPModel
from app.csp.constraints import ExactSumConstraint, DebtReserveCSPConstraint, MinimumLiquidityCSPConstraint
from app.csp.solver import CSPSolver


def test_constraint_auditing_pass_and_fail():
    assets = [
        Asset(id="equity", name="Equity", asset_type=AssetType.EQUITY, expected_return=0.14, risk=0.40, liquidity=0.80)
    ]
    constraints = [
        Constraint(
            id="c_max_risk",
            constraint_type=ConstraintType.MAXIMUM_RISK,
            parameters={"threshold": 0.20},
            severity=ConstraintSeverity.CRITICAL
        )
    ]
    problem = FinancialProblem(
        capital=100.0,
        assets=assets,
        liabilities=[],
        constraints=constraints,
        minimum_liquidity=0.20
    )
    search_problem = FinancialAllocationProblem(problem)

    # State with 100% equity -> High risk -> Should fail constraint
    risky_state = FinancialState(
        total_capital=100.0,
        cash=0.0,
        allocations={"equity": 100.0},
        reserved_for_debt=0.0,
    )
    evals = search_problem.evaluate_constraints(risky_state)
    risk_eval = next(e for e in evals if e.constraint_id == "c_max_risk")
    assert not risk_eval.satisfied
    assert not search_problem.is_state_compliant(risky_state)


def test_csp_backtracking_solver():
    # CSP formulation for 3 buckets summing to 50
    model = CSPModel()
    domain = [0.0, 10.0, 20.0, 30.0, 40.0, 50.0]
    model.add_variable("cash", domain)
    model.add_variable("debt_reserve", domain)
    model.add_variable("gov_bond", domain)

    # Constraints
    model.add_constraint(ExactSumConstraint(["cash", "debt_reserve", "gov_bond"], total_sum=50.0))
    model.add_constraint(DebtReserveCSPConstraint("debt_reserve", min_required=10.0))
    model.add_constraint(
        MinimumLiquidityCSPConstraint(
            variables=["cash", "debt_reserve", "gov_bond"],
            liquidity_weights={"cash": 1.0, "debt_reserve": 1.0, "gov_bond": 0.95},
            total_capital=50.0,
            min_liquidity=0.50
        )
    )

    solver = CSPSolver(model)
    result = solver.solve()

    assert result.success
    assert result.assignment is not None
    assert sum(result.assignment.values()) == 50.0
    assert result.assignment["debt_reserve"] >= 10.0
