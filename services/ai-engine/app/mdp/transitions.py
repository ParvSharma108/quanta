"""Transition probabilities and reward functions for treasury MDP."""

from typing import Dict, List, Tuple
from app.mdp.state import MDPState, MDPAction, PortfolioPosture, MarketRegime


# Regime Markov Transition Matrix: P(regime_{t+1} | regime_t)
REGIME_TRANSITIONS: Dict[MarketRegime, Dict[MarketRegime, float]] = {
    MarketRegime.BULL: {
        MarketRegime.BULL: 0.65,
        MarketRegime.NORMAL: 0.20,
        MarketRegime.VOLATILE: 0.10,
        MarketRegime.BEAR: 0.05,
    },
    MarketRegime.NORMAL: {
        MarketRegime.BULL: 0.25,
        MarketRegime.NORMAL: 0.50,
        MarketRegime.VOLATILE: 0.15,
        MarketRegime.BEAR: 0.10,
    },
    MarketRegime.VOLATILE: {
        MarketRegime.BULL: 0.15,
        MarketRegime.NORMAL: 0.30,
        MarketRegime.VOLATILE: 0.35,
        MarketRegime.BEAR: 0.20,
    },
    MarketRegime.BEAR: {
        MarketRegime.BULL: 0.10,
        MarketRegime.NORMAL: 0.30,
        MarketRegime.VOLATILE: 0.25,
        MarketRegime.BEAR: 0.35,
    },
}


def get_next_posture_and_liq(current: MDPState, action: MDPAction) -> Tuple[PortfolioPosture, bool]:
    """Determine resulting posture and liquidity state after action."""
    if action == MDPAction.MAINTAIN_CURRENT:
        return (current.posture, current.is_liquidity_sufficient)
    elif action == MDPAction.SHIFT_DEFENSIVE:
        return (PortfolioPosture.DEFENSIVE, True)
    elif action == MDPAction.SHIFT_BALANCED:
        return (PortfolioPosture.BALANCED, True)
    elif action == MDPAction.SHIFT_AGGRESSIVE:
        # Aggressive posture lowers liquid cash buffer
        return (PortfolioPosture.AGGRESSIVE, False if current.market_regime == MarketRegime.BEAR else True)
    elif action == MDPAction.INJECT_LIQUIDITY:
        return (PortfolioPosture.DEFENSIVE, True)
    return (current.posture, current.is_liquidity_sufficient)


def get_transition_probabilities(state: MDPState, action: MDPAction) -> List[Tuple[float, MDPState]]:
    """Compute list of (probability, next_state) for MDP Bellman update."""
    next_posture, next_liq = get_next_posture_and_liq(state, action)
    regime_probs = REGIME_TRANSITIONS[state.market_regime]

    transitions: List[Tuple[float, MDPState]] = []
    for next_regime, prob in regime_probs.items():
        # In Bear or Volatile market with Aggressive posture, liquidity risk increases
        final_liq = next_liq
        if next_posture == PortfolioPosture.AGGRESSIVE and next_regime in (MarketRegime.BEAR, MarketRegime.VOLATILE):
            final_liq = False

        s_prime = MDPState(posture=next_posture, market_regime=next_regime, is_liquidity_sufficient=final_liq)
        transitions.append((prob, s_prime))

    return transitions


def compute_reward(state: MDPState, action: MDPAction, next_state: MDPState) -> float:
    """Multi-objective reward: Return - Transaction_Cost - Risk_Penalty - Liquidity_Deficit_Penalty."""
    # 1. Base Expected Return by Posture & Regime
    return_matrix = {
        (PortfolioPosture.DEFENSIVE, MarketRegime.BULL): 0.05,
        (PortfolioPosture.DEFENSIVE, MarketRegime.NORMAL): 0.05,
        (PortfolioPosture.DEFENSIVE, MarketRegime.VOLATILE): 0.045,
        (PortfolioPosture.DEFENSIVE, MarketRegime.BEAR): 0.04,

        (PortfolioPosture.BALANCED, MarketRegime.BULL): 0.10,
        (PortfolioPosture.BALANCED, MarketRegime.NORMAL): 0.08,
        (PortfolioPosture.BALANCED, MarketRegime.VOLATILE): 0.06,
        (PortfolioPosture.BALANCED, MarketRegime.BEAR): -0.02,

        (PortfolioPosture.AGGRESSIVE, MarketRegime.BULL): 0.18,
        (PortfolioPosture.AGGRESSIVE, MarketRegime.NORMAL): 0.12,
        (PortfolioPosture.AGGRESSIVE, MarketRegime.VOLATILE): 0.02,
        (PortfolioPosture.AGGRESSIVE, MarketRegime.BEAR): -0.15,
    }
    base_ret = return_matrix.get((next_state.posture, next_state.market_regime), 0.05)

    # 2. Transaction cost for switching posture
    tx_cost = 0.005 if action not in (MDPAction.MAINTAIN_CURRENT,) else 0.0

    # 3. Risk and Liquidity penalties
    liq_penalty = 0.10 if not next_state.is_liquidity_sufficient else 0.0
    vol_penalty = 0.04 if next_state.market_regime == MarketRegime.VOLATILE and next_state.posture == PortfolioPosture.AGGRESSIVE else 0.0

    return base_ret - tx_cost - liq_penalty - vol_penalty
