"""Deterministic and explainable multi-factor risk scoring engine."""

from typing import Any, Dict, List
from pydantic import BaseModel, Field
from app.domain.asset import Asset
from app.domain.financial_state import FinancialState


class RiskFactorBreakdown(BaseModel):
    """Granular explainable breakdown of portfolio risk components."""
    weighted_asset_risk: float = Field(..., description="Capital-weighted intrinsic asset risk")
    concentration_index_hhi: float = Field(..., description="Herfindahl-Hirschman Index [0, 1]")
    concentration_penalty: float = Field(..., description="Penalty contribution from concentration")
    liquidity_deficit_penalty: float = Field(..., description="Penalty for falling below liquidity target")
    leverage_penalty: float = Field(..., description="Penalty from corporate debt obligations")
    composite_risk_score: float = Field(..., description="Final normalized risk index in [0, 1]")
    risk_tier: str = Field(..., description="Categorical rating: Conservative, Moderate, High, Aggressive")
    explanations: List[str] = Field(default_factory=list, description="Audit and explainability rationale")


class RiskEngine:
    """Deterministic Multi-Factor Portfolio Risk Analyzer."""

    def __init__(
        self,
        concentration_weight: float = 0.15,
        liquidity_penalty_weight: float = 0.20,
        leverage_weight: float = 0.10,
        min_liquidity_target: float = 0.20
    ):
        self.concentration_weight = concentration_weight
        self.liquidity_penalty_weight = liquidity_penalty_weight
        self.leverage_weight = leverage_weight
        self.min_liquidity_target = min_liquidity_target

    def analyze(self, state: FinancialState, assets_map: Dict[str, Asset]) -> RiskFactorBreakdown:
        """Perform multi-factor risk decomposition with full explainability."""
        explanations: List[str] = []
        total_cap = state.total_capital
        if total_cap <= 0:
            return RiskFactorBreakdown(
                weighted_asset_risk=0.0,
                concentration_index_hhi=0.0,
                concentration_penalty=0.0,
                liquidity_deficit_penalty=0.0,
                leverage_penalty=0.0,
                composite_risk_score=0.0,
                risk_tier="Conservative",
                explanations=["Zero capital balance."]
            )

        # 1. Base Asset Risk
        weighted_asset_risk = (state.cash + state.reserved_for_debt) * 0.01
        for asset_id, amount in state.allocations.items():
            if asset_id in assets_map and amount > 0:
                weighted_asset_risk += amount * assets_map[asset_id].risk
        base_risk = weighted_asset_risk / total_cap
        explanations.append(f"Base asset risk is {base_risk:.4f} across deployed capital.")

        # 2. Concentration (HHI)
        active_weights = [amt / total_cap for amt in state.allocations.values() if amt > 0]
        cash_weight = (state.cash + state.reserved_for_debt) / total_cap
        all_weights = active_weights + [cash_weight]
        hhi = sum(w ** 2 for w in all_weights)
        conc_penalty = self.concentration_weight * (hhi * 0.5)
        explanations.append(f"Concentration HHI is {hhi:.4f} contributing +{conc_penalty:.4f} to composite risk.")

        # 3. Liquidity Deficit Penalty
        curr_liq = state.calculate_liquidity(assets_map)
        liq_deficit = max(0.0, self.min_liquidity_target - curr_liq)
        liq_penalty = self.liquidity_penalty_weight * ((liq_deficit / max(self.min_liquidity_target, 0.01)) ** 2)
        if liq_deficit > 0:
            explanations.append(
                f"Liquidity shortfall of {liq_deficit*100:.1f}% incurs a penalty of +{liq_penalty:.4f}."
            )
        else:
            explanations.append(f"Liquidity {curr_liq*100:.1f}% satisfies the {self.min_liquidity_target*100:.1f}% floor.")

        # 4. Leverage / Debt Burden
        total_debt = sum(l.principal for l in state.liabilities)
        debt_ratio = min(1.0, total_debt / total_cap)
        debt_covered = min(1.0, state.reserved_for_debt / max(total_debt, 0.01))
        lev_penalty = self.leverage_weight * debt_ratio * (1.0 - debt_covered)
        if lev_penalty > 0:
            explanations.append(f"Uncovered debt burden incurs leverage penalty of +{lev_penalty:.4f}.")

        # Composite Score
        composite = 0.60 * base_risk + conc_penalty + liq_penalty + lev_penalty
        final_score = float(max(0.0, min(1.0, composite)))

        # Tier classification
        if final_score < 0.10:
            tier = "Ultra-Conservative"
        elif final_score < 0.25:
            tier = "Moderate"
        elif final_score < 0.40:
            tier = "High Growth / Moderate Risk"
        else:
            tier = "Aggressive / Elevated Risk"

        return RiskFactorBreakdown(
            weighted_asset_risk=base_risk,
            concentration_index_hhi=hhi,
            concentration_penalty=conc_penalty,
            liquidity_deficit_penalty=liq_penalty,
            leverage_penalty=lev_penalty,
            composite_risk_score=final_score,
            risk_tier=tier,
            explanations=explanations
        )
