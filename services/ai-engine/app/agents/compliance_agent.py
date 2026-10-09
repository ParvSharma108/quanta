"""ComplianceAgent validating statutory limits and treasury policy constraints."""

from typing import List
from app.agents.base import IntelligentAgent, AgentRole, AgentAssessment, ActionProposal
from app.domain.financial_state import FinancialState
from app.domain.strategy import FinancialAction, FinancialActionType
from app.domain.constraint import ConstraintSeverity
from app.domain.financial_problem import FinancialAllocationProblem


class ComplianceAgent(IntelligentAgent):
    """Specialist agent verifying regulatory compliance and constraint enforcement."""

    def __init__(self):
        super().__init__(name="Regulatory Compliance Agent", role=AgentRole.COMPLIANCE)

    def perceive_and_assess(
        self, state: FinancialState, problem: FinancialAllocationProblem
    ) -> AgentAssessment:
        evaluations = problem.evaluate_constraints(state)
        findings: List[str] = []
        proposals: List[ActionProposal] = []

        all_hard_satisfied = True
        violations_count = 0

        for res in evaluations:
            findings.append(res.message)
            if not res.satisfied:
                violations_count += 1
                if res.severity == ConstraintSeverity.CRITICAL:
                    all_hard_satisfied = False

                # Propose remedial action if debt reserve deficit
                if res.constraint_type.value == "debt_reserve":
                    needed = res.required - res.actual
                    act = FinancialAction(
                        action_type=FinancialActionType.RESERVE_CAPITAL,
                        amount=min(needed, state.cash),
                        reason="Mandatory compliance remediation: reserve capital for debt"
                    )
                    proposals.append(
                        ActionProposal(
                            proposed_by=self.role,
                            action=act,
                            confidence=1.0,
                            expected_utility_delta=0.20,
                            rationale=f"Fulfill mandatory debt reserve obligation of ₹{needed:.2f} Cr"
                        )
                    )

        total_rules = max(1, len(evaluations))
        compliance_score = (total_rules - violations_count) / total_rules

        return AgentAssessment(
            agent_name=self.name,
            role=self.role,
            is_acceptable=all_hard_satisfied,
            score=compliance_score,
            findings=findings,
            suggested_actions=proposals
        )
