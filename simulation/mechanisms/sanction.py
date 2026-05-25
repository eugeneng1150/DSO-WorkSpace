"""Sanction mechanism: agents can spend utility to punish others (1:3 cost ratio)."""
from __future__ import annotations
from .base import Mechanism
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..engine.market import Market
    from ..engine.agent import _BaseAgent


class SanctionMechanism(Mechanism):
    name = "sanction"

    async def on_session_start(self, market: "Market", agents: list["_BaseAgent"]) -> None:
        market.sanction_log = []

    def on_round_end(self, market: "Market", round_num: int) -> None:
        pass

    def get_stage_override(self, agent: "_BaseAgent", market: "Market") -> dict[str, str]:
        return {}
