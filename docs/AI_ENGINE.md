# QUANTA AI Decision Engine — Technical Specification & Academic Formulation

**Author:** Atharv (Member 1 — Team Lead)  
**Module:** AI Decision Engine (`services/ai-engine`)  
**Version:** 1.0.0 (Phase 1 Working Prototype)  

---

## 1. Academic & Syllabus Mapping

The QUANTA AI Decision Engine is structured around classical Artificial Intelligence fundamentals, directly mapping theoretical AI concepts to real-world corporate financial treasury management:

| AI Syllabus Unit | Theoretical Concept | QUANTA Financial Implementation | Primary Source File |
| :--- | :--- | :--- | :--- |
| **Unit I** | Problem Spaces & Formulations | Discrete Balance-Sheet State Space $S$, Physical Conservation Laws | `app/domain/financial_state.py` |
| **Unit II** | Uninformed Search | Breadth-First Search (BFS), Depth-First Search (DFS) | `app/search/bfs.py`, `app/search/dfs.py` |
| **Unit II** | Informed & Heuristic Search | Systematic Generate-and-Test, Steepest-Ascent Hill Climbing, Greedy Best-First, $A^*$ Search | `app/search/generate_and_test.py`, `app/search/hill_climbing.py`, `app/search/best_first.py`, `app/search/astar.py` |
| **Unit III** | Constraint Satisfaction (CSP) | Backtracking with Forward Checking & MRV heuristics across portfolio limits & liquidity floors | `app/csp/model.py`, `app/csp/solver.py` |
| **Unit III** | Adversarial Game Search | Minimax & Alpha-Beta Pruning modeling Treasury (MAX) vs Market Shock (MIN) | `app/game/minimax.py`, `app/game/alpha_beta.py` |
| **Unit IV** | Markov Decision Processes | Multi-period Dynamic Rebalancing MDP solved via Bellman Value Iteration | `app/mdp/environment.py`, `app/mdp/transitions.py` |
| **Unit V** | Intelligent Agents & Bayesian Networks | Cooperative Agent Council (`TreasuryAgent`, `RiskAgent`, `ComplianceAgent`, `DecisionAgent`) & Bayesian Macro Risk Network | `app/agents/`, `app/risk/bayesian.py` |

---

## 2. Financial State Space Formulation

Let $C \in \mathbb{R}^+$ be the total available capital (e.g., ₹100 Cr). A discrete state $S$ is defined as:

$$S = \left\langle c, \mathbf{a}, \mathbf{L}, d, \ell, \rho, r, \mathcal{M}, \mathcal{H} \right\rangle$$

Where:
- $c \ge 0$: Unallocated liquid cash balance.
- $\mathbf{a} = \{a_1, a_2, \dots, a_N\}$: Allocation vector where $a_i \ge 0$ is the capital allocated to asset $i$.
- $\mathbf{L}$: Vector of active corporate liabilities.
- $d \ge 0$: Liquid cash earmarked specifically for mandatory debt service.
- $\ell \in [0, 1]$: Weighted portfolio liquidity ratio.
- $\rho \in [0, 1]$: Composite normalized portfolio risk index.
- $r \in \mathbb{R}$: Annualized capital-weighted expected nominal return.
- $\mathcal{M} \in \{\text{normal}, \text{bull}, \text{bear}, \text{volatile}\}$: Macroeconomic regime tag.
- $\mathcal{H} = [u_1, u_2, \dots, u_k]$: Chronological sequence of actions executed from the root state.

### Balance Sheet Conservation Law
For any valid state $S$, the following strict conservation condition must hold:

$$c + d + \sum_{i=1}^{N} a_i = C \quad \text{and} \quad c, d, a_i \ge 0 \quad \forall i$$

---

## 3. Financial Action Space

At each step, given discrete step quantum $\Delta c$ (e.g. ₹5 Cr), the action space $\mathcal{U}(S)$ consists of:

1. **`INVEST(asset_id, amount)`**: Deploys $\Delta c$ from cash $c$ into target asset $a_i$:
   $$c' = c - \Delta c, \quad a_i' = a_i + \Delta c$$
2. **`RESERVE_CAPITAL(amount)`**: Earmarks $\Delta c$ from cash $c$ into debt reserve $d$:
   $$c' = c - \Delta c, \quad d' = d + \Delta c$$
3. **`REBALANCE(asset_id, amount)`**: Transfers capital between asset buckets or between asset and cash.
4. **`REPAY_DEBT(amount)`**: Discharges debt principal from earmarked reserve $d$.
5. **`HOLD_CASH(amount)`**: Finalizes the allocation process, retaining residual $c$ in risk-free liquid cash equivalents.

---

## 4. Search Problem & Heuristic Design

The search problem is formalized in `FinancialAllocationProblem`:
- **Initial State $S_0$**: $c = C, d = 0, \mathbf{a} = \mathbf{0}, \ell = 1.0, \rho = 0.01, r = r_{\text{cash}}$.
- **Goal Test $\mathcal{G}(S)$**: $c < \Delta c$ (capital fully deployed or reserved) **and** $S$ is strictly compliant with all critical hard constraints.

### A* Path Cost $g(n)$ and Heuristic $h(n)$
To find the maximum risk-adjusted utility using minimum-cost search, transition costs and heuristics are formulated as:

1. **Step Cost $c(S, u, S')$**:
   $$c(S, u, S') = \text{Offset} - \left( U(S') - U(S) \right) + \text{Cost}(u) + \text{Penalty}(S')$$
   Where economic utility is:
   $$U(S) = r(S) - (1 - \tau) \cdot \lambda \cdot \rho(S)^2 + w_\ell \cdot \ell(S)$$
   ($\tau$ = risk tolerance, $\lambda$ = risk aversion factor = $1.5$, $w_\ell$ = liquidity weight = $0.25$).

2. **Admissible Heuristic $h(n)$**:
   $$h(n) = \max\left(0, \frac{c_n}{\Delta c} \cdot \epsilon - \frac{c_n}{C} \cdot r_{\max} \cdot \gamma\right)$$
   $h(n)$ provides an admissible, monotonic lower-bound on the remaining cost-to-go, guaranteeing that $A^*$ returns the optimal allocation trajectory.

---

## 5. Constraint Satisfaction Framework (CSP)

The CSP solver evaluates:
1. **Capital Budget**: $\sum a_i + c + d = C$
2. **Minimum Liquidity Floor**: $\ell(S) = \frac{c + d + \sum a_i \cdot \ell_i}{C} \ge L_{\min}$
3. **Maximum Risk Ceiling**: $\rho(S) \le R_{\max}$
4. **Mandatory Debt Reserve**: $d \ge \sum_{j \in \text{Mandatory}} L_j$
5. **Asset & Class Caps**: $\sum_{i \in \text{Class}} a_i \le \text{Cap}_{\text{Class}} \cdot C$

The Backtracking solver employs **Forward Checking** (domain filtering) and the **Minimum Remaining Values (MRV)** heuristic with degree tie-breaking.

---

## 6. Multi-Factor Deterministic Risk Engine

Portfolio risk $\rho(S) \in [0, 1]$ is computed deterministically across four explainable pillars:

$$\rho(S) = 0.60 \cdot \rho_{\text{asset}} + 0.15 \cdot \left(\frac{\text{HHI}}{2}\right) + 0.20 \cdot \left(\frac{\max(0, L_{\min} - \ell)}{L_{\min}}\right)^2 + 0.10 \cdot \rho_{\text{leverage}}$$

Where:
- $\rho_{\text{asset}} = \frac{c \cdot r_{\text{cash\_risk}} + \sum a_i \cdot \text{risk}_i}{C}$
- $\text{HHI} = \left(\frac{c+d}{C}\right)^2 + \sum \left(\frac{a_i}{C}\right)^2$ (Herfindahl-Hirschman Concentration Index)
- $\rho_{\text{leverage}} = \min\left(1, \frac{\text{Debt}}{C}\right) \cdot \left(1 - \frac{d}{\text{Debt}}\right)$

---

## 7. Intelligent Agent Council Architecture

QUANTA does **not** use an LLM for financial computations. Instead, it utilizes classical intelligent agents collaborating through structured message passing and council deliberation:

```
                      ┌──────────────────────────────────────┐
                      │            DecisionAgent             │
                      │ (Synthesizer & Council Coordinator)  │
                      └──────────────────┬───────────────────┘
                                         │
                 ┌───────────────────────┼───────────────────────┐
                 │                       │                       │
                 ▼                       ▼                       ▼
      ┌────────────────────┐  ┌────────────────────┐  ┌────────────────────┐
      │   TreasuryAgent    │  │     RiskAgent      │  │  ComplianceAgent   │
      │  (Yield & Return)  │  │ (Safety & Vol)     │  │ (Rules & Reserves) │
      └────────────────────┘  └────────────────────┘  └────────────────────┘
```

1. **`TreasuryAgent`**: Evaluates capital productivity, unallocated idle cash, and identifies highest yielding instruments.
2. **`RiskAgent`**: Monitors concentration risk, tail-risk drawdown, and enforces volatility thresholds.
3. **`ComplianceAgent`**: Validates regulatory requirements, debt servicing covenants, and liquidity floors.
4. **`DecisionAgent`**: Reconciles conflicting proposals, executes algorithmic $A^*$ optimization, and compiles an explainable strategy audit.

---

## 8. Adversarial Stress-Testing (Minimax & Alpha-Beta)

To ensure capital resilience against macroeconomic crises, QUANTA evaluates strategies against an adverse market player:
- **MAX Player (Treasury)**: Selects capital allocation actions to maximize risk-adjusted payoff.
- **MIN Player (Market Adversary)**: Selects worst-case macroeconomic shock events (e.g. *Severe Equity & Credit Crash*, *Liquidity Squeeze*, *Macro Stagflation*).
- **Alpha-Beta Pruning**: Prunes dominated shock branches to rapidly find the game-theoretic minimax robust strategy.
