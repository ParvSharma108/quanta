# QUANTA Modern Frontend Dashboard

Autonomous Financial Treasury & Quantum Capital Optimization web interface.

## Features & Modules

1. **Executive Treasury Cockpit**: Real-time capital base KPI cards (₹100 Cr default / dynamic multi-tenant), statutory liquidity floor tracking, expected annualized return, and interactive asset allocation donut & comparison charts.
2. **Corporate Treasury Management (`/treasuries`)**: Multi-tenant balance sheet onboarding, live PostgreSQL database integration, and detail views (`/treasuries/[id]`).
3. **Quantum QAOA Lab**: Interactive quantum parameter playground (circuit depth $p \in [1, 4]$, measurement shots, binary slack variable expansion toggle, and computational basis statevector probability distributions).
4. **Classical Benchmark Scorecard**: Multi-solver comparison scorecard evaluating Exact Enumeration, Greedy Heuristics, Simulated Annealing, Continuous SLSQP, and HiGHS MILP side-by-side with sortable performance metrics.
5. **AI Deliberation Council**: Multi-agent consensus deliberation panel showing opinions and rationale from `TreasuryAgent`, `RiskAgent`, and `ComplianceAgent` alongside deterministic A* search trajectory timelines.
6. **Balance Sheet & Parameter Editor**: Interactive live slider controls for Total Capital, Risk Tolerance ($\lambda$), and Minimum Liquidity floors, with asset ticket configuration.
7. **Adversarial Stress Testing & Risk**: Bayesian risk analysis, liquidity buffer checks, and VaR calculation.
8. **Security & RBAC Administration (`/admin/users`, `/admin/audit-logs`)**: Role-based access control (`admin`, `analyst`, `viewer`) and immutable audit trails.

## Technology Stack

- **Framework**: SvelteKit 3 + Svelte 5 (Runes) + TypeScript
- **Styling**: Tailwind CSS v4 + Dark-mode Glassmorphic Quantum Design System
- **Icons**: Lucide Svelte (`@lucide/svelte`)
- **Visualizations**: Chart.js reactive charts + Research benchmark plots
- **Backend Communication**: Go Backend (`:8080`), Optimization Engine (`:8001`), AI Decision Engine (`:8000`) with resilient client-side fallbacks

## Quickstart

```bash
# Navigate to frontend
cd apps/frontend

# Install dependencies
npm install

# Run dev server on port 3000
npm run dev

# Run type checks
npm run check

# Build production bundle
npm run build
```
