"""MDP Environment and Value Iteration solver for multi-period capital management."""

from typing import Dict, List, Tuple
from pydantic import BaseModel, Field
from app.mdp.state import MDPState, MDPAction, PortfolioPosture, MarketRegime
from app.mdp.transitions import get_transition_probabilities, compute_reward


class PolicyEvaluationReport(BaseModel):
    """Optimal policy mapping and state value table."""
    iterations_to_converge: int
    optimal_policy: Dict[str, str] = Field(..., description="Map of state string -> optimal action")
    state_values: Dict[str, float] = Field(..., description="Expected discounted values V*(s)")
    discount_factor: float


class TreasuryMDPEnvironment:
    """Solves the multi-period dynamic treasury allocation problem using Bellman Value Iteration."""

    def __init__(self, gamma: float = 0.95, theta: float = 1e-6):
        self.gamma = gamma
        self.theta = theta
        self.all_states = self._enumerate_states()
        self.all_actions = list(MDPAction)

    def _enumerate_states(self) -> List[MDPState]:
        """Enumerate all discrete finite states in the state space."""
        states: List[MDPState] = []
        for p in PortfolioPosture:
            for r in MarketRegime:
                for liq in (True, False):
                    states.append(MDPState(posture=p, market_regime=r, is_liquidity_sufficient=liq))
        return states

    def value_iteration(self, max_iterations: int = 500) -> PolicyEvaluationReport:
        """Run standard Bellman Value Iteration to compute optimal policy π*(s) and V*(s)."""
        V: Dict[MDPState, float] = {s: 0.0 for s in self.all_states}
        policy: Dict[MDPState, MDPAction] = {}

        iteration = 0
        while iteration < max_iterations:
            iteration += 1
            delta = 0.0
            new_V = dict(V)

            for s in self.all_states:
                action_values = []
                for a in self.all_actions:
                    expected_val = 0.0
                    for prob, s_prime in get_transition_probabilities(s, a):
                        reward = compute_reward(s, a, s_prime)
                        expected_val += prob * (reward + self.gamma * V[s_prime])
                    action_values.append((expected_val, a))

                best_val, best_action = max(action_values, key=lambda x: x[0])
                new_V[s] = best_val
                policy[s] = best_action
                delta = max(delta, abs(new_V[s] - V[s]))

            V = new_V
            if delta < self.theta:
                break

        # Format string keys for serialization
        policy_str = {f"{s.posture.value}:{s.market_regime.value}:liq={s.is_liquidity_sufficient}": policy[s].value for s in self.all_states}
        v_str = {f"{s.posture.value}:{s.market_regime.value}:liq={s.is_liquidity_sufficient}": round(V[s], 4) for s in self.all_states}

        return PolicyEvaluationReport(
            iterations_to_converge=iteration,
            optimal_policy=policy_str,
            state_values=v_str,
            discount_factor=self.gamma
        )
