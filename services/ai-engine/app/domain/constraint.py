"""Constraint models for portfolio and treasury regulatory compliance."""

from enum import Enum
from typing import Any, Dict, Optional
from pydantic import BaseModel, Field


class ConstraintType(str, Enum):
    """Categorical types of financial constraints."""
    MINIMUM_LIQUIDITY = "minimum_liquidity"
    MAXIMUM_RISK = "maximum_risk"
    MAXIMUM_ASSET_EXPOSURE = "maximum_asset_exposure"
    MAXIMUM_ASSET_TYPE_EXPOSURE = "maximum_asset_type_exposure"
    CAPITAL_BUDGET = "capital_budget"
    DEBT_RESERVE = "debt_reserve"
    MINIMUM_EXPECTED_RETURN = "minimum_expected_return"
    CUSTOM = "custom"


class ConstraintSeverity(str, Enum):
    """Severity classification for constraint evaluation."""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


class ConstraintEvaluationResult(BaseModel):
    """Structured evaluation report for an individual constraint.
    
    Attributes:
        constraint_id: Identifier of the evaluated constraint.
        constraint_type: Type of constraint.
        satisfied: Boolean flag indicating if state satisfies the constraint.
        actual: Computed value from the current financial state.
        required: Threshold or target value required by policy.
        severity: Impact level if violated.
        message: Human-readable explainability string detailing compliance.
        penalty: Numerical penalty value used by heuristic / search scoring.
    """
    constraint_id: str
    constraint_type: ConstraintType
    satisfied: bool
    actual: float
    required: float
    severity: ConstraintSeverity = ConstraintSeverity.CRITICAL
    message: str
    penalty: float = 0.0


class Constraint(BaseModel):
    """Declarative specification of a treasury or portfolio constraint.
    
    Attributes:
        id: Unique constraint identifier.
        constraint_type: Category of constraint.
        description: Readable description of the policy rule.
        parameters: Configuration dictionary (e.g. {'threshold': 0.20, 'asset_id': 'equity'}).
        severity: Severity if violated (default CRITICAL).
        penalty_weight: Multiplier for soft-constraint penalty calculation.
    """
    id: str = Field(..., description="Unique constraint identifier")
    constraint_type: ConstraintType = Field(..., description="Type of constraint")
    description: str = Field(default="", description="Human-readable policy rationale")
    parameters: Dict[str, Any] = Field(default_factory=dict, description="Thresholds and targets")
    severity: ConstraintSeverity = Field(default=ConstraintSeverity.CRITICAL, description="Violation severity")
    penalty_weight: float = Field(default=10.0, ge=0.0, description="Penalty coefficient for search scoring")
