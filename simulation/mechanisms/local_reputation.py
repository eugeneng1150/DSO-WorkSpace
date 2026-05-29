"""Local reputation mechanism: gossip-based, no system-computed scores exposed to agents."""
from __future__ import annotations
from .base import Mechanism
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..engine.market import Market
    from ..engine.agent import _BaseAgent


class LocalReputationMechanism(Mechanism):
    name = "local_reputation"

    def on_round_end(self, market: "Market", round_num: int) -> None:
        pass

    def get_stage_override(self, agent: "_BaseAgent", market: "Market") -> dict[str, str]:
        return {}
