"""Main simulation loop: 5 phases per round."""
from __future__ import annotations
import asyncio
import json
from typing import TYPE_CHECKING

from .market import Market, Message, TradeOffer, Contract
from .prompt_builder import build_prompt
from ..metrics.social import compute_metrics
from ..config import (
    GOODS, ROUNDS, UTILITY_CONSUME, COST_PRODUCE, MEDIATION_FEE,
    DEFAULT_BREACH_PENALTY, MEMORY_WINDOW,
)

if TYPE_CHECKING:
    from .agent import _BaseAgent
    from ..mechanisms.base import Mechanism


class Game:
    def __init__(
        self,
        agents: list["_BaseAgent"],
        mechanisms: list["Mechanism"],
        condition_label: str,
        run_idx: int,
    ):
        self.agents = agents
        self.mechanisms = mechanisms
        self.condition_label = condition_label
        self.run_idx = run_idx
        self.mechanism_names = [m.name for m in mechanisms]

        agent_ids = [a.agent_id for a in agents]
        self.market = Market(agent_ids=agent_ids, goods=GOODS)

        self.round_logs: list[dict] = []
        self.trace_log: list[dict] = []
        self._utility_history: dict[int, list[float]] = {a.agent_id: [] for a in agents}

    def run(self) -> list[dict]:
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self._run_async())

    async def _run_async(self) -> list[dict]:
        # Session start hooks (e.g. mediation design/vote)
        for mech in self.mechanisms:
            mech.on_session_start(self.market, self.agents)

        for round_num in range(1, ROUNDS + 1):
            self.market.new_round(round_num)
            for mech in self.mechanisms:
                mech.on_round_start(self.market, round_num)

            round_utilities = await self._run_round(round_num)

            # Set production baseline after round 1
            if round_num == 1:
                prod = self.market.production_per_round[-1] if self.market.production_per_round else {}
                n = len(self.agents)
                self.market._production_baseline = sum(prod.values()) / max(n, 1)

            metrics = compute_metrics(self.market, round_utilities)
            self.market.metrics_log.append({"round": round_num, **metrics})

            for mech in self.mechanisms:
                mech.on_round_end(self.market, round_num)

            private_messages = [
                {"sender": m.sender_id, "recipient": m.recipient_id, "text": m.text}
                for inbox in self.market.private_inboxes.values()
                for m in inbox
            ]
            public_messages = [
                {"sender": m.sender_id, "text": m.text}
                for m in self.market.public_feed
            ]

            self.round_logs.append({
                "round": round_num,
                "metrics": metrics,
                "utilities": round_utilities,
                "trade_count": len([t for t in self.market.trade_history if t.round_num == round_num]),
                "defections": sum(
                    1 for t in self.market.trade_history
                    if t.round_num == round_num and t.status == "defected"
                ),
                "production": dict(self.market.production_per_round[-1]) if self.market.production_per_round else {},
                "private_messages": private_messages,
                "public_messages": public_messages,
            })

        return self.round_logs

    async def _run_round(self, round_num: int) -> dict[int, float]:
        """Execute all 5 phases. Returns {agent_id: utility_this_round}."""

        # --- Phase 1: Production ---
        production_actions = await self._call_agents_phase("production", round_num)
        production_this_round: dict[int, int] = {}
        for agent in self.agents:
            actions = production_actions.get(agent.agent_id, [])
            units = 0
            for act in actions:
                if act.get("action") == "produce" and act.get("good") == agent.specialty:
                    qty = min(int(act.get("quantity", 0)), 5)
                    self.market.inventories[agent.agent_id][agent.specialty] += qty
                    units += qty
            production_this_round[agent.agent_id] = units
        self.market.production_per_round.append(production_this_round)

        # --- Phase 2: Communication + Contract Proposals ---
        comm_actions = await self._call_agents_phase("communication", round_num)
        for agent in self.agents:
            actions = comm_actions.get(agent.agent_id, [])
            self._process_messages(agent.agent_id, actions, round_num)
            self._process_trade_proposals(agent.agent_id, actions, round_num)
            if "contracting" in self.mechanism_names:
                self._process_contract_proposals(agent.agent_id, actions, round_num)

        # Contract review stage: agents that received proposals respond
        if "contracting" in self.mechanism_names:
            review_actions = await self._call_agents_phase("contract_review", round_num)
            for agent in self.agents:
                actions = review_actions.get(agent.agent_id, [])
                self._process_contract_signing(agent.agent_id, actions)

        # --- Phase 3: Trade ---
        trade_actions = await self._call_agents_phase("trade", round_num)
        for agent in self.agents:
            actions = trade_actions.get(agent.agent_id, [])
            self._process_trade_decisions(agent.agent_id, actions, round_num)

        # Contracting enforcement happens in on_round_end
        if "contracting" in self.mechanism_names:
            from ..mechanisms.contracting import ContractingMechanism
            for mech in self.mechanisms:
                if isinstance(mech, ContractingMechanism):
                    mech.on_round_end(self.market, round_num)

        # --- Phase 4: Consumption ---
        round_utilities: dict[int, float] = {}
        for agent in self.agents:
            consumed_utility = 0.0
            inv = self.market.inventories[agent.agent_id]
            for need in agent.needs:
                qty = inv.get(need, 0)
                consumed_utility += qty * UTILITY_CONSUME
                inv[need] = 0  # consume all held units of needed goods

            # Deduct production costs
            prod_cost = production_this_round.get(agent.agent_id, 0) * COST_PRODUCE
            consumed_utility -= prod_cost

            # Apply contract breach penalties
            if hasattr(self.market, "_penalty_ledger"):
                penalty = self.market._penalty_ledger.pop(agent.agent_id, 0)
                consumed_utility -= penalty

            round_utilities[agent.agent_id] = consumed_utility
            agent.last_utility = consumed_utility
            agent.total_utility += consumed_utility
            self._utility_history[agent.agent_id].append(consumed_utility)

        return round_utilities

    async def _call_agents_phase(self, phase: str, round_num: int) -> dict[int, list[dict]]:
        """Build prompts for all agents and call them concurrently."""
        prompts = {}
        for agent in self.agents:
            stage_overrides = {}
            for mech in self.mechanisms:
                stage_overrides.update(mech.get_stage_override(agent, self.market))

            # Skip contract review if agent has no pending proposals
            if phase == "contract_review":
                has_pending = any(
                    c.counterparty_id == agent.agent_id and c.status == "proposed"
                    for c in self.market.contracts.values()
                )
                if not has_pending:
                    continue

            metrics = self.market.metrics_log[-1] if self.market.metrics_log else {
                "efficiency": 1.0, "equality": 1.0, "sustainability": 1.0, "peace": 1.0
            }

            prompt = build_prompt(
                agent_id=agent.agent_id,
                specialty=agent.specialty,
                needs=agent.needs,
                last_utility=agent.last_utility,
                total_utility=agent.total_utility,
                metrics=metrics,
                market=self.market,
                mechanisms=self.mechanism_names,
                stage_overrides=stage_overrides,
            )
            prompts[agent.agent_id] = (agent, prompt)

        async def _staggered_call(agent, prompt, delay):
            await asyncio.sleep(delay)
            return await agent.call(prompt)

        results = await asyncio.gather(*[
            _staggered_call(agent, prompt, i * 0.1)
            for i, (agent, prompt) in enumerate(prompts.values())
        ])

        for agent_id, (agent, _) in prompts.items():
            if agent.last_raw_response:
                self.trace_log.append({
                    "round": round_num,
                    "phase": phase,
                    "agent_id": agent_id,
                    "agent_type": type(agent).__name__,
                    "specialty": agent.specialty,
                    "reasoning": agent.last_raw_response,
                })

        return {
            agent_id: actions
            for (agent_id, (_, __)), actions in zip(prompts.items(), results)
        }

    def _process_messages(self, sender_id: int, actions: list[dict], round_num: int) -> None:
        for act in actions:
            if act.get("action") == "send_private":
                try:
                    target = int(act["target"])
                    self.market.post_message(Message(
                        sender_id=sender_id, text=act.get("text", ""),
                        round_num=round_num, channel="private", recipient_id=target
                    ))
                except (KeyError, ValueError):
                    pass
            elif act.get("action") == "send_public":
                self.market.post_message(Message(
                    sender_id=sender_id, text=act.get("text", ""),
                    round_num=round_num, channel="public"
                ))

    def _process_trade_proposals(self, proposer_id: int, actions: list[dict], round_num: int) -> None:
        for act in actions:
            if act.get("action") == "propose_trade":
                try:
                    target = int(act["target"])
                    offer = act["offer"]
                    request = act["request"]
                    trade = TradeOffer(
                        trade_id=self.market.new_trade_id(),
                        proposer_id=proposer_id,
                        target_id=target,
                        offer_good=offer["good"],
                        offer_qty=int(offer["quantity"]),
                        request_good=request["good"],
                        request_qty=int(request["quantity"]),
                        round_num=round_num,
                    )
                    self.market.post_trade_offer(trade)
                except (KeyError, ValueError, TypeError):
                    pass

    def _process_contract_proposals(self, proposer_id: int, actions: list[dict], round_num: int) -> None:
        for act in actions:
            if act.get("action") == "propose_contract":
                try:
                    target = int(act["target"])
                    terms = act["terms"]
                    contract = Contract(
                        contract_id=self.market.new_contract_id(),
                        proposer_id=proposer_id,
                        counterparty_id=target,
                        proposer_delivers_good=terms["i_deliver"]["good"],
                        proposer_delivers_qty=int(terms["i_deliver"]["quantity"]),
                        counterparty_delivers_good=terms["they_deliver"]["good"],
                        counterparty_delivers_qty=int(terms["they_deliver"]["quantity"]),
                        breach_penalty=int(terms.get("breach_penalty", DEFAULT_BREACH_PENALTY)),
                        execution_round=int(terms.get("execution_round", round_num)),
                    )
                    self.market.contracts[contract.contract_id] = contract
                    # Notify counterparty via private channel
                    self.market.post_message(Message(
                        sender_id=proposer_id,
                        text=f"CONTRACT PROPOSAL {contract.contract_id}: I deliver "
                             f"{contract.proposer_delivers_qty}×{contract.proposer_delivers_good}, "
                             f"you deliver {contract.counterparty_delivers_qty}×"
                             f"{contract.counterparty_delivers_good}. "
                             f"Penalty: {contract.breach_penalty}. Round: {contract.execution_round}.",
                        round_num=round_num, channel="private", recipient_id=target
                    ))
                except (KeyError, ValueError, TypeError):
                    pass

    def _process_contract_signing(self, agent_id: int, actions: list[dict]) -> None:
        for act in actions:
            cid = act.get("contract_id")
            if not cid or cid not in self.market.contracts:
                continue
            contract = self.market.contracts[cid]
            if contract.counterparty_id != agent_id:
                continue
            if act.get("action") == "sign_contract":
                contract.status = "signed"
            elif act.get("action") == "reject_contract":
                contract.status = "rejected"

    def _process_trade_decisions(self, agent_id: int, actions: list[dict], round_num: int) -> None:
        for act in actions:
            action_type = act.get("action")
            trade_id = act.get("trade_id")
            if not trade_id:
                continue

            # Find the trade in pending offers for this agent
            offer = next(
                (o for o in self.market.pending_offers.get(agent_id, []) if o.trade_id == trade_id),
                None,
            )
            if offer is None:
                continue

            if action_type == "reject_trade":
                offer.status = "rejected"

            elif action_type in ("accept_trade", "delegate_to_mediator"):
                delegated = action_type == "delegate_to_mediator"
                # Check if proposer also delegated (both must delegate for guarantee)
                proposer_delegated = getattr(offer, "_proposer_delegated", False)

                if delegated and proposer_delegated and self.market.active_mediator:
                    # Mediated simultaneous exchange
                    self._execute_mediated_trade(offer, round_num)
                else:
                    # Standard trade: proposer delivers first, target may defect
                    self._execute_standard_trade(offer, agent_id, defect=False, round_num=round_num)
                    if delegated:
                        # Deduct mediation fee
                        # Applied at consumption via utility adjustment
                        if not hasattr(self.market, "_penalty_ledger"):
                            self.market._penalty_ledger = {}
                        self.market._penalty_ledger[agent_id] = (
                            self.market._penalty_ledger.get(agent_id, 0) + MEDIATION_FEE
                        )

            elif action_type == "defect_trade":
                self._execute_standard_trade(offer, agent_id, defect=True, round_num=round_num)

    def _execute_standard_trade(
        self, offer: TradeOffer, accepting_agent: int, defect: bool, round_num: int
    ) -> None:
        if defect:
            # Accepting agent takes proposer's goods but doesn't deliver
            transferred = self.market.transfer_goods(
                offer.proposer_id, accepting_agent, offer.offer_good, offer.offer_qty
            )
            if transferred:
                self.market.record_trade_outcome(offer, defected_by=accepting_agent)
        else:
            ok1 = self.market.transfer_goods(
                offer.proposer_id, accepting_agent, offer.offer_good, offer.offer_qty
            )
            ok2 = self.market.transfer_goods(
                accepting_agent, offer.proposer_id, offer.request_good, offer.request_qty
            )
            if ok1 and ok2:
                self.market.record_trade_outcome(offer)
            else:
                self.market.record_trade_outcome(offer, defected_by=accepting_agent if not ok2 else offer.proposer_id)

    def _execute_mediated_trade(self, offer: TradeOffer, round_num: int) -> None:
        active = self.market.active_mediator
        if active.action_both == "execute_fair":
            ok1 = self.market.transfer_goods(
                offer.proposer_id, offer.target_id, offer.offer_good, offer.offer_qty
            )
            ok2 = self.market.transfer_goods(
                offer.target_id, offer.proposer_id, offer.request_good, offer.request_qty
            )
            offer.status = "mediated" if (ok1 and ok2) else "defected"
        elif active.action_both == "cancel":
            offer.status = "rejected"
        self.market.trade_history.append(offer)
        # Deduct mediation fee from both parties
        if not hasattr(self.market, "_penalty_ledger"):
            self.market._penalty_ledger = {}
        for aid in [offer.proposer_id, offer.target_id]:
            self.market._penalty_ledger[aid] = (
                self.market._penalty_ledger.get(aid, 0) + MEDIATION_FEE
            )
