"""DecisionAgent acting as executive orchestrator across specialist agents."""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

from app.agents.base import IntelligentAgent, AgentRole, AgentAssessment
from app.agents.treasury_agent import TreasuryAgent
from app.agents.risk_agent import RiskAgent
from app.agents.compliance_agent import ComplianceAgent
from app.domain.financial_state import FinancialState
from app.domain.strategy import Strategy, FinancialAction
from app.domain.financial_problem import FinancialAllocationProblem, FinancialProblem
from app.search.astar import AStarSearch
from app.search.base import SearchResult
from app.risk.scoring import RiskEngine


class DeliberationSummary(BaseModel):
    """Multi-agent council evaluation summary."""
    treasury_opinion: AgentAssessment
    risk_opinion: AgentAssessment
    compliance_opinion: AgentAssessment
    consensus_reached: bool
    recommended_strategy: Strategy
    search_metrics: SearchResult


class DecisionAgent(IntelligentAgent):
    """Executive synthesizer coordinating treasury, risk, and compliance agents."""

    def __init__(self):
        super().__init__(name="Chief Financial Decision Intelligence Agent", role=AgentRole.DECISION)
        self.treasury_agent = TreasuryAgent()
        self.risk_agent = RiskAgent()
        self.compliance_agent = ComplianceAgent()
        self.risk_engine = RiskEngine()

    def perceive_and_assess(
        self, state: FinancialState, problem: FinancialAllocationProblem
    ) -> AgentAssessment:
        t_assess = self.treasury_agent.perceive_and_assess(state, problem)
        r_assess = self.risk_agent.perceive_and_assess(state, problem)
        c_assess = self.compliance_agent.perceive_and_assess(state, problem)

        is_consensus = t_assess.is_acceptable and r_assess.is_acceptable and c_assess.is_acceptable
        avg_score = (t_assess.score + r_assess.score + c_assess.score) / 3.0

        findings = [
            f"Treasury score: {t_assess.score:.2f} | Risk score: {r_assess.score:.2f} | Compliance score: {c_assess.score:.2f}",
            f"Council consensus: {'APPROVED' if is_consensus else 'REJECTED / ACTION REQUIRED'}"
        ]

        return AgentAssessment(
            agent_name=self.name,
            role=self.role,
            is_acceptable=is_consensus,
            score=avg_score,
            findings=findings,
            suggested_actions=c_assess.suggested_actions or r_assess.suggested_actions or t_assess.suggested_actions
        )

    def synthesize_strategy(
        self, problem: FinancialAllocationProblem, search_algorithm_name: str = "astar"
    ) -> DeliberationSummary:
        """Run full multi-agent deliberation and algorithmic search optimization."""
        # 1. Initial council assessment
        initial_st = problem.initial_state
        t_init = self.treasury_agent.perceive_and_assess(initial_st, problem)
        r_init = self.risk_agent.perceive_and_assess(initial_st, problem)
        c_init = self.compliance_agent.perceive_and_assess(initial_st, problem)

        # 2. Algorithmic Search Optimization
        solver = AStarSearch()
        search_res = solver.search(problem)

        final_st = search_res.final_state or initial_st

        # 3. Post-search final council assessment
        t_final = self.treasury_agent.perceive_and_assess(final_st, problem)
        r_final = self.risk_agent.perceive_and_assess(final_st, problem)
        c_final = self.compliance_agent.perceive_and_assess(final_st, problem)

        is_compliant = problem.is_state_compliant(final_st)
        total_allocated = sum(final_st.allocations.values())

        # Construct explanation
        alloc_summary_parts = [
            f"₹{amt:.2f} Cr in {a_id}" for a_id, amt in final_st.allocations.items() if amt > 0
        ]
        if final_st.reserved_for_debt > 0:
            alloc_summary_parts.append(f"₹{final_st.reserved_for_debt:.2f} Cr reserved for liabilities")
        if final_st.cash > 0:
            alloc_summary_parts.append(f"₹{final_st.cash:.2f} Cr held as liquid cash")

        alloc_str = ", ".join(alloc_summary_parts)
        explanation = (
            f"Optimal strategy synthesized via {search_res.algorithm} in {search_res.execution_time_ms:.2f} ms "
            f"exploring {search_res.states_explored} states. "
            f"Portfolio allocated as: {alloc_str}. "
            f"Delivering an expected return of {final_st.expected_return*100:.2f}% with a composite risk of {final_st.risk_score:.4f} "
            f"and liquidity ratio of {final_st.liquidity_ratio*100:.1f}%."
        )

        strategy = Strategy(
            actions=search_res.actions,
            total_allocated=total_allocated,
            expected_return=final_st.expected_return,
            risk_score=final_st.risk_score,
            liquidity_ratio=final_st.liquidity_ratio,
            objective_value=search_res.objective_value,
            is_compliant=is_compliant,
            explanation=explanation,
            metadata={
                "algorithm": search_res.algorithm,
                "states_explored": search_res.states_explored,
                "execution_time_ms": search_res.execution_time_ms,
                "depth": search_res.depth,
                "final_allocations": final_st.allocations,
                "reserved_for_debt": final_st.reserved_for_debt,
                "cash_retained": final_st.cash
            }
        )

        return DeliberationSummary(
            treasury_opinion=t_final,
            risk_opinion=r_final,
            compliance_opinion=c_final,
            consensus_reached=is_compliant and r_final.is_acceptable,
            recommended_strategy=strategy,
            search_metrics=search_res
        )
