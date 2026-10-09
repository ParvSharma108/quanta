"""Minimax adversarial game search for worst-case stress testing."""

from typing import Dict, List, Optional, Tuple
from app.game.game_state import TreasuryGameState, MarketShockAction
from app.domain.financial_problem import FinancialAllocationProblem
from app.domain.strategy import FinancialAction


MARKET_SHOCK_ACTIONS: List[MarketShockAction] = [
    MarketShockAction(
        shock_name="Status Quo",
        equity_drawdown=0.0,
        credit_spread_spike=0.0,
        liquidity_freeze=0.0,
        description="Benign macroeconomic environment"
    ),
    MarketShockAction(
        shock_name="Liquidity Squeeze",
        equity_drawdown=-0.10,
        credit_spread_spike=-0.05,
        liquidity_freeze=-0.25,
        description="Short-term commercial paper and liquidity freeze"
    ),
    MarketShockAction(
        shock_name="Macro Stagflation & Rate Shock",
        equity_drawdown=-0.20,
        credit_spread_spike=-0.12,
        liquidity_freeze=-0.15,
        description="Central bank rate hike spike causing credit spread widening"
    ),
    MarketShockAction(
        shock_name="Severe Equity & Credit Crash",
        equity_drawdown=-0.35,
        credit_spread_spike=-0.20,
        liquidity_freeze=-0.30,
        description="Systemic black swan crisis with simultaneous drawdowns"
    ),
]


class MinimaxSolver:
    """Minimax tree search evaluator for robust capital allocation."""

    def __init__(self, max_depth: int = 3):
        self.max_depth = max_depth
        self.nodes_evaluated = 0

    def minimax(
        self,
        node: TreasuryGameState,
        problem: FinancialAllocationProblem,
        depth: int,
        is_maximizing: bool
    ) -> float:
        """Recursive minimax evaluation."""
        self.nodes_evaluated += 1

        if depth >= self.max_depth or node.is_terminal(self.max_depth):
            return node.evaluate_payoff(problem.risk_tolerance)

        if is_maximizing:
            # MAX turn: Treasury chooses highest utility action
            max_eval = -float("inf")
            succs = problem.successors(node.financial_state)
            if not succs:
                return node.evaluate_payoff(problem.risk_tolerance)

            for act, next_st in succs:
                child = TreasuryGameState(
                    financial_state=next_st,
                    assets_map=node.assets_map,
                    is_max_turn=False,
                    active_shock=node.active_shock,
                    depth=depth + 1
                )
                eval_score = self.minimax(child, problem, depth + 1, is_maximizing=False)
                max_eval = max(max_eval, eval_score)
            return max_eval
        else:
            # MIN turn: Market adversary chooses the most damaging shock
            min_eval = float("inf")
            for shock in MARKET_SHOCK_ACTIONS:
                child = TreasuryGameState(
                    financial_state=node.financial_state,
                    assets_map=node.assets_map,
                    is_max_turn=True,
                    active_shock=shock,
                    depth=depth + 1
                )
                eval_score = self.minimax(child, problem, depth + 1, is_maximizing=True)
                min_eval = min(min_eval, eval_score)
            return min_eval
