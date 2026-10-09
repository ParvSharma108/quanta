"""Formal state-space representation for corporate financial treasury."""

from __future__ import annotations
import copy
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, Field

from app.domain.asset import Asset
from app.domain.liability import Liability
from app.domain.strategy import FinancialAction, FinancialActionType


class FinancialState(BaseModel):
    """Immutable/safely cloneable financial state of corporate treasury.
    
    Attributes:
        total_capital: Initial or total balance sheet capital.
        cash: Current unallocated cash balance.
        allocations: Map of asset_id -> allocated capital amount.
        liabilities: List of liabilities active on the balance sheet.
        reserved_for_debt: Liquid cash earmarked specifically for liability service.
        liquidity_ratio: Current portfolio weighted liquidity index [0.0, 1.0].
        risk_score: Current portfolio weighted risk index [0.0, 1.0].
        expected_return: Current portfolio weighted annual return fraction.
        market_state: Current macroeconomic state tag ('normal', 'bull', 'bear', etc.).
        history: Chronological list of actions executed to reach this state.
    """
    total_capital: float = Field(..., gt=0.0, description="Total treasury capital base")
    cash: float = Field(..., ge=0.0, description="Unallocated liquid cash")
    allocations: Dict[str, float] = Field(default_factory=dict, description="Asset allocations")
    liabilities: List[Liability] = Field(default_factory=list, description="Corporate liabilities")
    reserved_for_debt: float = Field(default=0.0, ge=0.0, description="Earmarked debt reserve")
    liquidity_ratio: float = Field(default=1.0, ge=0.0, le=1.0, description="Weighted liquidity")
    risk_score: float = Field(default=0.0, ge=0.0, le=1.0, description="Composite risk score")
    expected_return: float = Field(default=0.0, description="Weighted annual expected return")
    market_state: str = Field(default="normal", description="Market regime identifier")
    history: List[FinancialAction] = Field(default_factory=list, description="Action path trace")

    def clone(self) -> FinancialState:
        """Create an independent deep copy of the financial state."""
        return FinancialState(
            total_capital=self.total_capital,
            cash=self.cash,
            allocations=dict(self.allocations),
            liabilities=[copy.deepcopy(l) for l in self.liabilities],
            reserved_for_debt=self.reserved_for_debt,
            liquidity_ratio=self.liquidity_ratio,
            risk_score=self.risk_score,
            expected_return=self.expected_return,
            market_state=self.market_state,
            history=list(self.history),
        )

    def is_valid(self, tolerance: float = 1e-5) -> bool:
        """Check if physical balance sheet conservation holds."""
        if self.cash < -tolerance:
            return False
        total_allocated = sum(self.allocations.values()) + self.cash + self.reserved_for_debt
        if abs(total_allocated - self.total_capital) > (self.total_capital * tolerance + 0.01):
            return False
        for amt in self.allocations.values():
            if amt < -tolerance:
                return False
        return True

    def calculate_expected_return(self, assets_map: Dict[str, Asset], cash_return: float = 0.03) -> float:
        """Compute capital-weighted nominal expected return across portfolio."""
        if self.total_capital <= 0:
            return 0.0
        
        weighted_sum = (self.cash + self.reserved_for_debt) * cash_return
        for asset_id, amount in self.allocations.items():
            if asset_id in assets_map and amount > 0:
                asset = assets_map[asset_id]
                net_return = asset.expected_return - asset.cost
                weighted_sum += amount * net_return
        
        return weighted_sum / self.total_capital

    def calculate_liquidity(self, assets_map: Dict[str, Asset]) -> float:
        """Compute capital-weighted liquidity score in [0.0, 1.0]."""
        if self.total_capital <= 0:
            return 1.0
        
        # Free cash has 1.0 liquidity factor; debt reserve has 1.0 liquidity factor
        weighted_liq = (self.cash + self.reserved_for_debt) * 1.0
        for asset_id, amount in self.allocations.items():
            if asset_id in assets_map and amount > 0:
                weighted_liq += amount * assets_map[asset_id].liquidity
        
        ratio = weighted_liq / self.total_capital
        return max(0.0, min(1.0, ratio))

    def calculate_risk(
        self,
        assets_map: Dict[str, Asset],
        concentration_weight: float = 0.15,
        liquidity_penalty_weight: float = 0.20,
        min_liquidity_target: float = 0.20
    ) -> float:
        """Compute comprehensive, explainable risk score in [0.0, 1.0].
        
        Components:
        1. Weighted Asset Risk: Capital-weighted intrinsic risk of held assets.
        2. Concentration Penalty: Herfindahl-Hirschman Index (HHI) of active allocations.
        3. Liquidity Deficit Penalty: Quadratic penalty if liquidity falls below target.
        4. Leverage / Debt Burden: Mandatory debt reserve ratio.
        """
        if self.total_capital <= 0:
            return 0.0
        
        # 1. Base asset risk (cash risk = 0.01)
        weighted_asset_risk = (self.cash + self.reserved_for_debt) * 0.01
        for asset_id, amount in self.allocations.items():
            if asset_id in assets_map and amount > 0:
                weighted_asset_risk += amount * assets_map[asset_id].risk
        base_risk = weighted_asset_risk / self.total_capital

        # 2. Concentration index (HHI across asset buckets)
        active_weights = [amount / self.total_capital for amount in self.allocations.values() if amount > 0]
        cash_weight = (self.cash + self.reserved_for_debt) / self.total_capital
        all_weights = active_weights + [cash_weight]
        hhi = sum(w ** 2 for w in all_weights)  # Ranges from ~1/N to 1.0

        # 3. Liquidity deficit
        curr_liq = self.calculate_liquidity(assets_map)
        liq_deficit = max(0.0, min_liquidity_target - curr_liq)
        liq_penalty = (liq_deficit / max(min_liquidity_target, 0.01)) ** 2

        # 4. Composite aggregation
        composite = (
            0.65 * base_risk +
            concentration_weight * (hhi * 0.5) +
            liquidity_penalty_weight * liq_penalty
        )
        return float(max(0.0, min(1.0, composite)))

    def utility_score(
        self,
        risk_tolerance: float = 0.50,
        liquidity_weight: float = 0.25,
        risk_aversion_factor: float = 1.5
    ) -> float:
        """Compute the risk-adjusted economic utility of the state.
        
        Formula:
            Utility = Expected_Return 
                    - (1.0 - Risk_Tolerance) * Risk_Aversion * (Risk_Score ^ 2)
                    + Liquidity_Weight * Liquidity_Ratio
        """
        risk_penalty = (1.0 - risk_tolerance) * risk_aversion_factor * (self.risk_score ** 2)
        liq_benefit = liquidity_weight * self.liquidity_ratio
        return self.expected_return - risk_penalty + liq_benefit

    def apply_action(self, action: FinancialAction, assets_map: Optional[Dict[str, Asset]] = None) -> FinancialState:
        """Apply a discrete financial action and return a new cloned state."""
        new_state = self.clone()
        new_state.history.append(action)

        if action.action_type == FinancialActionType.HOLD_CASH:
            # Cash remains unchanged, action acknowledged
            pass

        elif action.action_type == FinancialActionType.RESERVE_CAPITAL:
            amt = min(action.amount, new_state.cash)
            new_state.cash -= amt
            new_state.reserved_for_debt += amt

        elif action.action_type == FinancialActionType.INVEST:
            if not action.asset_id:
                raise ValueError("INVEST action requires asset_id")
            amt = min(action.amount, new_state.cash)
            new_state.cash -= amt
            current_alloc = new_state.allocations.get(action.asset_id, 0.0)
            new_state.allocations[action.asset_id] = round(current_alloc + amt, 6)

        elif action.action_type == FinancialActionType.REPAY_DEBT:
            amt = min(action.amount, new_state.cash + new_state.reserved_for_debt)
            # Draw from debt reserve first, then cash
            from_reserve = min(amt, new_state.reserved_for_debt)
            from_cash = amt - from_reserve
            new_state.reserved_for_debt -= from_reserve
            new_state.cash -= from_cash

        elif action.action_type == FinancialActionType.REBALANCE:
            if not action.asset_id:
                raise ValueError("REBALANCE action requires asset_id")
            # Positive amount = buy, negative = sell
            if action.amount >= 0:
                amt = min(action.amount, new_state.cash)
                new_state.cash -= amt
                new_state.allocations[action.asset_id] = round(new_state.allocations.get(action.asset_id, 0.0) + amt, 6)
            else:
                sell_amt = min(abs(action.amount), new_state.allocations.get(action.asset_id, 0.0))
                new_state.allocations[action.asset_id] = round(new_state.allocations[action.asset_id] - sell_amt, 6)
                new_state.cash += sell_amt

        # Update analytical metrics if asset catalog provided
        if assets_map is not None:
            new_state.expected_return = new_state.calculate_expected_return(assets_map)
            new_state.liquidity_ratio = new_state.calculate_liquidity(assets_map)
            new_state.risk_score = new_state.calculate_risk(assets_map)

        return new_state

    def state_signature(self, round_digits: int = 2) -> Tuple[Any, ...]:
        """Produce a hashable discrete signature for graph search closed sets."""
        alloc_tuple = tuple(sorted((k, round(v, round_digits)) for k, v in self.allocations.items() if v > 0))
        return (
            round(self.cash, round_digits),
            round(self.reserved_for_debt, round_digits),
            alloc_tuple
        )
