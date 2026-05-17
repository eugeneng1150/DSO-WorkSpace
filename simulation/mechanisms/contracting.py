"""Contracting mechanism: proposal → sign/reject → enforcement on breach."""
from __future__ import annotations
import asyncio
from .base import Mechanism
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..engine.market import Market, Contract
    from ..engine.agent import _BaseAgent


class ContractingMechanism(Mechanism):
    name = "contracting"

    def on_communication_phase(self, market: "Market", agents: list["_BaseAgent"]) -> None:
        # Proposal and signing are handled by the engine parsing agent action outputs.
        # This hook is a no-op; the engine calls agents with stage=1 then stage=2 prompts.
        pass

    def on_round_end(self, market: "Market", round_num: int) -> None:
        """Enforce all contracts due this round: detect breaches, transfer penalties."""
        for contract in market.contracts.values():
            if contract.status != "signed" or contract.execution_round != round_num:
                continue

            proposer_inv = market.inventories[contract.proposer_id]
            counterparty_inv = market.inventories[contract.counterparty_id]

            proposer_breached = proposer_inv.get(contract.proposer_delivers_good, 0) < contract.proposer_delivers_qty
            counterparty_breached = counterparty_inv.get(contract.counterparty_delivers_good, 0) < contract.counterparty_delivers_qty

            if proposer_breached:
                self._apply_breach(market, contract.proposer_id, contract.counterparty_id, contract.breach_penalty)
                contract.status = "breached"
            elif counterparty_breached:
                self._apply_breach(market, contract.counterparty_id, contract.proposer_id, contract.breach_penalty)
                contract.status = "breached"
            else:
                # Both can deliver — execute the exchange
                market.transfer_goods(
                    contract.proposer_id, contract.counterparty_id,
                    contract.proposer_delivers_good, contract.proposer_delivers_qty
                )
                market.transfer_goods(
                    contract.counterparty_id, contract.proposer_id,
                    contract.counterparty_delivers_good, contract.counterparty_delivers_qty
                )
                contract.status = "executed"

    def _apply_breach(self, market: "Market", breacher_id: int, victim_id: int, penalty: int) -> None:
        # Penalty deducted from breacher's next-round utility (tracked as a debt)
        # Simple implementation: add to a penalty ledger on the market
        if not hasattr(market, "_penalty_ledger"):
            market._penalty_ledger = {}
        market._penalty_ledger[breacher_id] = (
            market._penalty_ledger.get(breacher_id, 0) + penalty
        )
        market._penalty_ledger[victim_id] = (
            market._penalty_ledger.get(victim_id, 0) - penalty
        )
        market._update_reputation(breacher_id, success=False)

    def get_stage_override(self, agent: "_BaseAgent", market: "Market") -> dict[str, str]:
        aid = agent.agent_id
        # Stage 2: agent has a pending contract proposal to review
        has_pending = any(
            c.counterparty_id == aid and c.status == "proposed"
            for c in market.contracts.values()
        )
        if has_pending:
            return {"contracting": "2"}

        # Stage 3: agent has a signed active contract this round
        has_active = any(
            (c.proposer_id == aid or c.counterparty_id == aid)
            and c.status == "signed"
            and c.execution_round == market.round_num
            for c in market.contracts.values()
        )
        if has_active:
            return {"contracting": "3"}

        # Stage 4: agent's proposal was rejected
        has_rejected = any(
            c.proposer_id == aid and c.status == "rejected"
            and c.execution_round == market.round_num
            for c in market.contracts.values()
        )
        if has_rejected:
            return {"contracting": "4"}

        # Stage 1: default — proposal phase
        return {"contracting": "1"}
