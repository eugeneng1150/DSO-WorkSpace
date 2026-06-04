"""Judicial mechanism: complaint-driven enforcement with imperfect information."""
from __future__ import annotations
from .base import Mechanism
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..engine.market import Market
    from ..engine.agent import _BaseAgent


class JudicialMechanism(Mechanism):
    name = "judicial"

    async def on_session_start(self, market: "Market", agents: list["_BaseAgent"]) -> None:
        market.complaint_log = []

    def on_round_end(self, market: "Market", round_num: int) -> None:
        pass
