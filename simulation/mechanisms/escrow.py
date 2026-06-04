"""Escrow mechanism: shared insurance pool that compensates defection victims.

Pool starts at ESCROW_POOL_INITIAL. Each defection pays the victim ESCROW_PAYOUT
from the pool. When the pool hits 0, all agents' total utility is reset to 0.
"""
from __future__ import annotations
from .base import Mechanism
from ..config import ESCROW_POOL_INITIAL, ESCROW_PAYOUT
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..engine.market import Market
    from ..engine.agent import _BaseAgent


class EscrowMechanism(Mechanism):
    name = "escrow"

    async def on_session_start(self, market: "Market", agents: list["_BaseAgent"]) -> None:
        market.escrow_pool = ESCROW_POOL_INITIAL
        market.escrow_log = []
        market.escrow_collapsed = False
        market._escrow_agents = agents

    def on_round_end(self, market: "Market", round_num: int) -> None:
        if market.escrow_collapsed:
            return

        for trade in market.trade_history:
            if trade.round_num != round_num:
                continue
            if trade.status == "defected" and trade.defected_by is not None:
                defector = trade.defected_by
                victim = (trade.proposer_id if defector == trade.target_id
                          else trade.target_id)

                payout = min(ESCROW_PAYOUT, market.escrow_pool)
                market.escrow_pool -= payout
                if payout > 0:
                    market._penalty_ledger[victim] = (
                        market._penalty_ledger.get(victim, 0) - payout
                    )

                market.escrow_log.append({
                    "round": round_num,
                    "trade_id": trade.trade_id,
                    "defector": defector,
                    "victim": victim,
                    "payout": payout,
                    "pool_remaining": market.escrow_pool,
                })

        if market.escrow_pool <= 0 and not market.escrow_collapsed:
            market.escrow_collapsed = True
            for agent in market._escrow_agents:
                agent.total_utility = 0
            market.escrow_log.append({
                "round": round_num,
                "event": "POOL_COLLAPSED",
                "pool_remaining": 0,
            })
