"""CSP Variable, Domain, and Problem models."""

from typing import Any, Callable, Dict, Generic, List, Optional, Set, TypeVar

V = TypeVar("V")  # Variable type
D = TypeVar("D")  # Domain value type


class CSPVariable(Generic[V, D]):
    """Variable in a Constraint Satisfaction Problem."""

    def __init__(self, name: V, domain: List[D]):
        self.name = name
        self.domain = list(domain)

    def __repr__(self) -> str:
        return f"<CSPVar {self.name}: {len(self.domain)} values>"


class CSPConstraint(ABC := object):
    """Abstract base class for CSP constraints."""

    def __init__(self, variables: List[Any], name: str = ""):
        self.variables = variables
        self.name = name or self.__class__.__name__

    def is_satisfied(self, assignment: Dict[Any, Any]) -> bool:
        """Check if current partial or full assignment satisfies constraint."""
        raise NotImplementedError


class CSPModel:
    """CSP formulation containing variables, domains, and constraints."""

    def __init__(self):
        self.variables: Dict[str, CSPVariable[str, Any]] = {}
        self.constraints: List[CSPConstraint] = []
        self.var_constraints_map: Dict[str, List[CSPConstraint]] = {}

    def add_variable(self, name: str, domain: List[Any]) -> None:
        """Add a variable with its discrete domain."""
        var = CSPVariable(name, domain)
        self.variables[name] = var
        self.var_constraints_map[name] = []

    def add_constraint(self, constraint: CSPConstraint) -> None:
        """Register a constraint over a subset of variables."""
        self.constraints.append(constraint)
        for var in constraint.variables:
            if var in self.var_constraints_map:
                self.var_constraints_map[var].append(constraint)
