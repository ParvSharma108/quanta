# QUANTA Frontend Dashboard

Modern, responsive web dashboard for QUANTA — Autonomous Financial Treasury & Quantum Capital Optimization.

## Features & Modules

1. **Treasury Overview**: Real-time capital base KPI cards (₹100 Cr), statutory liquidity floor tracking, expected annualized return, and interactive asset allocation donut & comparison charts.
2. **Quantum QAOA Lab**: Interactive quantum parameter playground (circuit depth $p \in [1, 4]$, measurement shots, binary slack variable expansion toggle, and computational basis statevector probability distributions).
3. **Classical Benchmark**: Multi-solver comparison scorecard evaluating Exact Enumeration, Greedy Heuristics, Simulated Annealing, Continuous SLSQP, and HiGHS MILP side-by-side with sortable performance metrics.
4. **AI Deliberation Council**: Multi-agent consensus deliberation panel showing opinions and rationale from `TreasuryAgent`, `RiskAgent`, and `ComplianceAgent` alongside deterministic A* search trajectory timelines.
5. **Balance Sheet Editor**: Interactive live slider controls for Total Capital, Risk Tolerance ($\lambda$), and Minimum Liquidity floors, with asset ticket configuration.
6. **Empirical Results**: Direct visual access to the research benchmark plots (`runtime_vs_n_scaling.png`, `qaoa_approx_ratio_vs_p.png`, `feasibility_rate_by_method.png`, `objective_gap_vs_exact.png`).

## Technology Stack

- **Framework**: Svelte 5 + TypeScript + Vite 6
- **Styling**: Tailwind CSS + Glassmorphism design system + Lucide Icons
- **Data Visualization**: Chart.js (Responsive Canvas)
- **Deployment**: Multi-stage Dockerfile with Nginx serving static assets on port 3000

## Quickstart

```bash
# Install dependencies
npm install

# Run dev server
npm run dev

# Build production bundle
npm run build
```
