"""Reputation mechanism: exposes engine-tracked system scores to all agents."""
from __future__ import annotations
from .base import Mechanism
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..engine.market import Market
    from ..engine.agent import _BaseAgent


class ReputationMechanism(Mechanism):
    name = "reputation"

    def on_round_end(self, market: "Market", round_num: int) -> None:
        # Reputation scores are updated in market.record_trade_outcome() as trades complete.
        # Nothing extra needed here — scores are already in market.system_reputation.
        pass

    def get_stage_override(self, agent: "_BaseAgent", market: "Market") -> dict[str, str]:
        # Reputation has a single block (no stages); stage_override not needed.
        return {}
