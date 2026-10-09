"""Unit tests for financial domain models and state transitions."""

import pytest
from app.domain.asset import Asset, AssetType
from app.domain.liability import Liability
from app.domain.constraint import Constraint, ConstraintType, ConstraintSeverity
from app.domain.strategy import FinancialAction, FinancialActionType
from app.domain.financial_state import FinancialState
from app.domain.financial_problem import FinancialProblem, FinancialAllocationProblem


@pytest.fixture
def sample_assets():
    return [
        Asset(
            id="gov_bond",
            name="Government Bonds",
            asset_type=AssetType.GOV_BOND,
            expected_return=0.07,
            risk=0.05,
            liquidity=0.95
        ),
        Asset(
            id="equity",
            name="Equity",
            asset_type=AssetType.EQUITY,
            expected_return=0.14,
            risk=0.40,
            liquidity=0.80
        ),
    ]


@pytest.fixture
def sample_liabilities():
    return [
        Liability(
            id="loan_1",
            name="Bank Term Loan",
            principal=15.0,
            interest_rate=0.08,
            priority=1,
            is_mandatory_reserve=True
        )
    ]


def test_asset_validation():
    with pytest.raises(ValueError):
        Asset(id="a1", name="", asset_type=AssetType.CASH, expected_return=0.05, risk=0.1, liquidity=0.9)


def test_financial_state_balance_conservation(sample_assets, sample_liabilities):
    state = FinancialState(
        total_capital=100.0,
        cash=85.0,
        allocations={"gov_bond": 0.0, "equity": 0.0},
        liabilities=sample_liabilities,
        reserved_for_debt=15.0,
    )
    assert state.is_valid()

    # Invalid state where sum does not match total_capital
    invalid_state = FinancialState(
        total_capital=100.0,
        cash=50.0,
        allocations={"gov_bond": 20.0},
        liabilities=sample_liabilities,
        reserved_for_debt=10.0,
    )
    assert not invalid_state.is_valid()


def test_state_transitions_apply_action(sample_assets):
    assets_map = {a.id: a for a in sample_assets}
    initial_state = FinancialState(
        total_capital=100.0,
        cash=100.0,
        allocations={"gov_bond": 0.0, "equity": 0.0},
        reserved_for_debt=0.0,
    )

    # 1. Action: Reserve Capital
    act_reserve = FinancialAction(
        action_type=FinancialActionType.RESERVE_CAPITAL,
        amount=15.0,
        reason="Reserve for debt"
    )
    st1 = initial_state.apply_action(act_reserve, assets_map)
    assert st1.cash == 85.0
    assert st1.reserved_for_debt == 15.0
    assert st1.is_valid()

    # 2. Action: Invest in Equity
    act_invest = FinancialAction(
        action_type=FinancialActionType.INVEST,
        asset_id="equity",
        amount=20.0,
        reason="Invest in equity"
    )
    st2 = st1.apply_action(act_invest, assets_map)
    assert st2.cash == 65.0
    assert st2.allocations["equity"] == 20.0
    assert st2.reserved_for_debt == 15.0
    assert st2.is_valid()

    # Verify immutability: st1 is unchanged
    assert st1.cash == 85.0
    assert st1.allocations.get("equity", 0.0) == 0.0


def test_financial_allocation_problem_successors(sample_assets, sample_liabilities):
    problem = FinancialProblem(
        capital=100.0,
        step_size=10.0,
        assets=sample_assets,
        liabilities=sample_liabilities,
        constraints=[],
        risk_tolerance=0.50,
        minimum_liquidity=0.20
    )
    search_problem = FinancialAllocationProblem(problem)

    initial_st = search_problem.initial_state
    succs = search_problem.successors(initial_st)
    assert len(succs) > 0

    # Ensure all successor states preserve balance conservation
    for act, next_st in succs:
        assert next_st.is_valid()
