"""Governance mechanism: external deterministic Oracle + Controller state machine."""
from __future__ import annotations
from collections import defaultdict
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from .base import Mechanism
from ..config import (
    GOV_ORACLE_WINDOW, GOV_DEFECTION_THRESHOLD, GOV_PRODUCTION_THRESHOLD,
    GOV_PRODUCTION_CONSEC, GOV_TRADE_VOLUME_MIN, GOV_PREDATORY_THRESHOLD,
    GOV_FINE_SCHEDULE, GOV_SUSPENSION_DURATION, GOV_WARNING_EXPIRY,
    GOV_CLEAN_ROUNDS_TO_DEESCALATE,
)

if TYPE_CHECKING:
    from ..engine.market import Market
    from ..engine.agent import _BaseAgent


@dataclass
class GovernanceState:
    agent_id: int
    status: str = "active"
    fine_tier: int = 0
    suspension_rounds_left: int = 0
    clean_rounds: int = 0
    grace_until_round: int = 0
    triggered_signals: list[str] = field(default_factory=list)


class Oracle:
    """Deterministic signal detector — no LLM calls."""

    def evaluate(self, agent_id: int, market: "Market", round_num: int) -> list[str]:
        fired = []
        if self._check_defection_rate(agent_id, market, round_num):
            fired.append("D1_defection_rate")
        if self._check_production_withdrawal(agent_id, market, round_num):
            fired.append("D2_production_withdrawal")
        if self._check_trade_volume_collapse(agent_id, market, round_num):
            fired.append("D3_trade_volume_collapse")
        if self._check_predatory_targeting(agent_id, market, round_num):
            fired.append("D4_predatory_targeting")
        return fired

    def _recent_trades(self, agent_id: int, market: "Market", round_num: int):
        lo = round_num - GOV_ORACLE_WINDOW + 1
        return [
            t for t in market.trade_history
            if t.round_num >= lo
            and (t.proposer_id == agent_id or t.target_id == agent_id)
        ]

    def _check_defection_rate(self, agent_id: int, market: "Market", round_num: int) -> bool:
        trades = self._recent_trades(agent_id, market, round_num)
        if len(trades) < 2:
            return False
        defections = sum(1 for t in trades if t.defected_by == agent_id)
        return defections / len(trades) > GOV_DEFECTION_THRESHOLD

    def _check_production_withdrawal(self, agent_id: int, market: "Market", round_num: int) -> bool:
        if market._production_baseline is None or market._production_baseline == 0:
            return False
        per_agent_baseline = market._production_baseline
        threshold = per_agent_baseline * GOV_PRODUCTION_THRESHOLD

        history = market.production_per_round
        if len(history) < GOV_PRODUCTION_CONSEC:
            return False
        recent = history[-GOV_PRODUCTION_CONSEC:]
        return all(r.get(agent_id, 0) < threshold for r in recent)

    def _check_trade_volume_collapse(self, agent_id: int, market: "Market", round_num: int) -> bool:
        if round_num < GOV_ORACLE_WINDOW:
            return False
        trades = self._recent_trades(agent_id, market, round_num)
        completed = [t for t in trades if t.status in ("completed", "mediated")]
        return len(completed) < GOV_TRADE_VOLUME_MIN

    def _check_predatory_targeting(self, agent_id: int, market: "Market", round_num: int) -> bool:
        trades = self._recent_trades(agent_id, market, round_num)
        victim_counts: dict[int, int] = defaultdict(int)
        for t in trades:
            if t.defected_by == agent_id:
                victim = t.target_id if t.proposer_id == agent_id else t.proposer_id
                victim_counts[victim] += 1
        return any(c >= GOV_PREDATORY_THRESHOLD for c in victim_counts.values())


class GovernanceController:
    """State machine: advances each agent's governance state by one round."""

    def __init__(self):
        self.oracle = Oracle()

    def step(self, state: GovernanceState, market: "Market", round_num: int) -> int:
        """Advance state by one round. Returns fine amount for this round."""
        state.triggered_signals = []

        if state.status == "suspended":
            state.suspension_rounds_left -= 1
            if state.suspension_rounds_left <= 0:
                state.status = "active"
                state.fine_tier = 0
                state.clean_rounds = 0
                state.grace_until_round = round_num + GOV_ORACLE_WINDOW
            return 0

        if round_num < state.grace_until_round:
            state.clean_rounds += 1
            return 0

        signals = self.oracle.evaluate(state.agent_id, market, round_num)
        state.triggered_signals = signals
        has_violation = len(signals) > 0

        if has_violation:
            state.clean_rounds = 0
        else:
            state.clean_rounds += 1

        if state.status == "active":
            if has_violation:
                state.status = "warning"

        elif state.status == "warning":
            if has_violation:
                state.status = "fined"
                state.fine_tier = 1
            elif state.clean_rounds >= GOV_WARNING_EXPIRY:
                state.status = "active"

        elif state.status == "fined":
            if has_violation:
                if state.fine_tier >= 3:
                    state.status = "suspended"
                    state.suspension_rounds_left = GOV_SUSPENSION_DURATION
                    return 0
                state.fine_tier = min(3, state.fine_tier + 1)
            elif state.clean_rounds >= GOV_CLEAN_ROUNDS_TO_DEESCALATE:
                state.fine_tier -= 1
                state.clean_rounds = 0
                if state.fine_tier <= 0:
                    state.fine_tier = 0
                    state.status = "active"
                    return 0

        return GOV_FINE_SCHEDULE.get(state.fine_tier, 0)


class GovernanceMechanism(Mechanism):
    name = "governance"

    def __init__(self):
        self.controller = GovernanceController()

    async def on_session_start(self, market: "Market", agents: list["_BaseAgent"]) -> None:
        market.governance_states = {
            a.agent_id: GovernanceState(agent_id=a.agent_id)
            for a in agents
        }
        market.governance_log = []

    def on_round_start(self, market: "Market", round_num: int) -> None:
        round_events = {}
        for agent_id, state in market.governance_states.items():
            old_status = state.status
            fine_amount = self.controller.step(state, market, round_num)

            if fine_amount > 0:
                market._penalty_ledger[agent_id] = (
                    market._penalty_ledger.get(agent_id, 0) + fine_amount
                )

            round_events[agent_id] = {
                "old_status": old_status,
                "new_status": state.status,
                "fine_tier": state.fine_tier,
                "fine_amount": fine_amount,
                "signals": list(state.triggered_signals),
                "clean_rounds": state.clean_rounds,
                "suspension_rounds_left": state.suspension_rounds_left,
            }

        market.governance_log.append({"round": round_num, "events": round_events})

    def get_stage_override(self, agent: "_BaseAgent", market: "Market") -> dict[str, str]:
        return {}
