"""MDP State and Action representations for multi-period capital management."""

from enum import Enum
from typing import NamedTuple, Tuple


class MarketRegime(str, Enum):
    """Macroeconomic regimes in MDP transitions."""
    BULL = "bull"
    NORMAL = "normal"
    BEAR = "bear"
    VOLATILE = "volatile"


class PortfolioPosture(str, Enum):
    """Discretized allocation posture."""
    DEFENSIVE = "defensive"    # High cash & gov bonds, min equity
    BALANCED = "balanced"      # Mix of bonds & equities
    AGGRESSIVE = "aggressive"  # Max equity & corporate credit


class MDPState(NamedTuple):
    """Discretized state representation (posture, market_regime, liquidity_status)."""
    posture: PortfolioPosture
    market_regime: MarketRegime
    is_liquidity_sufficient: bool


class MDPAction(str, Enum):
    """Discrete rebalancing decisions in multi-period MDP."""
    MAINTAIN_CURRENT = "maintain_current"
    SHIFT_DEFENSIVE = "shift_defensive"
    SHIFT_BALANCED = "shift_balanced"
    SHIFT_AGGRESSIVE = "shift_aggressive"
    INJECT_LIQUIDITY = "inject_liquidity"
