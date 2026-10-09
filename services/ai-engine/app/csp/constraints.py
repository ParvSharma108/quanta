"""Financial domain constraints for CSP solver."""

from typing import Any, Dict, List
from app.csp.model import CSPConstraint


class ExactSumConstraint(CSPConstraint):
    """Enforces that all assigned variables sum exactly to total_capital (or <= when partial)."""

    def __init__(self, variables: List[str], total_sum: float, tolerance: float = 1e-4):
        super().__init__(variables, name="ExactSumConstraint")
        self.total_sum = total_sum
        self.tolerance = tolerance

    def is_satisfied(self, assignment: Dict[str, Any]) -> bool:
        current_sum = sum(assignment[v] for v in self.variables if v in assignment)
        
        # If all variables assigned, must equal total_sum exactly
        if all(v in assignment for v in self.variables):
            return abs(current_sum - self.total_sum) <= self.tolerance
        
        # If partially assigned, cannot exceed total_sum
        return current_sum <= (self.total_sum + self.tolerance)


class DebtReserveCSPConstraint(CSPConstraint):
    """Enforces minimum mandatory debt reserve."""

    def __init__(self, reserve_var: str, min_required: float):
        super().__init__([reserve_var], name="DebtReserveCSPConstraint")
        self.reserve_var = reserve_var
        self.min_required = min_required

    def is_satisfied(self, assignment: Dict[str, Any]) -> bool:
        if self.reserve_var in assignment:
            return assignment[self.reserve_var] >= (self.min_required - 1e-4)
        return True


class MinimumLiquidityCSPConstraint(CSPConstraint):
    """Enforces minimum weighted portfolio liquidity."""

    def __init__(
        self,
        variables: List[str],
        liquidity_weights: Dict[str, float],
        total_capital: float,
        min_liquidity: float
    ):
        super().__init__(variables, name="MinimumLiquidityCSPConstraint")
        self.liquidity_weights = liquidity_weights
        self.total_capital = total_capital
        self.min_liquidity = min_liquidity

    def is_satisfied(self, assignment: Dict[str, Any]) -> bool:
        # If all assigned, check full weighted liquidity
        if all(v in assignment for v in self.variables):
            weighted_liq = sum(
                assignment[v] * self.liquidity_weights.get(v, 1.0)
                for v in self.variables
            )
            ratio = weighted_liq / self.total_capital
            return ratio >= (self.min_liquidity - 1e-4)
        
        # Partial: Upper bound check (assume unassigned vars have 1.0 liquidity)
        assigned_sum = sum(assignment[v] for v in self.variables if v in assignment)
        unassigned_sum = max(0.0, self.total_capital - assigned_sum)
        max_possible_liq = sum(
            assignment[v] * self.liquidity_weights.get(v, 1.0)
            for v in self.variables if v in assignment
        ) + unassigned_sum * 1.0
        
        return (max_possible_liq / self.total_capital) >= (self.min_liquidity - 1e-4)


class MaximumRiskCSPConstraint(CSPConstraint):
    """Enforces maximum weighted portfolio risk."""

    def __init__(
        self,
        variables: List[str],
        risk_weights: Dict[str, float],
        total_capital: float,
        max_risk: float
    ):
        super().__init__(variables, name="MaximumRiskCSPConstraint")
        self.risk_weights = risk_weights
        self.total_capital = total_capital
        self.max_risk = max_risk

    def is_satisfied(self, assignment: Dict[str, Any]) -> bool:
        assigned_risk = sum(
            assignment[v] * self.risk_weights.get(v, 0.01)
            for v in self.variables if v in assignment
        )
        # Cannot already exceed max allowable risk on assigned portion
        if (assigned_risk / self.total_capital) > (self.max_risk + 1e-4):
            return False
        
        if all(v in assignment for v in self.variables):
            return (assigned_risk / self.total_capital) <= (self.max_risk + 1e-4)
        return True


class MaxAssetTypeCSPConstraint(CSPConstraint):
    """Enforces cap on grouped asset classes (e.g. max equity)."""

    def __init__(self, type_variables: List[str], max_amount: float):
        super().__init__(type_variables, name="MaxAssetTypeCSPConstraint")
        self.type_variables = type_variables
        self.max_amount = max_amount

    def is_satisfied(self, assignment: Dict[str, Any]) -> bool:
        curr_sum = sum(assignment[v] for v in self.type_variables if v in assignment)
        return curr_sum <= (self.max_amount + 1e-4)
