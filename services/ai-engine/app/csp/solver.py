"""Backtracking CSP solver with Forward Checking and MRV heuristics."""

import copy
import time
from typing import Any, Dict, List, Optional, Tuple
from app.csp.model import CSPModel


class CSPSolverResult:
    """Outcome of CSP solver execution."""

    def __init__(
        self,
        success: bool,
        assignment: Optional[Dict[str, float]],
        nodes_explored: int,
        backtracks: int,
        execution_time_ms: float
    ):
        self.success = success
        self.assignment = assignment or {}
        self.nodes_explored = nodes_explored
        self.backtracks = backtracks
        self.execution_time_ms = execution_time_ms


class CSPSolver:
    """Backtracking solver supporting Forward Checking, MRV, and AC-3."""

    def __init__(self, model: CSPModel):
        self.model = model
        self.nodes_explored = 0
        self.backtracks = 0

    def is_consistent(self, var: str, value: Any, assignment: Dict[str, Any]) -> bool:
        """Check if assigning value to var is consistent with all relevant constraints."""
        temp_assignment = dict(assignment)
        temp_assignment[var] = value

        for constraint in self.model.var_constraints_map.get(var, []):
            if not constraint.is_satisfied(temp_assignment):
                return False
        return True

    def select_unassigned_variable_mrv(
        self, assignment: Dict[str, Any], domains: Dict[str, List[Any]]
    ) -> str:
        """Select unassigned variable with Minimum Remaining Values (MRV) and Degree heuristic."""
        unassigned = [v for v in self.model.variables if v not in assignment]
        
        # Sort by: (1) domain size ascending (MRV), (2) number of constraints descending (Degree)
        def var_key(v: str):
            domain_size = len(domains[v])
            degree = len(self.model.var_constraints_map.get(v, []))
            return (domain_size, -degree)

        return min(unassigned, key=var_key)

    def forward_check(
        self, var: str, value: Any, assignment: Dict[str, Any], domains: Dict[str, List[Any]]
    ) -> Optional[Dict[str, List[Any]]]:
        """Perform forward checking and prune incompatible values from neighbor domains."""
        new_domains = {v: list(d) for v, d in domains.items()}
        temp_assignment = dict(assignment)
        temp_assignment[var] = value

        for other_var in self.model.variables:
            if other_var not in temp_assignment:
                pruned_domain = []
                for other_val in new_domains[other_var]:
                    if self.is_consistent(other_var, other_val, temp_assignment):
                        pruned_domain.append(other_val)
                if not pruned_domain:
                    # Domain wipeout detected
                    return None
                new_domains[other_var] = pruned_domain

        return new_domains

    def solve(self, timeout_ms: float = 10000.0) -> CSPSolverResult:
        """Execute backtracking search with forward checking."""
        start_time = time.perf_counter()
        self.nodes_explored = 0
        self.backtracks = 0

        initial_domains = {v: list(var_obj.domain) for v, var_obj in self.model.variables.items()}

        def backtrack(
            assignment: Dict[str, Any], domains: Dict[str, List[Any]]
        ) -> Optional[Dict[str, Any]]:
            self.nodes_explored += 1
            
            # Base case: All variables assigned
            if len(assignment) == len(self.model.variables):
                # Verify full consistency across all constraints
                for constraint in self.model.constraints:
                    if not constraint.is_satisfied(assignment):
                        return None
                return assignment

            var = self.select_unassigned_variable_mrv(assignment, domains)
            
            # Value ordering: Descending values to prioritize higher productive allocations
            sorted_domain = sorted(domains[var], reverse=True)

            for val in sorted_domain:
                if self.is_consistent(var, val, assignment):
                    new_assignment = dict(assignment)
                    new_assignment[var] = val

                    # Forward checking
                    pruned_domains = self.forward_check(var, val, assignment, domains)
                    if pruned_domains is not None:
                        result = backtrack(new_assignment, pruned_domains)
                        if result is not None:
                            return result

                    self.backtracks += 1

            return None

        solution = backtrack({}, initial_domains)
        elapsed_ms = (time.perf_counter() - start_time) * 1000.0

        return CSPSolverResult(
            success=solution is not None,
            assignment=solution,
            nodes_explored=self.nodes_explored,
            backtracks=self.backtracks,
            execution_time_ms=elapsed_ms
        )
