"""Monte Carlo scenario sampling and Value-at-Risk (VaR) estimation."""

from typing import Dict, List, Optional
import numpy as np
from pydantic import BaseModel, Field
from app.domain.asset import Asset
from app.domain.financial_state import FinancialState


class MonteCarloSimulationReport(BaseModel):
    """Statistical simulation report for portfolio loss distribution."""
    num_scenarios: int
    mean_simulated_return: float
    std_simulated_return: float
    var_95: float = Field(..., description="Value at Risk at 95% confidence (annual fraction)")
    cvar_95: float = Field(..., description="Conditional Value at Risk / Expected Shortfall at 95%")
    var_99: float = Field(..., description="Value at Risk at 99% confidence")
    cvar_99: float = Field(..., description="Conditional Value at Risk at 99%")
    worst_case_loss_pct: float
    probability_of_loss: float


class MonteCarloRiskSimulator:
    """Simulates multivariate stochastic returns for a given financial state."""

    def __init__(self, default_scenarios: int = 2000, seed: Optional[int] = 42):
        self.default_scenarios = default_scenarios
        self.seed = seed

    def simulate(
        self,
        state: FinancialState,
        assets_map: Dict[str, Asset],
        num_scenarios: Optional[int] = None
    ) -> MonteCarloSimulationReport:
        """Generate correlated return scenarios and compute parametric / historical VaR."""
        n_sims = num_scenarios or self.default_scenarios
        rng = np.random.default_rng(self.seed)

        active_allocations = [
            (a_id, amt) for a_id, amt in state.allocations.items()
            if a_id in assets_map and amt > 0
        ]
        
        total_cap = state.total_capital
        if not active_allocations or total_cap <= 0:
            # All cash state
            return MonteCarloSimulationReport(
                num_scenarios=n_sims,
                mean_simulated_return=0.03,
                std_simulated_return=0.001,
                var_95=0.0,
                cvar_95=0.0,
                var_99=0.0,
                cvar_99=0.0,
                worst_case_loss_pct=0.0,
                probability_of_loss=0.0
            )

        weights = []
        expected_returns = []
        volatilities = []

        # Cash weight
        cash_weight = (state.cash + state.reserved_for_debt) / total_cap
        weights.append(cash_weight)
        expected_returns.append(0.03)
        volatilities.append(0.002)

        for a_id, amt in active_allocations:
            asset = assets_map[a_id]
            weights.append(amt / total_cap)
            expected_returns.append(asset.expected_return)
            volatilities.append(asset.volatility or (asset.risk * 0.35))

        w = np.array(weights)
        mu = np.array(expected_returns)
        sigma = np.array(volatilities)
        n_assets = len(weights)

        # Build correlation matrix (simplified Equicorrelation with positive cross-asset correlation)
        corr_matrix = np.full((n_assets, n_assets), 0.25)
        np.fill_diagonal(corr_matrix, 1.0)
        # Cash has 0 correlation with risky assets
        corr_matrix[0, :] = 0.0
        corr_matrix[:, 0] = 0.0
        corr_matrix[0, 0] = 1.0

        cov_matrix = np.outer(sigma, sigma) * corr_matrix

        # Generate Gaussian draws
        simulated_returns = rng.multivariate_normal(mu, cov_matrix, size=n_sims)
        portfolio_returns = simulated_returns @ w

        # Loss distribution = -portfolio_returns
        losses = -portfolio_returns

        var_95 = float(np.percentile(losses, 95))
        cvar_95 = float(np.mean(losses[losses >= var_95]))

        var_99 = float(np.percentile(losses, 99))
        cvar_99 = float(np.mean(losses[losses >= var_99]))

        prob_loss = float(np.mean(portfolio_returns < 0.0))
        worst_loss = float(np.max(losses))

        return MonteCarloSimulationReport(
            num_scenarios=n_sims,
            mean_simulated_return=float(np.mean(portfolio_returns)),
            std_simulated_return=float(np.std(portfolio_returns)),
            var_95=max(0.0, var_95),
            cvar_95=max(0.0, cvar_95),
            var_99=max(0.0, var_99),
            cvar_99=max(0.0, cvar_99),
            worst_case_loss_pct=max(0.0, worst_loss),
            probability_of_loss=prob_loss
        )
