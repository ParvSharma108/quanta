"""TreasuryAgent focusing on yield optimization and capital deployment."""

from typing import List
from app.agents.base import IntelligentAgent, AgentRole, AgentAssessment, ActionProposal
from app.domain.financial_state import FinancialState
from app.domain.strategy import FinancialAction, FinancialActionType
from app.domain.financial_problem import FinancialAllocationProblem


class TreasuryAgent(IntelligentAgent):
    """Specialist agent seeking to maximize capital productivity and returns."""

    def __init__(self):
        super().__init__(name="Chief Treasury Agent", role=AgentRole.TREASURY)

    def perceive_and_assess(
        self, state: FinancialState, problem: FinancialAllocationProblem
    ) -> AgentAssessment:
        findings: List[str] = []
        proposals: List[ActionProposal] = []

        unallocated_cash = state.cash
        findings.append(f"Unallocated treasury cash balance: ₹{unallocated_cash:.2f} Cr.")

        if unallocated_cash >= problem.step_size:
            # Sort assets by net yield (expected_return - cost)
            sorted_assets = sorted(
                problem.assets_list,
                key=lambda a: (a.expected_return - a.cost),
                reverse=True
            )
            findings.append(f"Highest yielding asset: {sorted_assets[0].name} ({sorted_assets[0].expected_return*100:.1f}%).")

            for asset in sorted_assets:
                curr_amt = state.allocations.get(asset.id, 0.0)
                if asset.max_investment is not None and (curr_amt + problem.step_size) > asset.max_investment:
                    continue

                act = FinancialAction(
                    action_type=FinancialActionType.INVEST,
                    asset_id=asset.id,
                    amount=problem.step_size,
                    cost=problem.step_size * asset.cost,
                    reason=f"Deploy capital to maximize yield via {asset.name}"
                )
                conf = max(0.2, min(0.95, asset.expected_return / 0.15))
                proposals.append(
                    ActionProposal(
                        proposed_by=self.role,
                        action=act,
                        confidence=conf,
                        expected_utility_delta=asset.expected_return * (problem.step_size / problem.capital),
                        rationale=f"Deploy ₹{problem.step_size:.2f} Cr to {asset.name} yielding {asset.expected_return*100:.1f}%"
                    )
                )

        score = state.expected_return / 0.15  # Scaled return score

        return AgentAssessment(
            agent_name=self.name,
            role=self.role,
            is_acceptable=True,
            score=min(1.0, score),
            findings=findings,
            suggested_actions=proposals
        )
