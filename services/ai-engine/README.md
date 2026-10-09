# AI Decision Engine (`services/ai-engine`)

**Lead Engineer:** Atharv (Member 1)  
**Framework:** FastAPI, Python 3.12+, Pydantic, NumPy, SciPy, pytest  

---

## Capabilities & Architecture

1. **Deterministic Search Engine**:
   - `BreadthFirstSearch` (BFS)
   - `DepthFirstSearch` (DFS)
   - `GenerateAndTest` (Systematic partition search)
   - `HillClimbingSearch` (Steepest ascent with local neighborhood rebalancing & restarts)
   - `BestFirstSearch` (Greedy best-first with heuristic guidance)
   - `AStarSearch` (Optimal $A^*$ search with admissible risk-adjusted heuristic $f(n) = g(n) + h(n)$)

2. **Constraint Satisfaction (CSP)**:
   - Backtracking solver with Forward Checking and Minimum Remaining Values (MRV) heuristic.
   - Enforces physical budget conservation, minimum liquidity floors, maximum risk ceilings, and mandatory liability reserves.

3. **Multi-Factor Risk Engine & Bayesian Reasoning**:
   - Deterministic 4-factor risk decomposition: Base Asset Risk + Concentration HHI Penalty + Liquidity Deficit Penalty + Leverage Penalty.
   - Bayesian Network for conditional probability inference under macroeconomic shocks (Recession, Rate Hikes, Liquidity Crises).
   - Monte Carlo Risk Simulator for parametric and historical Value-at-Risk (VaR 95/99) and Expected Shortfall (CVaR).

4. **Game-Theoretic Adversarial Stress Testing**:
   - Minimax and Alpha-Beta Pruning modeling Treasury optimization against worst-case macroeconomic shock adversaries.

5. **Dynamic Rebalancing MDP**:
   - Multi-period Markov Decision Process with state transitions across market regimes (Bull, Normal, Bear, Volatile) solved via Bellman Value Iteration.

6. **Intelligent Agent Council**:
   - Cooperative multi-agent council: `TreasuryAgent` (Yield), `RiskAgent` (Safety), `ComplianceAgent` (Statutory Rules), and `DecisionAgent` (Executive Orchestrator).

---

## Running the Engine

### Run Pytest Test Suite (23 Tests)
```bash
pytest -v
```

### Run Synthetic INR 100 Cr Benchmark
```bash
python examples/basic_capital_allocation.py
```

### Start FastAPI Web Service
```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```
Interactive OpenAPI Swagger documentation will be accessible at: `http://localhost:8000/docs`
