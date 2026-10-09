"""Synthetic INR 100 Cr Capital Allocation Benchmark Demonstration.

Runs:
- Breadth-First Search (BFS)
- Depth-First Search (DFS)
- Generate-and-Test
- Hill Climbing (Steepest Ascent)
- Greedy Best-First Search
- A* Search
- Multi-Agent Deliberation Council (Treasury, Risk, Compliance, Decision)
- Adversarial Alpha-Beta Stress Test
- Bayesian Risk Reasoning
- Monte Carlo VaR Simulation
"""

import sys
import os

# Set UTF-8 encoding for stdout if available
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Add service root to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.domain.asset import Asset, AssetType
from app.domain.liability import Liability
from app.domain.constraint import Constraint, ConstraintType, ConstraintSeverity
from app.domain.financial_problem import FinancialProblem, FinancialAllocationProblem
from app.search.bfs import BreadthFirstSearch
from app.search.dfs import DepthFirstSearch
from app.search.generate_and_test import GenerateAndTest
from app.search.hill_climbing import HillClimbingSearch
from app.search.best_first import BestFirstSearch
from app.search.astar import AStarSearch
from app.risk.scoring import RiskEngine
from app.risk.bayesian import BayesianRiskNetwork, BayesianEvidence
from app.risk.sampling import MonteCarloRiskSimulator
from app.game.alpha_beta import AlphaBetaPruningSolver
from app.agents.decision_agent import DecisionAgent


def build_synthetic_problem() -> FinancialProblem:
    """Construct the canonical INR 100 Cr corporate treasury problem."""
    assets = [
        Asset(
            id="gov_bond",
            name="Government Bonds",
            asset_type=AssetType.GOV_BOND,
            expected_return=0.07,
            risk=0.05,
            liquidity=0.95,
            volatility=0.03
        ),
        Asset(
            id="corp_bond",
            name="Corporate Bonds",
            asset_type=AssetType.CORP_BOND,
            expected_return=0.09,
            risk=0.15,
            liquidity=0.75,
            volatility=0.08
        ),
        Asset(
            id="equity",
            name="Equity Portfolio",
            asset_type=AssetType.EQUITY,
            expected_return=0.14,
            risk=0.40,
            liquidity=0.80,
            volatility=0.22
        ),
        Asset(
            id="cash_buffer",
            name="Cash Equivalents / T-Bills",
            asset_type=AssetType.CASH,
            expected_return=0.03,
            risk=0.01,
            liquidity=1.00,
            volatility=0.001
        ),
    ]

    liabilities = [
        Liability(
            id="term_loan_1",
            name="Senior Term Debt",
            principal=15.0,  # INR 15 Cr
            interest_rate=0.085,
            maturity_months=12,
            priority=1,
            is_mandatory_reserve=True
        )
    ]

    constraints = [
        Constraint(
            id="c_min_liq",
            constraint_type=ConstraintType.MINIMUM_LIQUIDITY,
            description="Maintain at least 20% portfolio weighted liquidity",
            parameters={"threshold": 0.20},
            severity=ConstraintSeverity.CRITICAL
        ),
        Constraint(
            id="c_max_risk",
            constraint_type=ConstraintType.MAXIMUM_RISK,
            description="Portfolio risk score must not exceed 0.30",
            parameters={"threshold": 0.30},
            severity=ConstraintSeverity.CRITICAL
        ),
        Constraint(
            id="c_max_equity",
            constraint_type=ConstraintType.MAXIMUM_ASSET_TYPE_EXPOSURE,
            description="Maximum 30% capital allocation to equity class",
            parameters={"asset_type": "equity", "max_fraction": 0.30},
            severity=ConstraintSeverity.CRITICAL
        ),
        Constraint(
            id="c_debt_reserve",
            constraint_type=ConstraintType.DEBT_RESERVE,
            description="Mandatory debt servicing reserve of INR 15 Cr",
            parameters={"amount": 15.0},
            severity=ConstraintSeverity.CRITICAL
        ),
    ]

    return FinancialProblem(
        capital=100.0,
        step_size=5.0,  # INR 5 Cr discrete increments
        assets=assets,
        liabilities=liabilities,
        constraints=constraints,
        risk_tolerance=0.50,
        minimum_liquidity=0.20,
        objective="maximize_risk_adjusted_return",
        market_state="normal"
    )


def run_benchmark():
    print("=" * 80)
    print("QUANTA -- AI Decision Engine: INR 100 Cr Benchmark Demonstration")
    print("=" * 80)

    problem = build_synthetic_problem()
    search_problem = FinancialAllocationProblem(problem)

    print("\n1. PROBLEM FORMULATION:")
    print(f"   Total Balance Sheet Capital : INR {problem.capital:.2f} Cr")
    print(f"   Allocation Granularity Step : INR {problem.step_size:.2f} Cr")
    print(f"   Mandatory Debt Reserve Req  : INR {search_problem.mandatory_debt_reserve:.2f} Cr")
    print(f"   Minimum Liquidity Ratio     : {problem.minimum_liquidity*100:.1f}%")
    print(f"   Available Assets            : {[a.name for a in problem.assets]}")

    algorithms = [
        BreadthFirstSearch(),
        DepthFirstSearch(),
        GenerateAndTest(),
        HillClimbingSearch(num_restarts=3),
        BestFirstSearch(),
        AStarSearch(),
    ]

    print("\n2. EXECUTING CLASSICAL AI SEARCH ALGORITHMS:\n")
    print(f"{'Algorithm':<32} | {'Success':<7} | {'Exp Return':<10} | {'Risk':<7} | {'Liquidity':<9} | {'Explored':<8} | {'Time (ms)':<9}")
    print("-" * 96)

    results = []
    for algo in algorithms:
        res = algo.search(search_problem)
        results.append(res)
        final_ret = f"{res.expected_return*100:.2f}%" if res.success else "N/A"
        final_risk = f"{res.risk_score:.4f}" if res.success else "N/A"
        final_liq = f"{res.liquidity_ratio*100:.1f}%" if res.success else "N/A"
        print(f"{res.algorithm:<32} | {str(res.success):<7} | {final_ret:<10} | {final_risk:<7} | {final_liq:<9} | {res.states_explored:<8} | {res.execution_time_ms:<9.2f}")

    # Inspect A* solution details
    astar_res = next(r for r in results if r.algorithm == "A* Search")
    print("\n3. DETAILED ALLOCATION FROM A* SEARCH:")
    if astar_res.final_state:
        st = astar_res.final_state
        print(f"   - Reserved for Liabilities : INR {st.reserved_for_debt:.2f} Cr")
        print(f"   - Liquid Cash Retained     : INR {st.cash:.2f} Cr")
        for a_id, amt in st.allocations.items():
            print(f"   - {search_problem.assets_map[a_id].name:<26} : INR {amt:.2f} Cr")
        print(f"   - Total Allocated + Reserved : INR {sum(st.allocations.values()) + st.reserved_for_debt + st.cash:.2f} Cr")
        print(f"   - Annual Expected Return     : {st.expected_return*100:.2f}%")
        print(f"   - Portfolio Risk Index       : {st.risk_score:.4f}")
        print(f"   - Portfolio Liquidity Ratio  : {st.liquidity_ratio*100:.1f}%")

    print("\n4. CONSTRAINT COMPLIANCE AUDIT:")
    evals = search_problem.evaluate_constraints(astar_res.final_state)
    for ev in evals:
        status_icon = "[PASS]" if ev.satisfied else "[FAIL]"
        print(f"   {status_icon} {ev.constraint_id:<20}: {ev.message}")

    print("\n5. MULTI-FACTOR RISK DECOMPOSITION:")
    risk_engine = RiskEngine()
    risk_breakdown = risk_engine.analyze(astar_res.final_state, search_problem.assets_map)
    print(f"   - Base Weighted Asset Risk   : {risk_breakdown.weighted_asset_risk:.4f}")
    print(f"   - Concentration HHI Index    : {risk_breakdown.concentration_index_hhi:.4f} (+{risk_breakdown.concentration_penalty:.4f})")
    print(f"   - Liquidity Deficit Penalty  : +{risk_breakdown.liquidity_deficit_penalty:.4f}")
    print(f"   - Debt Leverage Penalty      : +{risk_breakdown.leverage_penalty:.4f}")
    print(f"   - Composite Risk Score       : {risk_breakdown.composite_risk_score:.4f} ({risk_breakdown.risk_tier})")

    print("\n6. BAYESIAN MACROECONOMIC SHOCK REASONING:")
    bayes = BayesianRiskNetwork()
    evidence = BayesianEvidence(inflation_high=True, rate_hike=True)
    bayes_res = bayes.infer(evidence)
    print(f"   Evidence Observed: High Inflation=True, Rate Hike=True")
    print(f"   - Posterior P(Recession)        : {bayes_res.p_recession*100:.1f}%")
    print(f"   - Posterior P(Liquidity Crisis) : {bayes_res.p_liquidity_crisis*100:.1f}%")
    print(f"   - Stress Multiplier             : {bayes_res.stress_multiplier:.2f}x")
    print(f"   - Bayesian Insight              : {bayes_res.explanation}")

    print("\n7. MONTE CARLO VALUE-AT-RISK (VaR) STRESS SIMULATION (2,000 SCENARIOS):")
    mc = MonteCarloRiskSimulator(seed=42)
    mc_report = mc.simulate(astar_res.final_state, search_problem.assets_map, num_scenarios=2000)
    print(f"   - Mean Simulated Return  : {mc_report.mean_simulated_return*100:.2f}% (Std: {mc_report.std_simulated_return*100:.2f}%)")
    print(f"   - Parametric VaR (95%)   : {mc_report.var_95*100:.2f}% max expected loss")
    print(f"   - Expected Shortfall CVaR: {mc_report.cvar_95*100:.2f}%")
    print(f"   - Probability of Loss    : {mc_report.probability_of_loss*100:.1f}%")

    print("\n8. ADVERSARIAL ALPHA-BETA GAME STRESS TESTING:")
    game_solver = AlphaBetaPruningSolver(max_depth=3)
    stress_res = game_solver.stress_test(search_problem)
    print(f"   - Evaluated Nodes        : {stress_res.nodes_evaluated} (Pruned: {stress_res.pruned_branches})")
    print(f"   - Worst-Case Payoff      : {stress_res.worst_case_payoff:.4f}")
    print(f"   - Worst Adversary Shock  : {stress_res.worst_market_shock}")
    print(f"   - Robust Action Selected : {stress_res.best_treasury_action}")

    print("\n9. MULTI-AGENT COUNCIL DELIBERATION (TREASURY, RISK, COMPLIANCE, DECISION):")
    decision_agent = DecisionAgent()
    deliberation = decision_agent.synthesize_strategy(search_problem)
    print(f"   - Treasury Agent Opinion : Acceptable={deliberation.treasury_opinion.is_acceptable}, Score={deliberation.treasury_opinion.score:.2f}")
    print(f"   - Risk Agent Opinion     : Acceptable={deliberation.risk_opinion.is_acceptable}, Score={deliberation.risk_opinion.score:.2f}")
    print(f"   - Compliance Opinion     : Acceptable={deliberation.compliance_opinion.is_acceptable}, Score={deliberation.compliance_opinion.score:.2f}")
    print(f"   - Consensus Reached      : {deliberation.consensus_reached}")
    print(f"   - Synthesized Explanation: {deliberation.recommended_strategy.explanation}")

    print("\n" + "=" * 80)
    print("DEMONSTRATION COMPLETED SUCCESSFULLY.")
    print("=" * 80)


if __name__ == "__main__":
    run_benchmark()
