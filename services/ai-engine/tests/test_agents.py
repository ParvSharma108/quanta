"""Unit tests for Intelligent Agents Council."""

import pytest
from app.domain.asset import Asset, AssetType
from app.domain.liability import Liability
from app.domain.constraint import Constraint, ConstraintType
from app.domain.financial_problem import FinancialProblem, FinancialAllocationProblem
from app.agents.treasury_agent import TreasuryAgent
from app.agents.risk_agent import RiskAgent
from app.agents.compliance_agent import ComplianceAgent
from app.agents.decision_agent import DecisionAgent


@pytest.fixture
def problem_fixture():
    assets = [
        Asset(id="gov_bond", name="Gov Bonds", asset_type=AssetType.GOV_BOND, expected_return=0.07, risk=0.05, liquidity=0.95),
        Asset(id="equity", name="Equity", asset_type=AssetType.EQUITY, expected_return=0.14, risk=0.40, liquidity=0.80),
    ]
    liabilities = [
        Liability(id="debt_1", name="Senior Debt", principal=15.0, interest_rate=0.08, priority=1, is_mandatory_reserve=True)
    ]
    constraints = [
        Constraint(id="c_liq", constraint_type=ConstraintType.MINIMUM_LIQUIDITY, parameters={"threshold": 0.20}),
        Constraint(id="c_debt", constraint_type=ConstraintType.DEBT_RESERVE, parameters={"amount": 15.0}),
    ]
    problem = FinancialProblem(
        capital=100.0,
        step_size=5.0,
        assets=assets,
        liabilities=liabilities,
        constraints=constraints,
        risk_tolerance=0.50,
        minimum_liquidity=0.20
    )
    return FinancialAllocationProblem(problem)


def test_treasury_agent_proposals(problem_fixture):
    agent = TreasuryAgent()
    assessment = agent.perceive_and_assess(problem_fixture.initial_state, problem_fixture)
    assert assessment.is_acceptable
    assert len(assessment.suggested_actions) > 0


def test_compliance_agent_debt_check(problem_fixture):
    agent = ComplianceAgent()
    # Initial state has 0 debt reserve -> non-compliant
    assessment = agent.perceive_and_assess(problem_fixture.initial_state, problem_fixture)
    assert not assessment.is_acceptable
    assert len(assessment.suggested_actions) > 0


def test_decision_agent_synthesis(problem_fixture):
    decision_agent = DecisionAgent()
    deliberation = decision_agent.synthesize_strategy(problem_fixture)
    assert deliberation.recommended_strategy is not None
    assert deliberation.recommended_strategy.is_compliant
    assert deliberation.recommended_strategy.total_allocated > 0
    assert deliberation.consensus_reached
