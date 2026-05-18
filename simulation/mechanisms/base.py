"""Abstract Mechanism class. Each mechanism hooks into the engine at specific phases."""
from __future__ import annotations
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..engine.market import Market
    from ..engine.agent import _BaseAgent


class Mechanism(ABC):
    name: str = ""

    async def on_session_start(self, market: "Market", agents: list["_BaseAgent"]) -> None:
        """Called once before Round 1. Used by Mediation for design/vote phase."""

    def on_round_start(self, market: "Market", round_num: int) -> None:
        """Called at the start of each round before any agent actions."""

    def on_communication_phase(self, market: "Market", agents: list["_BaseAgent"]) -> None:
        """Called during communication phase. Used by Contracting for proposal stage."""

    def on_trade_phase(self, market: "Market", agents: list["_BaseAgent"]) -> None:
        """Called during trade phase for mechanism-specific enforcement."""

    def on_round_end(self, market: "Market", round_num: int) -> None:
        """Called after consumption. Used for contract enforcement, reputation updates."""

    def get_stage_override(self, agent: "_BaseAgent", market: "Market") -> dict[str, str]:
        """Return {mechanism_name: stage_label} so prompt_builder picks the right stage."""
        return {}
