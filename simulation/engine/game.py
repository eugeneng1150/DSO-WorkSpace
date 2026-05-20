"""Main simulation loop: 5 phases per round."""
from __future__ import annotations
import asyncio
import json
from typing import TYPE_CHECKING
from tqdm import tqdm

from .market import Market, Message, TradeOffer, Contract, generate_network
from .prompt_builder import build_prompt
from ..metrics.social import compute_metrics
from ..config import (
    GOODS, ROUNDS, UTILITY_CONSUME, COST_PRODUCE, MEDIATION_FEE,
    DEFAULT_BREACH_PENALTY, MEMORY_WINDOW, MIN_NEIGHBORS, MAX_NEIGHBORS,
    ROUND_INCOME, SPOILAGE_RATE,
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
        self.specialties = {a.agent_id: a.specialty for a in agents}
        network = generate_network(agent_ids, self.specialties, MIN_NEIGHBORS, MAX_NEIGHBORS)
        self.market = Market(agent_ids=agent_ids, goods=GOODS, network=network)

        self.round_logs: list[dict] = []
        self.trace_log: list[dict] = []
        self.session_log: dict = {
            "network": {str(k): sorted(v) for k, v in self.market.network.items()},
            "specialties": {str(k): v for k, v in self.specialties.items()},
        }
        self._utility_history: dict[int, list[float]] = {a.agent_id: [] for a in agents}

    def run(self) -> list[dict]:
        loop = asyncio.get_event_loop()
        return loop.run_until_complete(self._run_async())

    async def _run_async(self) -> list[dict]:
        # Session start hooks (e.g. mediation design/vote)
        for mech in self.mechanisms:
            await mech.on_session_start(self.market, self.agents)

        # Capture one-time session state after setup
        if self.market.mediator_designs:
            approval_counts: dict[int, int] = {}
            for approved_ids in self.market.mediation_votes.values():
                for did in approved_ids:
                    approval_counts[did] = approval_counts.get(did, 0) + 1
            self.session_log["mediator_designs"] = [
                {
                    "designer_id": d.designer_id,
                    "action_both": d.action_both,
                    "action_one": d.action_one,
                    "rationale": d.rationale,
                    "approval_votes": approval_counts.get(d.designer_id, 0),
                }
                for d in self.market.mediator_designs
            ]
            self.session_log["mediation_votes"] = {
                str(voter): approved
                for voter, approved in self.market.mediation_votes.items()
            }
            if self.market.active_mediator:
                m = self.market.active_mediator
                self.session_log["elected_mediator"] = {
                    "designer_id": m.designer_id,
                    "action_both": m.action_both,
                    "action_one": m.action_one,
                    "rationale": m.rationale,
                    "approval_votes": approval_counts.get(m.designer_id, 0),
                }

        pbar = tqdm(range(1, ROUNDS + 1), desc=f"[{self.condition_label}] Run {self.run_idx}", unit="round", leave=True)
        for round_num in pbar:
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
            pbar.set_postfix(sust=f"{metrics['sustainability']:.2f}", peace=f"{metrics['peace']:.2f}")

            for mech in self.mechanisms:
                if mech.name == "contracting":
                    continue  # already enforced in Phase 3b inside _run_round
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

            round_trades = [t for t in self.market.trade_history if t.round_num == round_num]

            # Reputation deltas vs previous round
            prev_rep = self.round_logs[-1]["reputation"] if self.round_logs else {}
            reputation_now = {
                str(aid): round(score, 4)
                for aid, score in self.market.system_reputation.items()
            }
            reputation_delta = {
                aid: round(reputation_now[aid] - prev_rep.get(aid, reputation_now[aid]), 4)
                for aid in reputation_now
            }

            # Contracting: split contracts by status and what happened this round
            def _fmt_contract(c) -> dict:
                return {
                    "contract_id": c.contract_id,
                    "proposer": c.proposer_id,
                    "counterparty": c.counterparty_id,
                    "proposer_delivers": {"good": c.proposer_delivers_good, "qty": c.proposer_delivers_qty},
                    "counterparty_delivers": {"good": c.counterparty_delivers_good, "qty": c.counterparty_delivers_qty},
                    "breach_penalty": c.breach_penalty,
                    "execution_round": c.execution_round,
                    "status": c.status,
                }

            all_contracts = list(self.market.contracts.values())
            contracts_proposed  = [_fmt_contract(c) for c in all_contracts if c.status == "proposed"]
            contracts_active    = [_fmt_contract(c) for c in all_contracts if c.status == "signed"]
            contracts_executed  = [_fmt_contract(c) for c in all_contracts if c.status == "executed" and c.execution_round == round_num]
            contracts_breached  = [_fmt_contract(c) for c in all_contracts if c.status == "breached" and c.execution_round == round_num]
            contracts_rejected  = [_fmt_contract(c) for c in all_contracts if c.status == "rejected"]
            penalty_ledger      = dict(getattr(self.market, "_penalty_ledger", {}))

            # Mediation: active mediator config + trade outcomes
            active_med = self.market.active_mediator
            mediated_trades = [t for t in round_trades if t.status == "mediated"]

            self.round_logs.append({
                "round": round_num,
                "metrics": metrics,
                "utilities": {str(k): v for k, v in round_utilities.items()},
                "production": {str(k): v for k, v in (self.market.production_per_round[-1] if self.market.production_per_round else {}).items()},
                "inventories": {
                    str(aid): dict(inv)
                    for aid, inv in self.market.inventories.items()
                },
                "tokens": {str(aid): v for aid, v in self.market.tokens.items()},
                # --- Reputation ---
                "reputation": reputation_now,
                "reputation_delta": reputation_delta,
                # --- Trades ---
                "trades": [
                    {
                        "trade_id": t.trade_id,
                        "proposer": t.proposer_id,
                        "target": t.target_id,
                        "offer": {"good": t.offer_good, "qty": t.offer_qty},
                        "price": t.price,
                        "status": t.status,
                        "defected_by": t.defected_by,
                    }
                    for t in round_trades
                ],
                "trade_count": len(round_trades),
                "defections": sum(1 for t in round_trades if t.status == "defected"),
                "mediated_trade_count": len(mediated_trades),
                # --- Contracting ---
                "contracts_proposed": contracts_proposed,
                "contracts_active": contracts_active,
                "contracts_executed_this_round": contracts_executed,
                "contracts_breached_this_round": contracts_breached,
                "contracts_rejected": contracts_rejected,
                "penalty_ledger": penalty_ledger,
                # --- Mediation ---
                "active_mediator": {
                    "designer_id": active_med.designer_id,
                    "action_both": active_med.action_both,
                    "action_one": active_med.action_one,
                } if active_med else None,
                # --- Reputation intermediate ---
                "defections_suffered_cumulative": {
                    str(k): v for k, v in self.market.defections_suffered.items()
                },
                "warnings_broadcast_cumulative": {
                    str(k): v for k, v in self.market.warnings_broadcast.items()
                },
                "negative_mentions": list(self.market.negative_mentions),
                # --- Messages ---
                "private_messages": private_messages,
                "public_messages": public_messages,
            })

        return self.round_logs

    async def _run_round(self, round_num: int) -> dict[int, float]:
        """Execute all 5 phases. Returns {agent_id: utility_this_round}."""

        # --- Phase 0a: Round income (prevents deflationary token drain) ---
        for agent in self.agents:
            self.market.tokens[agent.agent_id] += ROUND_INCOME

        # --- Phase 0b: Inventory spoilage (perishable goods) ---
        if round_num > 1:
            for agent in self.agents:
                inv = self.market.inventories[agent.agent_id]
                for good in GOODS:
                    old_qty = inv[good]
                    if old_qty > 0:
                        inv[good] = int(old_qty * (1 - SPOILAGE_RATE))

        # --- Phase 1: Production ---
        production_actions = await self._call_agents_phase("production", round_num)
        production_this_round: dict[int, int] = {}
        for agent in self.agents:
            actions = production_actions.get(agent.agent_id, [])
            units = 0
            for act in actions:
                if act.get("action") == "produce" and act.get("good") == agent.specialty:
                    qty = min(int(act.get("quantity", 0)), 5)
                    affordable_qty = min(qty, self.market.tokens.get(agent.agent_id, 0) // COST_PRODUCE)
                    production_cost = affordable_qty * COST_PRODUCE
                    if production_cost:
                        self.market.tokens[agent.agent_id] -= production_cost
                    self.market.inventories[agent.agent_id][agent.specialty] += affordable_qty
                    units += affordable_qty
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

        # --- Phase 3b: Contract enforcement (before consumption so penalties apply same round) ---
        for mech in self.mechanisms:
            if hasattr(mech, 'on_round_end') and mech.name == "contracting":
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
                "sustainability": 1.0, "peace": 1.0
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
                specialties=self.specialties,
                round_num=round_num,
                total_rounds=ROUNDS,
            )
            prompts[agent.agent_id] = (agent, prompt)

        async def _staggered_call(agent, prompt, delay):
            await asyncio.sleep(delay)
            return await agent.call(prompt)

        results = await asyncio.gather(*[
            _staggered_call(agent, prompt, i * 0.05)
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
                    if not self.market.are_neighbors(sender_id, target):
                        continue
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
        # Track committed inventory to prevent over-promising
        committed: dict[str, int] = {g: 0 for g in GOODS}
        for act in actions:
            if act.get("action") == "propose_sale":
                try:
                    target = int(act["target"])
                    offer = act["offer"]
                    qty = max(0, int(offer["quantity"]))
                    price = max(0, int(act["price"]))
                    good = offer["good"]
                    if qty == 0:
                        continue
                    # Cap quantity to what's actually available after prior commitments
                    available = self.market.inventories[proposer_id].get(good, 0) - committed.get(good, 0)
                    qty = min(qty, max(0, available))
                    if qty == 0:
                        continue
                    committed[good] = committed.get(good, 0) + qty
                    trade = TradeOffer(
                        trade_id=self.market.new_trade_id(),
                        proposer_id=proposer_id,
                        target_id=target,
                        offer_good=good,
                        offer_qty=qty,
                        price=price,
                        round_num=round_num,
                        proposer_delegated=bool(act.get("use_mediator", False)),
                    )
                    self.market.post_trade_offer(trade)
                except (KeyError, ValueError, TypeError):
                    pass

    def _process_contract_proposals(self, proposer_id: int, actions: list[dict], round_num: int) -> None:
        for act in actions:
            if act.get("action") == "propose_contract":
                try:
                    target = int(act["target"])
                    if not self.market.are_neighbors(proposer_id, target):
                        continue
                    terms = act["terms"]
                    contract = Contract(
                        contract_id=self.market.new_contract_id(),
                        proposer_id=proposer_id,
                        counterparty_id=target,
                        proposer_delivers_good=terms["i_deliver"]["good"],
                        proposer_delivers_qty=max(0, int(terms["i_deliver"]["quantity"])),
                        counterparty_delivers_good=terms["they_deliver"]["good"],
                        counterparty_delivers_qty=max(0, int(terms["they_deliver"]["quantity"])),
                        breach_penalty=max(0, int(terms.get("breach_penalty", DEFAULT_BREACH_PENALTY))),
                        execution_round=int(terms.get("execution_round", round_num)),
                    )
                    self.market.contracts[contract.contract_id] = contract
                    # Notify counterparty via private channel
                    def fmt_asset(qty: int, asset: str) -> str:
                        return f"{qty} tokens" if asset == "TOKENS" else f"{qty}×{asset}"

                    self.market.post_message(Message(
                        sender_id=proposer_id,
                        text=f"CONTRACT PROPOSAL {contract.contract_id}: I deliver "
                             f"{fmt_asset(contract.proposer_delivers_qty, contract.proposer_delivers_good)}, "
                             f"you deliver {fmt_asset(contract.counterparty_delivers_qty, contract.counterparty_delivers_good)}. "
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

                if delegated and self.market.active_mediator:
                    # Mediated simultaneous exchange
                    self._execute_mediated_trade(offer, round_num)
                else:
                    # Standard trade: proposer delivers first, target may defect
                    self._execute_standard_trade(offer, agent_id, defect=False, round_num=round_num)

            elif action_type == "defect_trade":
                self._execute_standard_trade(offer, agent_id, defect=True, round_num=round_num)

    def _execute_standard_trade(
        self, offer: TradeOffer, accepting_agent: int, defect: bool, round_num: int
    ) -> None:
        if defect:
            # Buyer takes seller's goods but does not pay.
            transferred = self.market.transfer_goods(
                offer.proposer_id, accepting_agent, offer.offer_good, offer.offer_qty
            )
            if transferred:
                self.market.record_trade_outcome(offer, defected_by=accepting_agent)
        else:
            if not self.market.can_deliver_asset(offer.proposer_id, offer.offer_good, offer.offer_qty):
                self.market.record_trade_outcome(offer, defected_by=offer.proposer_id)
                return
            ok1 = self.market.transfer_goods(offer.proposer_id, accepting_agent, offer.offer_good, offer.offer_qty)
            ok2 = self.market.transfer_tokens(accepting_agent, offer.proposer_id, offer.price)
            if ok1 and ok2:
                self.market.record_trade_outcome(offer)
            else:
                self.market.record_trade_outcome(offer, defected_by=accepting_agent if not ok2 else offer.proposer_id)

    def _execute_mediated_trade(self, offer: TradeOffer, round_num: int) -> None:
        active = self.market.active_mediator
        if active.action_both == "execute_fair":
            seller_ready = self.market.can_deliver_asset(offer.proposer_id, offer.offer_good, offer.offer_qty)
            buyer_ready = self.market.can_deliver_asset(offer.target_id, "TOKENS", offer.price)
            if seller_ready and buyer_ready:
                self.market.transfer_goods(offer.proposer_id, offer.target_id, offer.offer_good, offer.offer_qty)
                self.market.transfer_tokens(offer.target_id, offer.proposer_id, offer.price)
                offer.status = "mediated"
                self.market.trade_history.append(offer)
                self.market._update_reputation(offer.proposer_id, success=True)
                self.market._update_reputation(offer.target_id, success=True)
            else:
                defected_by = offer.proposer_id if not seller_ready else offer.target_id
                self.market.record_trade_outcome(offer, defected_by=defected_by)
            # Deduct mediation fee from both parties only when mediation was attempted
            if not hasattr(self.market, "_penalty_ledger"):
                self.market._penalty_ledger = {}
            for aid in [offer.proposer_id, offer.target_id]:
                self.market._penalty_ledger[aid] = (
                    self.market._penalty_ledger.get(aid, 0) + MEDIATION_FEE
                )
        elif active.action_both == "execute_split":
            seller_ready = self.market.can_deliver_asset(offer.proposer_id, offer.offer_good, offer.offer_qty)
            buyer_ready = self.market.can_deliver_asset(offer.target_id, "TOKENS", offer.price)
            if seller_ready and buyer_ready:
                half_qty = max(1, offer.offer_qty // 2)
                half_price = max(1, offer.price // 2)
                self.market.transfer_goods(offer.proposer_id, offer.target_id, offer.offer_good, half_qty)
                self.market.transfer_tokens(offer.target_id, offer.proposer_id, half_price)
                offer.status = "mediated"
                self.market.trade_history.append(offer)
                self.market._update_reputation(offer.proposer_id, success=True)
                self.market._update_reputation(offer.target_id, success=True)
            else:
                defected_by = offer.proposer_id if not seller_ready else offer.target_id
                self.market.record_trade_outcome(offer, defected_by=defected_by)
            if not hasattr(self.market, "_penalty_ledger"):
                self.market._penalty_ledger = {}
            for aid in [offer.proposer_id, offer.target_id]:
                self.market._penalty_ledger[aid] = (
                    self.market._penalty_ledger.get(aid, 0) + MEDIATION_FEE
                )
        elif active.action_both == "cancel":
            offer.status = "rejected"
            self.market.trade_history.append(offer)
