"""Financial allocation problem definition and search problem abstraction."""

from __future__ import annotations
from typing import Any, Dict, List, Optional, Tuple
from pydantic import BaseModel, Field

from app.domain.asset import Asset, AssetType
from app.domain.liability import Liability
from app.domain.constraint import Constraint, ConstraintType, ConstraintSeverity, ConstraintEvaluationResult
from app.domain.strategy import FinancialAction, FinancialActionType
from app.domain.financial_state import FinancialState


class FinancialProblem(BaseModel):
    """Declarative specification of a corporate capital optimization problem.
    
    Attributes:
        capital: Total liquid balance sheet capital to allocate (e.g. ₹100 Cr).
        step_size: Discrete allocation step increment (e.g. ₹5 Cr).
        assets: Available investment options.
        liabilities: Active corporate obligations.
        constraints: Regulatory, risk, and policy constraints.
        risk_tolerance: Corporate risk appetite [0.0 = ultra-safe, 1.0 = aggressive].
        minimum_liquidity: Required portfolio liquidity ratio floor.
        objective: Primary optimization objective.
        market_state: Current macroeconomic regime tag.
    """
    capital: float = Field(..., gt=0.0, description="Total capital base")
    step_size: float = Field(default=5.0, gt=0.0, description="Allocation step quantum")
    assets: List[Asset] = Field(default_factory=list, description="Investment catalog")
    liabilities: List[Liability] = Field(default_factory=list, description="Obligations")
    constraints: List[Constraint] = Field(default_factory=list, description="Compliance rules")
    risk_tolerance: float = Field(default=0.50, ge=0.0, le=1.0, description="Risk tolerance")
    minimum_liquidity: float = Field(default=0.20, ge=0.0, le=1.0, description="Liquidity floor")
    objective: str = Field(default="maximize_risk_adjusted_return", description="Objective type")
    market_state: str = Field(default="normal", description="Market regime")


class FinancialAllocationProblem:
    """Formal Search Problem representation conforming to AI search abstraction.
    
    Provides standardized methods for:
    - initial_state
    - goal_test(state)
    - successors(state)
    - step_cost(state, action, next_state)
    - heuristic(state)
    - evaluate_constraints(state)
    """

    def __init__(self, problem: FinancialProblem):
        self.problem = problem
        self.capital = problem.capital
        self.step_size = problem.step_size
        self.assets_map: Dict[str, Asset] = {a.id: a for a in problem.assets}
        self.assets_list: List[Asset] = problem.assets
        self.liabilities_list: List[Liability] = problem.liabilities
        self.risk_tolerance = problem.risk_tolerance
        self.min_liquidity = problem.minimum_liquidity

        # Mandatory debt reserve calculation
        self.mandatory_debt_reserve = sum(
            l.principal for l in problem.liabilities if l.is_mandatory_reserve
        )

        # Build initial state
        self.initial_state = FinancialState(
            total_capital=self.capital,
            cash=self.capital,
            allocations={a.id: 0.0 for a in self.assets_list},
            liabilities=self.liabilities_list,
            reserved_for_debt=0.0,
            liquidity_ratio=1.0,
            risk_score=0.01,
            expected_return=0.03,  # Base cash return
            market_state=problem.market_state,
            history=[],
        )

    def evaluate_constraints(self, state: FinancialState) -> List[ConstraintEvaluationResult]:
        """Evaluate state against all active constraints and produce explainable audit reports."""
        results: List[ConstraintEvaluationResult] = []

        # 1. Physical Capital Budget Constraint
        total_allocated = sum(state.allocations.values()) + state.cash + state.reserved_for_debt
        budget_satisfied = abs(total_allocated - self.capital) <= 1e-4 and state.cash >= -1e-4
        budget_penalty = 0.0 if budget_satisfied else 100.0 * abs(total_allocated - self.capital)
        results.append(
            ConstraintEvaluationResult(
                constraint_id="c_capital_budget",
                constraint_type=ConstraintType.CAPITAL_BUDGET,
                satisfied=budget_satisfied,
                actual=total_allocated,
                required=self.capital,
                severity=ConstraintSeverity.CRITICAL,
                message=f"Total balance sheet sum ₹{total_allocated:.2f} Cr matches budget ₹{self.capital:.2f} Cr"
                if budget_satisfied else f"Capital budget violation: allocated ₹{total_allocated:.2f} Cr vs budget ₹{self.capital:.2f} Cr",
                penalty=budget_penalty
            )
        )

        # 2. Minimum Liquidity Constraint
        curr_liq = state.calculate_liquidity(self.assets_map)
        liq_req = self.min_liquidity
        for c in self.problem.constraints:
            if c.constraint_type == ConstraintType.MINIMUM_LIQUIDITY:
                liq_req = float(c.parameters.get("threshold", self.min_liquidity))
        
        liq_satisfied = curr_liq >= (liq_req - 1e-4)
        liq_deficit = max(0.0, liq_req - curr_liq)
        results.append(
            ConstraintEvaluationResult(
                constraint_id="c_min_liquidity",
                constraint_type=ConstraintType.MINIMUM_LIQUIDITY,
                satisfied=liq_satisfied,
                actual=curr_liq,
                required=liq_req,
                severity=ConstraintSeverity.CRITICAL,
                message=f"Liquidity ratio {curr_liq*100:.1f}% meets required floor {liq_req*100:.1f}%"
                if liq_satisfied else f"Liquidity ratio {curr_liq*100:.1f}% is below required {liq_req*100:.1f}%",
                penalty=liq_deficit * 50.0
            )
        )

        # 3. Mandatory Debt Reserve Constraint
        debt_req = self.mandatory_debt_reserve
        for c in self.problem.constraints:
            if c.constraint_type == ConstraintType.DEBT_RESERVE:
                debt_req = float(c.parameters.get("amount", self.mandatory_debt_reserve))

        debt_satisfied = state.reserved_for_debt >= (debt_req - 1e-4)
        debt_deficit = max(0.0, debt_req - state.reserved_for_debt)
        results.append(
            ConstraintEvaluationResult(
                constraint_id="c_debt_reserve",
                constraint_type=ConstraintType.DEBT_RESERVE,
                satisfied=debt_satisfied,
                actual=state.reserved_for_debt,
                required=debt_req,
                severity=ConstraintSeverity.CRITICAL,
                message=f"Debt reserve ₹{state.reserved_for_debt:.2f} Cr meets requirement ₹{debt_req:.2f} Cr"
                if debt_satisfied else f"Debt reserve ₹{state.reserved_for_debt:.2f} Cr is below required ₹{debt_req:.2f} Cr",
                penalty=debt_deficit * 20.0
            )
        )

        # 4. User-Configured Constraints (Max Risk, Asset Limits, Equity Caps)
        for c in self.problem.constraints:
            if c.constraint_type == ConstraintType.MAXIMUM_RISK:
                max_r = float(c.parameters.get("threshold", 0.30))
                curr_risk = state.calculate_risk(self.assets_map)
                sat = curr_risk <= (max_r + 1e-4)
                results.append(
                    ConstraintEvaluationResult(
                        constraint_id=c.id,
                        constraint_type=ConstraintType.MAXIMUM_RISK,
                        satisfied=sat,
                        actual=curr_risk,
                        required=max_r,
                        severity=c.severity,
                        message=f"Portfolio risk {curr_risk:.4f} is within limit {max_r:.4f}"
                        if sat else f"Portfolio risk {curr_risk:.4f} exceeds ceiling {max_r:.4f}",
                        penalty=max(0.0, curr_risk - max_r) * c.penalty_weight
                    )
                )

            elif c.constraint_type == ConstraintType.MAXIMUM_ASSET_EXPOSURE:
                target_asset_id = str(c.parameters.get("asset_id", ""))
                max_frac = float(c.parameters.get("max_fraction", 1.0))
                max_amt = max_frac * self.capital
                curr_amt = state.allocations.get(target_asset_id, 0.0)
                sat = curr_amt <= (max_amt + 1e-4)
                results.append(
                    ConstraintEvaluationResult(
                        constraint_id=c.id,
                        constraint_type=ConstraintType.MAXIMUM_ASSET_EXPOSURE,
                        satisfied=sat,
                        actual=curr_amt / self.capital if self.capital > 0 else 0.0,
                        required=max_frac,
                        severity=c.severity,
                        message=f"Asset '{target_asset_id}' exposure ₹{curr_amt:.2f} Cr is within max ₹{max_amt:.2f} Cr ({max_frac*100:.1f}%)"
                        if sat else f"Asset '{target_asset_id}' exposure ₹{curr_amt:.2f} Cr exceeds max ₹{max_amt:.2f} Cr ({max_frac*100:.1f}%)",
                        penalty=max(0.0, curr_amt - max_amt) * c.penalty_weight
                    )
                )

            elif c.constraint_type == ConstraintType.MAXIMUM_ASSET_TYPE_EXPOSURE:
                target_type = str(c.parameters.get("asset_type", "equity")).lower()
                max_frac = float(c.parameters.get("max_fraction", 0.30))
                max_amt = max_frac * self.capital
                
                type_total = sum(
                    amt for a_id, amt in state.allocations.items()
                    if a_id in self.assets_map and self.assets_map[a_id].asset_type.value.lower() == target_type
                )
                sat = type_total <= (max_amt + 1e-4)
                results.append(
                    ConstraintEvaluationResult(
                        constraint_id=c.id,
                        constraint_type=ConstraintType.MAXIMUM_ASSET_TYPE_EXPOSURE,
                        satisfied=sat,
                        actual=type_total / self.capital if self.capital > 0 else 0.0,
                        required=max_frac,
                        severity=c.severity,
                        message=f"Asset class '{target_type}' allocation ₹{type_total:.2f} Cr is within cap {max_frac*100:.1f}% (₹{max_amt:.2f} Cr)"
                        if sat else f"Asset class '{target_type}' allocation ₹{type_total:.2f} Cr exceeds cap {max_frac*100:.1f}% (₹{max_amt:.2f} Cr)",
                        penalty=max(0.0, type_total - max_amt) * c.penalty_weight
                    )
                )

        return results

    def is_state_compliant(self, state: FinancialState) -> bool:
        """Check if all critical hard constraints are strictly satisfied."""
        evaluations = self.evaluate_constraints(state)
        return all(e.satisfied for e in evaluations if e.severity == ConstraintSeverity.CRITICAL)

    def goal_test(self, state: FinancialState) -> bool:
        """Goal test: Capital is fully allocated (cash below step_size) and state is compliant."""
        # Goal state reached when free cash cannot fund any more discrete increments
        is_fully_deployed = state.cash < (self.step_size - 1e-4)
        return is_fully_deployed and self.is_state_compliant(state)

    def successors(self, state: FinancialState) -> List[Tuple[FinancialAction, FinancialState]]:
        """Generate valid next states reachable by discrete financial actions."""
        succs: List[Tuple[FinancialAction, FinancialState]] = []

        if state.cash < (self.step_size - 1e-4):
            # Terminal state reached in terms of allocation
            return succs

        # 1. Action: Reserve capital for mandatory liabilities if deficit exists
        if state.reserved_for_debt < self.mandatory_debt_reserve:
            needed = self.mandatory_debt_reserve - state.reserved_for_debt
            reserve_step = min(needed, min(self.step_size, state.cash))
            act = FinancialAction(
                action_type=FinancialActionType.RESERVE_CAPITAL,
                amount=reserve_step,
                reason=f"Earmark ₹{reserve_step:.2f} Cr for mandatory debt obligations"
            )
            succs.append((act, state.apply_action(act, self.assets_map)))

        # 2. Action: Invest discrete quantum into each eligible asset
        for asset in self.assets_list:
            current_amt = state.allocations.get(asset.id, 0.0)
            if asset.max_investment is not None and (current_amt + self.step_size) > asset.max_investment:
                continue

            # Check individual asset exposure limits
            exceeds_cap = False
            for c in self.problem.constraints:
                if c.constraint_type == ConstraintType.MAXIMUM_ASSET_EXPOSURE:
                    if c.parameters.get("asset_id") == asset.id:
                        cap = float(c.parameters.get("max_fraction", 1.0)) * self.capital
                        if (current_amt + self.step_size) > (cap + 1e-4):
                            exceeds_cap = True
                            break
                elif c.constraint_type == ConstraintType.MAXIMUM_ASSET_TYPE_EXPOSURE:
                    target_type = str(c.parameters.get("asset_type", "")).lower()
                    if asset.asset_type.value.lower() == target_type:
                        cap = float(c.parameters.get("max_fraction", 1.0)) * self.capital
                        curr_type_total = sum(
                            amt for a_id, amt in state.allocations.items()
                            if a_id in self.assets_map and self.assets_map[a_id].asset_type.value.lower() == target_type
                        )
                        if (curr_type_total + self.step_size) > (cap + 1e-4):
                            exceeds_cap = True
                            break
            if exceeds_cap:
                continue

            act = FinancialAction(
                action_type=FinancialActionType.INVEST,
                asset_id=asset.id,
                amount=self.step_size,
                cost=self.step_size * asset.cost,
                reason=f"Allocate ₹{self.step_size:.2f} Cr to {asset.name} (Exp Return: {asset.expected_return*100:.1f}%)"
            )
            next_state = state.apply_action(act, self.assets_map)
            succs.append((act, next_state))

        # 3. Action: Hold remaining cash
        act_hold = FinancialAction(
            action_type=FinancialActionType.HOLD_CASH,
            amount=state.cash,
            reason="Retain unallocated liquid cash in treasury"
        )
        # Applying HOLD_CASH finishes deployment by treating remaining cash as finalized
        held_state = state.clone()
        held_state.history.append(act_hold)
        held_state.expected_return = held_state.calculate_expected_return(self.assets_map)
        held_state.liquidity_ratio = held_state.calculate_liquidity(self.assets_map)
        held_state.risk_score = held_state.calculate_risk(self.assets_map)
        succs.append((act_hold, held_state))

        return succs

    def step_cost(self, state: FinancialState, action: FinancialAction, next_state: FinancialState) -> float:
        """Compute the non-negative transition cost for A* search.
        
        Cost formulation:
        Cost is inversely related to marginal risk-adjusted return contribution,
        plus transaction costs and any constraint violation penalties.
        
        To guarantee non-negative step costs for shortest-path search:
            step_cost = baseline_offset - (next_utility - current_utility) + action_cost + penalty
        """
        curr_util = state.utility_score(self.risk_tolerance)
        next_util = next_state.utility_score(self.risk_tolerance)
        util_gain = next_util - curr_util

        # Base non-negative cost increment (offset by max theoretical gain)
        # Max theoretical return per step is ~15%, so offset = 0.20
        base_cost = 0.20 - util_gain + (action.cost / max(1.0, self.capital))
        
        # Soft constraint penalties
        evals = self.evaluate_constraints(next_state)
        penalty = sum(e.penalty for e in evals if not e.satisfied)

        return max(0.001, base_cost + penalty * 0.1)

    def heuristic(self, state: FinancialState) -> float:
        """Admissible and consistent heuristic function h(n) for A* and Best-First search.
        
        Estimates the remaining minimum cost (maximum remaining risk-adjusted value)
        achievable with the unallocated cash balance C_rem.
        
        Let r_max = max(asset.expected_return for asset in assets)
        Let min_risk = min(asset.risk for asset in assets)
        Optimal future potential return = (C_rem / Total_Capital) * (r_max - risk_penalty)
        
        Heuristic cost-to-go:
            h(n) = remaining_steps * min_achievable_cost_per_step
        """
        if state.cash <= 1e-4:
            return 0.0

        best_asset_return = max((a.expected_return for a in self.assets_list), default=0.03)
        remaining_cash_ratio = state.cash / self.capital
        
        # Upper bound on future utility gain
        max_future_gain = remaining_cash_ratio * (best_asset_return * 1.2)
        
        # Lower bound on remaining path cost to goal
        h_val = max(0.0, (state.cash / self.step_size) * 0.01 - max_future_gain * 0.05)
        return float(h_val)
