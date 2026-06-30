"""SAC-inspired trust filtering mechanism for hardened mediation.

Computes a deterministic trust score per agent each round using observed
trade behaviour (no LLM evaluation).  Identifies low-trust neighbours and
injects trust-aware guidance into agent prompts alongside mediation Stage 3.
"""
from __future__ import annotations
from .base import Mechanism
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..engine.market import Market
    from ..engine.agent import _BaseAgent


def compute_trust_scores(market: "Market") -> dict[int, float]:
    """Deterministic trust score for every agent based on observed behaviour.

    Components (all derived from market state, no LLM):
      base        = system_reputation (success / total trades, 1.0 if no trades)
      defection   = fraction of trades where this agent defected
      false_accus = fraction of this agent's warnings targeting high-rep agents (>0.7)
      mediation   = fraction of this agent's completed trades that were mediated
      rejection   = fraction of this agent's proposals that were rejected

    Formula:
      trust = base - 0.25*defection - 0.15*false_accusation + 0.10*mediation - 0.30*rejection
      clamped to [0, 1]
    """
    scores: dict[int, float] = {}
    for aid in market.agent_ids:
        base = market.system_reputation.get(aid, 1.0)

        # Defection rate: how often did this agent defect?
        trades_involving = [
            t for t in market.trade_history
            if (t.proposer_id == aid or t.target_id == aid)
            and t.status in ("completed", "defected", "mediated")
        ]
        n_trades = len(trades_involving)
        n_defected = sum(1 for t in trades_involving if t.defected_by == aid)
        defection_rate = n_defected / n_trades if n_trades > 0 else 0.0

        # False accusation rate: warnings sent by this agent targeting high-rep agents
        warnings_sent = [
            m for m in market.negative_mentions if m.get("sender") == aid
        ]
        n_warnings = len(warnings_sent)
        n_false = sum(
            1 for m in warnings_sent
            if market.system_reputation.get(m.get("target"), 1.0) > 0.7
        )
        false_accus_rate = n_false / n_warnings if n_warnings > 0 else 0.0

        # Mediation rate: fraction of completed trades that went through mediator
        completed = [
            t for t in trades_involving
            if t.status in ("completed", "mediated")
        ]
        n_mediated = sum(1 for t in completed if t.status == "mediated")
        mediation_rate = n_mediated / len(completed) if completed else 0.0

        # Rejection rate: fraction of proposals by this agent that were rejected
        all_proposals = [
            t for t in market.trade_history if t.proposer_id == aid
        ]
        n_proposals = len(all_proposals)
        n_rejected = sum(1 for t in all_proposals if t.status == "rejected")
        rejection_rate = n_rejected / n_proposals if n_proposals > 0 else 0.0

        trust = (
            base
            - 0.25 * defection_rate
            - 0.15 * false_accus_rate
            + 0.10 * mediation_rate
            - 0.30 * rejection_rate
        )
        scores[aid] = max(0.0, min(1.0, trust))

    return scores


def identify_low_trust(
    market: "Market",
    trust_scores: dict[int, float],
    agent_id: int,
) -> set[int]:
    """Return the set of low-trust neighbours for a given agent.

    Flags all neighbours whose trust score falls below
    median - 1*std of the full population's scores.
    """
    import numpy as np

    neighbours = market.network.get(agent_id, set())
    if not neighbours:
        return set()

    all_scores = list(trust_scores.values())
    if not all_scores:
        return set()

    median = float(np.median(all_scores))
    std = float(np.std(all_scores))
    threshold = median - std

    low_trust = {nid for nid in neighbours if trust_scores.get(nid, 1.0) < threshold}
    return low_trust


class SACMechanism(Mechanism):
    name = "sac"

    def on_round_start(self, market: "Market", round_num: int) -> None:
        """Compute trust scores and low-trust sets before agents act."""
        trust_scores = compute_trust_scores(market)
        market.sac_trust_scores = trust_scores

        troll_ids = set(getattr(market, "troll_ids", []))

        # Compute per-agent low-trust neighbour sets (only for honest agents)
        low_trust_map: dict[int, set[int]] = {}
        for aid in market.agent_ids:
            if aid in troll_ids:
                continue
            low_trust_map[aid] = identify_low_trust(market, trust_scores, aid)
        market.sac_low_trust = low_trust_map

        # Compute SAC-specific metrics for logging
        honest_ids = [a for a in market.agent_ids if a not in troll_ids]
        honest_scores = [trust_scores[a] for a in honest_ids if a in trust_scores]
        troll_scores = [trust_scores[a] for a in troll_ids if a in trust_scores]

        avg_honest_trust = sum(honest_scores) / len(honest_scores) if honest_scores else 0.0
        avg_troll_trust = sum(troll_scores) / len(troll_scores) if troll_scores else 0.0

        total_filtered = sum(len(s) for s in low_trust_map.values())
        avg_filtered = total_filtered / len(honest_ids) if honest_ids else 0.0

        # Trades involving at least one low-trust agent (from last round)
        all_low_trust_ids = set()
        for s in low_trust_map.values():
            all_low_trust_ids.update(s)

        last_round_trades = [
            t for t in market.trade_history if t.round_num == round_num - 1
        ]
        trades_with_low_trust = sum(
            1 for t in last_round_trades
            if t.proposer_id in all_low_trust_ids or t.target_id in all_low_trust_ids
        )
        frac_low_trust_trades = (
            trades_with_low_trust / len(last_round_trades)
            if last_round_trades else 0.0
        )

        # Delegation rate (mediated / total non-rejected trades, last round)
        non_rejected = [t for t in last_round_trades if t.status != "rejected"]
        mediated = [t for t in non_rejected if t.status == "mediated"]
        delegation_rate = len(mediated) / len(non_rejected) if non_rejected else 0.0

        # Defection rate after filtering (honest-only trades, last round)
        honest_trades = [
            t for t in last_round_trades
            if t.proposer_id not in troll_ids and t.target_id not in troll_ids
            and t.status in ("completed", "defected", "mediated")
        ]
        honest_defections = sum(1 for t in honest_trades if t.status == "defected")
        defection_rate = honest_defections / len(honest_trades) if honest_trades else 0.0

        log_entry = {
            "round": round_num,
            "trust_scores": {str(k): round(v, 4) for k, v in trust_scores.items()},
            "avg_honest_trust": round(avg_honest_trust, 4),
            "avg_troll_trust": round(avg_troll_trust, 4),
            "avg_filtered_per_agent": round(avg_filtered, 2),
            "frac_low_trust_trades": round(frac_low_trust_trades, 4),
            "delegation_rate": round(delegation_rate, 4),
            "defection_rate_honest": round(defection_rate, 4),
            "low_trust_map": {
                str(k): sorted(v) for k, v in low_trust_map.items()
            },
        }

        if not hasattr(market, "sac_log"):
            market.sac_log = []
        market.sac_log.append(log_entry)

    def get_stage_override(self, agent: "_BaseAgent", market: "Market") -> dict[str, str]:
        return {"sac": "1"}
