"""RiskAgent focusing on portfolio safety, diversification, and volatility control."""

from typing import List
from app.agents.base import IntelligentAgent, AgentRole, AgentAssessment, ActionProposal
from app.domain.financial_state import FinancialState
from app.domain.strategy import FinancialAction, FinancialActionType
from app.domain.financial_problem import FinancialAllocationProblem
from app.risk.scoring import RiskEngine


class RiskAgent(IntelligentAgent):
    """Specialist agent monitoring volatility, concentration, and drawdown risks."""

    def __init__(self, max_allowable_risk: float = 0.30):
        super().__init__(name="Chief Risk Officer Agent", role=AgentRole.RISK)
        self.max_allowable_risk = max_allowable_risk
        self.risk_engine = RiskEngine()

    def perceive_and_assess(
        self, state: FinancialState, problem: FinancialAllocationProblem
    ) -> AgentAssessment:
        breakdown = self.risk_engine.analyze(state, problem.assets_map)
        findings: List[str] = list(breakdown.explanations)
        proposals: List[ActionProposal] = []

        is_acceptable = breakdown.composite_risk_score <= self.max_allowable_risk

        if not is_acceptable:
            findings.append(
                f"ALERT: Portfolio composite risk ({breakdown.composite_risk_score:.4f}) exceeds safety ceiling ({self.max_allowable_risk:.4f})."
            )
            # Propose de-risking actions: shift to safest liquid assets or cash
            safest_assets = sorted(problem.assets_list, key=lambda a: a.risk)
            for safe_asset in safest_assets[:2]:
                act = FinancialAction(
                    action_type=FinancialActionType.INVEST,
                    asset_id=safe_asset.id,
                    amount=problem.step_size,
                    reason=f"De-risk portfolio by directing flow to low-risk {safe_asset.name}"
                )
                proposals.append(
                    ActionProposal(
                        proposed_by=self.role,
                        action=act,
                        confidence=0.90,
                        expected_utility_delta=0.05,
                        rationale=f"Allocate to {safe_asset.name} (risk={safe_asset.risk:.2f}) to dilute portfolio risk"
                    )
                )

        score = max(0.0, 1.0 - (breakdown.composite_risk_score / max(0.01, self.max_allowable_risk)))

        return AgentAssessment(
            agent_name=self.name,
            role=self.role,
            is_acceptable=is_acceptable,
            score=min(1.0, score),
            findings=findings,
            suggested_actions=proposals
        )
