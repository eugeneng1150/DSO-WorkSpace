"""Network Rewiring mechanism: agents can sever and request trade links each round."""
from __future__ import annotations
from typing import TYPE_CHECKING

from .base import Mechanism

if TYPE_CHECKING:
    from ..engine.market import Market
    from ..engine.agent import _BaseAgent


class NetworkRewiringMechanism(Mechanism):
    name = "network_rewiring"

    async def on_session_start(self, market: Market, agents: list[_BaseAgent]) -> None:
        market.network_events = []
        market.network_degree_history = [{
            "round": 0,
            "degrees": {
                aid: len(neighbors)
                for aid, neighbors in market.network.items()
            },
        }]

    def on_round_end(self, market: Market, round_num: int) -> None:
        market.network_degree_history.append({
            "round": round_num,
            "degrees": {
                aid: len(neighbors)
                for aid, neighbors in market.network.items()
            },
        })

    def get_stage_override(self, agent, market) -> dict[str, str]:
        return {}
