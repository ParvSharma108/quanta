"""Unit tests for Game Theory (Minimax, Alpha-Beta) and MDP Policy Solver."""

import pytest
from app.domain.asset import Asset, AssetType
from app.domain.financial_problem import FinancialProblem, FinancialAllocationProblem
from app.game.game_state import TreasuryGameState
from app.game.alpha_beta import AlphaBetaPruningSolver
from app.mdp.environment import TreasuryMDPEnvironment


@pytest.fixture
def mini_problem():
    assets = [
        Asset(id="gov_bond", name="Gov", asset_type=AssetType.GOV_BOND, expected_return=0.07, risk=0.05, liquidity=0.95),
        Asset(id="equity", name="Equity", asset_type=AssetType.EQUITY, expected_return=0.14, risk=0.40, liquidity=0.80),
    ]
    prob = FinancialProblem(
        capital=30.0,
        step_size=10.0,
        assets=assets,
        liabilities=[],
        constraints=[]
    )
    return FinancialAllocationProblem(prob)


def test_alpha_beta_adversarial_stress_test(mini_problem):
    solver = AlphaBetaPruningSolver(max_depth=3)
    stress_report = solver.stress_test(mini_problem)
    assert stress_report.nodes_evaluated > 0
    assert stress_report.worst_case_payoff != 0.0
    assert stress_report.best_treasury_action is not None


def test_mdp_value_iteration():
    env = TreasuryMDPEnvironment(gamma=0.90)
    report = env.value_iteration(max_iterations=100)
    assert report.iterations_to_converge > 0
    assert len(report.optimal_policy) == len(env.all_states)
    assert len(report.state_values) == len(env.all_states)
