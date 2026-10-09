# QUANTA — System Architecture & Monorepo Design

## 1. System Topology

```
                                  +-----------------------------+
                                  |     User Web Dashboard      |
                                  |   (SvelteKit + TypeScript)  |
                                  |        Port: 3000           |
                                  +--------------+--------------+
                                                 | REST / JSON
                                                 v
                                  +-----------------------------+
                                  |        Go Backend           |
                                  |     (REST API & Auth)       |
                                  |        Port: 8080           |
                                  +-------+--------------+------+
                                          |              |
                    +---------------------+              +----------------------+
                    | PostgreSQL                         |                      |
                    v                                    v                      v
         +--------------------+             +--------------------+    +--------------------+
         |  PostgreSQL 16 DB  |             |  Python AI Engine  |    | Optimization Engine|
         |    Port: 5432      |             | (Search, CSP, Risk)|    |  (QUBO, QAOA, Sim) |
         |   (Audit Logs &    |             |    Port: 8000      |    |    Port: 8001      |
         |    Treasuries)     |             |     [ATHARV]       |    |      [PARV]        |
         +--------------------+             +--------------------+    +--------------------+
```

---

## 2. Team Ownership & Responsibilities

| Team Member | Module & Codebase | Technology | Core Responsibilities |
| :--- | :--- | :--- | :--- |
| **Atharv (Lead)** | `services/ai-engine/` | Python 3.12+, FastAPI, NumPy, SciPy | AI Search (BFS, DFS, Generate-and-Test, Hill Climbing, Best-First, A*), CSP, Bayesian Risk Reasoning, Game Theory (Minimax/Alpha-Beta), MDP, Multi-Agent Deliberation Council. |
| **Parv** | `services/optimization-engine/` | Python, Scipy, QUBO, QAOA, Qiskit/Pennylane | Mathematical programming (LP, QP), Quadratic Unconstrained Binary Optimization (QUBO), Quantum Approximate Optimization Algorithm (QAOA), Classical vs Quantum benchmarking. |
| **Aryan** | `apps/backend/`, `apps/frontend/`, `infrastructure/` | Go, PostgreSQL, SvelteKit, Docker | Go API gateway, PostgreSQL persistence, authentication, audit logging, Docker compose orchestration, interactive dashboard. |

---

## 3. Directory Layout

```
quanta/
├── apps/
│   ├── frontend/             # SvelteKit Dashboard (Aryan)
│   └── backend/              # Go REST Service & Database Migrations (Aryan)
│
├── services/
│   ├── ai-engine/            # Python AI Decision Engine (Atharv - Fully Implemented)
│   │   ├── app/
│   │   │   ├── domain/       # FinancialState, FinancialProblem, Asset, Liability, Constraint, Strategy
│   │   │   ├── search/       # BFS, DFS, Generate-and-Test, Hill Climbing, Best First, A*
│   │   │   ├── csp/          # CSP Model, Constraints, Backtracking Solver (MRV + Forward Checking)
│   │   │   ├── risk/         # Multi-factor Risk Scoring, Bayesian Shock Network, Monte Carlo VaR
│   │   │   ├── game/         # Adversarial Minimax & Alpha-Beta Pruning
│   │   │   ├── mdp/          # Multi-Period Rebalancing MDP & Value Iteration
│   │   │   ├── agents/       # Treasury, Risk, Compliance, and Decision Agent Council
│   │   │   └── api/          # FastAPI REST endpoints
│   │   ├── tests/            # 23 Unit & Integration Tests (pytest)
│   │   └── examples/         # Basic Capital Allocation Benchmark (₹100 Cr synthetic case)
│   │
│   └── optimization-engine/  # Mathematical & Quantum Solvers (Parv)
│
├── shared/
│   └── schemas/              # Canonical JSON Schema Contracts
├── infrastructure/
│   ├── docker/               # Docker configurations
│   └── postgres/             # Database initialization script (init.sql)
├── docs/                     # Technical specifications & integration contracts
├── docker-compose.yml        # Full system orchestration
├── Makefile                  # Developer CLI commands
└── README.md
```
