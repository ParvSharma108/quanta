"""Unit tests for Risk Engine, Bayesian Reasoning, and Monte Carlo VaR."""

import pytest
from app.domain.asset import Asset, AssetType
from app.domain.financial_state import FinancialState
from app.risk.scoring import RiskEngine
from app.risk.bayesian import BayesianRiskNetwork, BayesianEvidence
from app.risk.sampling import MonteCarloRiskSimulator


@pytest.fixture
def asset_catalog():
    return {
        "gov_bond": Asset(id="gov_bond", name="Gov", asset_type=AssetType.GOV_BOND, expected_return=0.07, risk=0.05, liquidity=0.95),
        "equity": Asset(id="equity", name="Equity", asset_type=AssetType.EQUITY, expected_return=0.14, risk=0.40, liquidity=0.80),
    }


def test_deterministic_risk_scoring(asset_catalog):
    engine = RiskEngine()
    
    # Safe diversified state
    safe_state = FinancialState(
        total_capital=100.0,
        cash=20.0,
        allocations={"gov_bond": 60.0, "equity": 20.0},
        reserved_for_debt=0.0
    )
    safe_report = engine.analyze(safe_state, asset_catalog)
    assert safe_report.composite_risk_score >= 0.0
    assert safe_report.composite_risk_score <= 1.0
    assert safe_report.concentration_index_hhi > 0.0

    # High concentration state
    conc_state = FinancialState(
        total_capital=100.0,
        cash=0.0,
        allocations={"equity": 100.0},
        reserved_for_debt=0.0
    )
    conc_report = engine.analyze(conc_state, asset_catalog)
    assert conc_report.composite_risk_score > safe_report.composite_risk_score


def test_bayesian_risk_network_inference():
    bayes = BayesianRiskNetwork()
    
    # Unconditional prior inference
    prior_res = bayes.infer()
    assert 0.0 <= prior_res.p_recession <= 1.0
    assert 0.0 <= prior_res.p_liquidity_crisis <= 1.0
    assert prior_res.stress_multiplier >= 1.0

    # Stressed condition: Inflation + Rate Hike
    stressed_res = bayes.infer(BayesianEvidence(inflation_high=True, rate_hike=True))
    assert stressed_res.p_recession > prior_res.p_recession
    assert stressed_res.p_liquidity_crisis > prior_res.p_liquidity_crisis


def test_monte_carlo_var_simulation(asset_catalog):
    simulator = MonteCarloRiskSimulator(default_scenarios=500, seed=42)
    state = FinancialState(
        total_capital=100.0,
        cash=10.0,
        allocations={"gov_bond": 50.0, "equity": 40.0},
        reserved_for_debt=0.0
    )
    report = simulator.simulate(state, asset_catalog, num_scenarios=500)
    assert report.num_scenarios == 500
    assert report.var_95 >= 0.0
    assert report.cvar_95 >= report.var_95
