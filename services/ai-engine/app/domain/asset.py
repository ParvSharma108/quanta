"""Domain model representing investment assets and capital vehicles."""

from enum import Enum
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field, field_validator


class AssetType(str, Enum):
    """Categorical classification of financial assets."""
    CASH = "cash"
    GOV_BOND = "gov_bond"
    CORP_BOND = "corp_bond"
    EQUITY = "equity"
    REAL_ESTATE = "real_estate"
    COMMODITY = "commodity"
    OTHER = "other"


class Asset(BaseModel):
    """Financial asset or investment vehicle eligible for capital allocation.
    
    Attributes:
        id: Unique identifier for the asset.
        name: Descriptive display name.
        asset_type: Classification (CASH, GOV_BOND, CORP_BOND, EQUITY, etc.).
        cost: Transaction or management cost fraction (e.g. 0.001 for 10 bps).
        expected_return: Annualized expected nominal return fraction (e.g. 0.07 for 7%).
        risk: Normalized risk score in [0.0, 1.0].
        liquidity: Normalized liquidity score in [0.0, 1.0] (1.0 = immediate cash equivalent).
        volatility: Annualized return volatility standard deviation.
        min_investment: Minimum discrete capital allocation allowed.
        max_investment: Maximum discrete capital allocation allowed.
        metadata: Domain-specific annotations or tags.
    """
    id: str = Field(..., description="Unique asset identifier")
    name: str = Field(..., description="Asset display name")
    asset_type: AssetType = Field(default=AssetType.OTHER, description="Asset class")
    cost: float = Field(default=0.0, ge=0.0, description="Acquisition / transaction friction")
    expected_return: float = Field(..., ge=-1.0, le=5.0, description="Expected annual return fraction")
    risk: float = Field(..., ge=0.0, le=1.0, description="Normalized risk index in [0, 1]")
    liquidity: float = Field(..., ge=0.0, le=1.0, description="Normalized liquidity factor in [0, 1]")
    volatility: float = Field(default=0.05, ge=0.0, description="Annualized volatility")
    min_investment: float = Field(default=0.0, ge=0.0, description="Minimum capital allocation")
    max_investment: Optional[float] = Field(default=None, ge=0.0, description="Optional maximum allocation limit")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Arbitrary financial metadata")

    @field_validator("name")
    @classmethod
    def validate_name_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Asset name cannot be empty")
        return v
