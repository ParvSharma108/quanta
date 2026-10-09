"""Action and Strategy models for capital allocation transitions."""

from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


class FinancialActionType(str, Enum):
    """Types of actions available to the treasury agent / search engine."""
    HOLD_CASH = "HOLD_CASH"
    INVEST = "INVEST"
    REPAY_DEBT = "REPAY_DEBT"
    REBALANCE = "REBALANCE"
    RESERVE_CAPITAL = "RESERVE_CAPITAL"


class FinancialAction(BaseModel):
    """Discrete operational decision executed on the treasury state.
    
    Attributes:
        action_type: Categorical action.
        asset_id: Target asset identifier (if INVEST or REBALANCE).
        liability_id: Target liability identifier (if REPAY_DEBT or RESERVE_CAPITAL).
        amount: Capital quantity involved in the action.
        cost: Frictional execution / brokerage cost.
        reason: Algorithmic or heuristic rationale for the action.
    """
    action_type: FinancialActionType = Field(..., description="Action classification")
    asset_id: Optional[str] = Field(default=None, description="Target asset identifier")
    liability_id: Optional[str] = Field(default=None, description="Target liability identifier")
    amount: float = Field(..., ge=0.0, description="Capital allocation quantum")
    cost: float = Field(default=0.0, ge=0.0, description="Transaction friction")
    reason: str = Field(default="", description="Explanatory text for audit trail")

    def __repr__(self) -> str:
        target = self.asset_id or self.liability_id or "treasury"
        return f"<Action: {self.action_type.value} ₹{self.amount:.2f} -> {target}>"


class Strategy(BaseModel):
    """Synthesized capital allocation strategy containing actions and outcomes.
    
    Attributes:
        actions: Ordered list of discrete actions.
        total_allocated: Total capital actively deployed.
        expected_return: Annualized expected return fraction of the resulting portfolio.
        risk_score: Normalized portfolio risk score [0, 1].
        liquidity_ratio: Overall liquidity ratio [0, 1].
        objective_value: Evaluated utility / objective function score.
        is_compliant: True if all hard constraints are satisfied.
        explanation: Human-understandable summary of the strategy rationale.
        metadata: Diagnostic and algorithmic audit information.
    """
    actions: List[FinancialAction] = Field(default_factory=list, description="Sequence of actions")
    total_allocated: float = Field(default=0.0, ge=0.0, description="Total deployed capital")
    expected_return: float = Field(default=0.0, description="Portfolio expected return")
    risk_score: float = Field(default=0.0, description="Portfolio risk score")
    liquidity_ratio: float = Field(default=1.0, description="Portfolio liquidity score")
    objective_value: float = Field(default=0.0, description="Utility or optimization score")
    is_compliant: bool = Field(default=True, description="Constraint compliance flag")
    explanation: str = Field(default="", description="Explainable recommendation text")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Audit and diagnostic metadata")
