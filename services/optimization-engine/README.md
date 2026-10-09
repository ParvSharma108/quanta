# Optimization Engine (Parv - Member 2)

This directory houses the Mathematical Programming and Quantum Optimization Engine for QUANTA.

## Responsibilities
- Classical Linear & Quadratic Programming (Simplex, Interior Point, Scipy optimize)
- Quadratic Unconstrained Binary Optimization (QUBO) formulations
- Quantum Approximate Optimization Algorithm (QAOA)
- Quantum simulator experiments (Qiskit / Pennylane)
- Benchmarking: Classical optimization vs Quantum annealing/QAOA solvers

## Interface Contract
- Operates on the unified `FinancialProblem` model specified in `shared/schemas/financial_problem.json`.
- Exposes REST endpoints on port 8001 to return optimized allocation vectors, duality gaps, quantum circuit depths, and execution runtimes.
