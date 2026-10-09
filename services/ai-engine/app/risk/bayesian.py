"""Bayesian network modeling for macroeconomic risk and conditional default reasoning."""

from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class BayesianEvidence(BaseModel):
    """Observed macroeconomic signals."""
    inflation_high: Optional[bool] = None
    rate_hike: Optional[bool] = None
    recession_signal: Optional[bool] = None


class BayesianRiskInferenceResult(BaseModel):
    """Posterior probabilities inferred from Bayesian network."""
    p_recession: float
    p_liquidity_crisis: float
    p_equity_downturn: float
    p_credit_spread_widening: float
    stress_multiplier: float
    explanation: str


class BayesianRiskNetwork:
    """Discrete Bayesian Network for macroeconomic and balance-sheet stress inference.
    
    Graph Topology:
    - Root 1: Inflation (High vs Normal) -> P(Inf=True) = 0.35
    - Root 2: Global Growth Slowdown -> P(Slow=True) = 0.25
    - Node: Rate Hike | Inflation -> P(RateHike | Inf)
    - Node: Recession | Inflation, Slowdown -> P(Recession | Inf, Slow)
    - Node: Liquidity Crisis | RateHike, Recession
    - Node: Equity Downturn | Recession
    - Node: Credit Spread Widening | RateHike, Recession
    """

    def __init__(self):
        # Prior probabilities
        self.p_inflation = 0.35
        self.p_slowdown = 0.25

        # Conditional probability tables (CPTs)
        # P(RateHike = True | Inflation)
        self.cpt_rate_hike = {
            True: 0.80,   # High inflation -> 80% rate hike probability
            False: 0.20   # Normal inflation -> 20%
        }

        # P(Recession = True | Inflation, Slowdown)
        self.cpt_recession = {
            (True, True): 0.70,
            (True, False): 0.40,
            (False, True): 0.50,
            (False, False): 0.10
        }

        # P(LiquidityCrisis = True | RateHike, Recession)
        self.cpt_liquidity_crisis = {
            (True, True): 0.65,
            (True, False): 0.30,
            (False, True): 0.45,
            (False, False): 0.05
        }

    def infer(self, evidence: Optional[BayesianEvidence] = None) -> BayesianRiskInferenceResult:
        """Perform exact Bayesian inference over macroeconomic shock probabilities."""
        ev = evidence or BayesianEvidence()

        # Enumerate over joint states of hidden variables (Inflation, Slowdown)
        total_weight = 0.0
        weighted_recession = 0.0
        weighted_liq_crisis = 0.0
        weighted_rate_hike = 0.0

        for inf in [True, False]:
            if ev.inflation_high is not None and ev.inflation_high != inf:
                continue
            p_inf = self.p_inflation if inf else (1.0 - self.p_inflation)

            for slow in [True, False]:
                if ev.recession_signal is not None and ev.recession_signal != slow:
                    # Treat signal as noisy indicator or direct clamp
                    pass
                p_slow = self.p_slowdown if slow else (1.0 - self.p_slowdown)
                prior_joint = p_inf * p_slow

                # Compute P(RateHike)
                p_rh = self.cpt_rate_hike[inf]
                for rh in [True, False]:
                    if ev.rate_hike is not None and ev.rate_hike != rh:
                        continue
                    p_rh_state = p_rh if rh else (1.0 - p_rh)

                    p_rec = self.cpt_recession[(inf, slow)]
                    for rec in [True, False]:
                        if ev.recession_signal is not None and ev.recession_signal != rec:
                            continue
                        p_rec_state = p_rec if rec else (1.0 - p_rec)

                        p_lc = self.cpt_liquidity_crisis[(rh, rec)]

                        state_prob = prior_joint * p_rh_state * p_rec_state
                        total_weight += state_prob

                        if rec:
                            weighted_recession += state_prob
                        if rh:
                            weighted_rate_hike += state_prob
                        weighted_liq_crisis += state_prob * p_lc

        if total_weight <= 0:
            # Fallback baseline
            p_post_rec = 0.25
            p_post_lc = 0.15
            p_post_rh = 0.40
        else:
            p_post_rec = weighted_recession / total_weight
            p_post_lc = weighted_liq_crisis / total_weight
            p_post_rh = weighted_rate_hike / total_weight

        p_eq_down = min(1.0, p_post_rec * 0.85 + 0.10)
        p_credit_widening = min(1.0, p_post_rh * 0.50 + p_post_rec * 0.40)
        stress_multiplier = 1.0 + (p_post_rec * 0.5 + p_post_lc * 0.8)

        explanation = (
            f"Posterior probability of recession is {p_post_rec*100:.1f}%, "
            f"liquidity crisis is {p_post_lc*100:.1f}%, resulting in a stress risk multiplier of {stress_multiplier:.2f}x."
        )

        return BayesianRiskInferenceResult(
            p_recession=p_post_rec,
            p_liquidity_crisis=p_post_lc,
            p_equity_downturn=p_eq_down,
            p_credit_spread_widening=p_credit_widening,
            stress_multiplier=stress_multiplier,
            explanation=explanation
        )
