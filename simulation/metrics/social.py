"""Compute all 7 metrics per round from market state."""
from __future__ import annotations
from typing import TYPE_CHECKING
import math

if TYPE_CHECKING:
    from ..engine.market import Market

from ..config import UTILITY_CONSUME, COST_PRODUCE, GOODS, N_AGENTS


def _gini(values: list[float]) -> float:
    if not values or sum(values) == 0:
        return 0.0
    n = len(values)
    sorted_v = sorted(values)
    cumsum = 0.0
    for i, v in enumerate(sorted_v):
        cumsum += (2 * (i + 1) - n - 1) * v
    return cumsum / (n * sum(sorted_v))


def compute_metrics(market: "Market", round_utilities: dict[int, float]) -> dict[str, float]:
    """
    round_utilities: {agent_id: utility_this_round}
    Returns dict with efficiency, equality, sustainability, peace + intermediate variables.
    """
    agent_ids = market.agent_ids
    n = len(agent_ids)

    # Efficiency: consumption utility realised / max possible consumption utility
    # Strips out production cost so a round with no trades = 0, perfect trading = 1.
    from ..config import MAX_PRODUCE
    current_prod = market.production_per_round[-1] if market.production_per_round else {}
    production_cost_this_round = sum(current_prod.values()) * COST_PRODUCE
    actual_utility = sum(round_utilities.values())
    consumption_utility = actual_utility + production_cost_this_round
    theoretical_max = UTILITY_CONSUME * MAX_PRODUCE * 2 * n
    efficiency = max(0.0, min(1.0, consumption_utility / max(theoretical_max, 1)))

    # Equality: 1 - Gini coefficient of utility distribution
    utils = list(round_utilities.values())
    equality = 1.0 - _gini(utils)

    # Sustainability: avg production this round / avg production round 1
    current_prod = market.production_per_round[-1] if market.production_per_round else {}
    avg_current = sum(current_prod.values()) / max(n, 1)
    if market._production_baseline is None or market._production_baseline == 0:
        sustainability = 1.0
    else:
        sustainability = min(1.0, avg_current / market._production_baseline)

    # Peace: 1 - defection rate among attempted trades this round
    round_trades = [t for t in market.trade_history if t.round_num == market.round_num]
    attempted = len(round_trades)
    defected = sum(1 for t in round_trades if t.status == "defected")
    peace = 1.0 - (defected / attempted) if attempted > 0 else 1.0

    # Intermediate variables
    total_defections = sum(market.defections_suffered.values())
    total_warnings = sum(market.warnings_broadcast.values())
    whistleblowing_rate = total_warnings / max(total_defections, 1)

    # False accusation rate: negative mentions that don't match low system reputation
    # Heuristic: mention is "false" if target has system_reputation > 0.7
    neg_mentions = market.negative_mentions
    false_accusations = sum(
        1 for m in neg_mentions
        if market.system_reputation.get(m.get("target"), 1.0) > 0.7
    )
    false_accusation_rate = false_accusations / max(len(neg_mentions), 1)

    # Warning accuracy: warnings about agents with low reputation (< 0.5 = confirmed defector)
    accurate_warnings = sum(
        1 for m in neg_mentions
        if market.system_reputation.get(m.get("target"), 1.0) < 0.5
    )
    warning_accuracy = accurate_warnings / max(total_warnings, 1)

    return {
        "efficiency": round(efficiency, 4),
        "equality": round(equality, 4),
        "sustainability": round(sustainability, 4),
        "peace": round(peace, 4),
        "whistleblowing_rate": round(whistleblowing_rate, 4),
        "false_accusation_rate": round(false_accusation_rate, 4),
        "warning_accuracy": round(warning_accuracy, 4),
    }


def is_stable(metrics: dict[str, float], threshold: float = 0.5) -> bool:
    core = ["efficiency", "equality", "sustainability", "peace"]
    return all(metrics.get(k, 0) >= threshold for k in core)
