"""Compute marketplace cooperation metrics per round from market state."""
from __future__ import annotations
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..engine.market import Market


def _gini(values: list[float]) -> float:
    """Compute Gini coefficient. Shifts values to non-negative if needed."""
    if not values or len(values) < 2:
        return 0.0
    min_val = min(values)
    if min_val < 0:
        values = [v - min_val for v in values]
    total = sum(values)
    if total == 0:
        return 0.0
    n = len(values)
    sorted_vals = sorted(values)
    cumsum = 0.0
    for i, v in enumerate(sorted_vals):
        cumsum += (2 * (i + 1) - n - 1) * v
    return cumsum / (n * total)


def compute_metrics(market: "Market", round_utilities: dict[int, float]) -> dict[str, float]:
    """
    round_utilities: {agent_id: utility_this_round}
    Returns dict with sustainability, peace, gini + intermediate variables.
    Troll agents are excluded from all metrics to avoid skewing results.
    """
    troll_ids = set(getattr(market, "troll_ids", []))
    agent_ids = [a for a in market.agent_ids if a not in troll_ids]
    n = len(agent_ids)

    # Sustainability: avg production this round / avg production round 1 (trolls excluded)
    current_prod = market.production_per_round[-1] if market.production_per_round else {}
    non_troll_prod = {k: v for k, v in current_prod.items() if k not in troll_ids}
    avg_current = sum(non_troll_prod.values()) / max(n, 1)
    if market._production_baseline is None or market._production_baseline == 0:
        sustainability = 1.0
    else:
        sustainability = min(1.0, avg_current / market._production_baseline)

    # Peace (cooperation rate): 1 - defection rate (exclude troll trades)
    non_troll_trades = [t for t in market.trade_history if t.proposer_id not in troll_ids and t.target_id not in troll_ids]
    attempted = len(non_troll_trades)
    defected = sum(1 for t in non_troll_trades if t.status == "defected")
    peace = 1.0 - (defected / attempted) if attempted > 0 else 1.0

    # Gini coefficient on per-round utilities (trolls excluded)
    non_troll_utils = [round_utilities[a] for a in agent_ids if a in round_utilities]
    gini = _gini(non_troll_utils)

    # Intermediate variables (exclude trolls)
    total_defections = sum(v for k, v in market.defections_suffered.items() if k not in troll_ids)
    total_warnings = sum(v for k, v in market.warnings_broadcast.items() if k not in troll_ids)
    whistleblowing_rate = total_warnings / max(total_defections, 1)

    neg_mentions = [m for m in market.negative_mentions if m.get("sender") not in troll_ids]
    false_accusations = sum(
        1 for m in neg_mentions
        if market.system_reputation.get(m.get("target"), 1.0) > 0.7
    )
    false_accusation_rate = false_accusations / max(len(neg_mentions), 1)

    accurate_warnings = sum(
        1 for m in neg_mentions
        if market.system_reputation.get(m.get("target"), 1.0) < 0.5
    )
    warning_accuracy = accurate_warnings / max(total_warnings, 1)

    return {
        "sustainability": round(sustainability, 4),
        "peace": round(peace, 4),
        "gini": round(gini, 4),
        "whistleblowing_rate": round(whistleblowing_rate, 4),
        "false_accusation_rate": round(false_accusation_rate, 4),
        "warning_accuracy": round(warning_accuracy, 4),
    }


