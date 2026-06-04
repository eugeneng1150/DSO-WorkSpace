"""Main simulation loop: 5 phases per round."""
from __future__ import annotations
import asyncio
from typing import TYPE_CHECKING
from tqdm import tqdm

from .market import Market, Message, TradeOffer, Contract, generate_network
from .prompt_builder import build_prompt
from ..metrics.social import compute_metrics
from .agent import TrollAgent
from ..config import (
    GOODS, ROUNDS, UTILITY_CONSUME, COST_PRODUCE, MEDIATION_FEE,
    DEFAULT_BREACH_PENALTY, MAX_PRODUCE, MIN_NEIGHBORS, MAX_NEIGHBORS,
    SPOILAGE_RATE, SANCTION_COST_RATIO,
    JUDICIAL_FILING_FEE, JUDICIAL_PENALTY,
    JUDICIAL_COMPENSATION, JUDICIAL_FALSE_FINE,
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
        total_rounds: int = ROUNDS,
    ):
        self.agents = agents
        self.mechanisms = mechanisms
        self.condition_label = condition_label
        self.run_idx = run_idx
        self.total_rounds = total_rounds
        self.mechanism_names = [m.name for m in mechanisms]

        agent_ids = [a.agent_id for a in agents]
        self.specialties = {a.agent_id: a.specialty for a in agents}
        self.troll_ids = [a.agent_id for a in agents if isinstance(a, TrollAgent)]
        network = generate_network(agent_ids, self.specialties, MIN_NEIGHBORS, MAX_NEIGHBORS)

        # Trolls are connected to ALL other agents (maximally exposed)
        for tid in self.troll_ids:
            for aid in agent_ids:
                if aid != tid:
                    network[tid].add(aid)
                    network[aid].add(tid)

        self.market = Market(agent_ids=agent_ids, goods=GOODS, network=network)
        self.market.troll_ids = self.troll_ids

        self.round_logs: list[dict] = []
        self.trace_log: list[dict] = []
        self.session_log: dict = {
            "network": {str(k): sorted(v) for k, v in self.market.network.items()},
            "specialties": {str(k): v for k, v in self.specialties.items()},
            "troll_ids": self.troll_ids,
        }
        self._pre_consumption_penalties: dict[int, float] = {}

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

        pbar = tqdm(range(1, self.total_rounds + 1), desc=f"[{self.condition_label}] Run {self.run_idx}", unit="round", leave=True)
        for round_num in pbar:
            self.market.new_round(round_num)
            for mech in self.mechanisms:
                mech.on_round_start(self.market, round_num)

            round_utilities = await self._run_round(round_num)

            # Set production baseline after round 1
            if round_num == 1:
                prod = self.market.production_per_round[-1] if self.market.production_per_round else {}
                non_troll_prod = {k: v for k, v in prod.items() if k not in self.troll_ids}
                n = len(non_troll_prod) or 1
                self.market._production_baseline = sum(non_troll_prod.values()) / n

            metrics = compute_metrics(self.market, round_utilities)
            self.market.metrics_log.append({"round": round_num, **metrics})
            non_troll_utils = [v for k, v in round_utilities.items() if k not in self.troll_ids]
            avg_util = sum(non_troll_utils) / max(len(non_troll_utils), 1)
            pbar.set_postfix(util=f"{avg_util:.1f}", gini=f"{metrics['gini']:.2f}")

            for mech in self.mechanisms:
                if mech.name in ("contracting", "escrow"):
                    continue  # already enforced inside _run_round before consumption
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
            penalty_ledger      = self._pre_consumption_penalties

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
                # --- Reputation ---
                "reputation": reputation_now,
                "reputation_delta": reputation_delta, # how much did reputation change this round vs last round?
                # --- Trades ---
                "trades": [
                    {
                        "trade_id": t.trade_id,
                        "proposer": t.proposer_id,
                        "target": t.target_id,
                        "offer": {"good": t.offer_good, "qty": t.offer_qty},
                        "want": {"good": t.want_good, "qty": t.want_qty},
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
                # --- Governance ---
                "governance": {
                    str(aid): {
                        "status": self.market.governance_states[aid].status,
                        "fine_tier": self.market.governance_states[aid].fine_tier,
                        "signals": list(self.market.governance_states[aid].triggered_signals),
                        "clean_rounds": self.market.governance_states[aid].clean_rounds,
                        "suspension_rounds_left": self.market.governance_states[aid].suspension_rounds_left,
                    }
                    for aid in self.market.agent_ids
                } if self.market.governance_states else None,
                # --- Network Rewiring ---
                "network": {
                    str(aid): sorted(neighbors)
                    for aid, neighbors in self.market.network.items()
                } if "network_rewiring" in self.mechanism_names else None,
                "network_events_this_round": [
                    e for e in self.market.network_events
                    if e["round"] == round_num
                ] if "network_rewiring" in self.mechanism_names else None,
                # --- Sanctions ---
                "sanctions_this_round": [
                    s for s in self.market.sanction_log
                    if s["round"] == round_num
                ] if hasattr(self.market, "sanction_log") and "sanction" in self.mechanism_names else None,
                # --- Judicial ---
                "complaints_this_round": [
                    c for c in self.market.complaint_log
                    if c["round"] == round_num
                ] if hasattr(self.market, "complaint_log") and "judicial" in self.mechanism_names else None,
                # --- Escrow ---
                "escrow_forfeitures_this_round": [
                    e for e in self.market.escrow_log
                    if e["round"] == round_num
                ] if hasattr(self.market, "escrow_log") and "escrow" in self.mechanism_names else None,
                # --- Messages ---
                "private_messages": private_messages,
                "public_messages": public_messages,
            })

        return self.round_logs

    async def _run_round(self, round_num: int) -> dict[int, float]:
        """Execute all 5 phases. Returns {agent_id: utility_this_round}."""

        # --- Phase 0: Inventory spoilage (perishable goods) ---
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
            gov = self.market.governance_states.get(agent.agent_id)
            if gov and gov.status == "suspended":
                production_this_round[agent.agent_id] = 0
                continue
            actions = production_actions.get(agent.agent_id, [])
            units = 0
            for act in actions:
                if act.get("action") == "produce" and act.get("good") == agent.specialty:
                    qty = min(max(0, int(act.get("quantity", 0))), MAX_PRODUCE - units)
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

        # Troll agents: propose trades to ALL neighbors (they'll defect on delivery)
        for agent in self.agents:
            if isinstance(agent, TrollAgent):
                self._inject_troll_proposals(agent, round_num)

        # Network rewiring (after messages/proposals, before trade phase)
        if "network_rewiring" in self.mechanism_names:
            self._process_network_actions(comm_actions, round_num)

        # Sanctions (agents punish others based on past behavior)
        if "sanction" in self.mechanism_names:
            self._process_sanction_actions(comm_actions, round_num)

        # Contract review stage: agents that received proposals respond
        if "contracting" in self.mechanism_names:
            review_actions = await self._call_agents_phase("contract_review", round_num)
            for agent in self.agents:
                actions = review_actions.get(agent.agent_id, [])
                self._process_contract_signing(agent.agent_id, actions)

        # --- Phase 2b: Contract enforcement (before barter so contracted goods transfer first) ---
        for mech in self.mechanisms:
            if mech.name == "contracting":
                mech.on_round_end(self.market, round_num)

        # --- Phase 3: Trade (agents see post-contract inventory) ---
        trade_actions = await self._call_agents_phase("trade", round_num)

        # Troll agents: override with defect-all on every pending offer
        for agent in self.agents:
            if isinstance(agent, TrollAgent):
                trade_actions[agent.agent_id] = [
                    {"action": "defect_trade", "trade_id": o.trade_id}
                    for o in self.market.pending_offers.get(agent.agent_id, [])
                ]

        for agent in self.agents:
            actions = trade_actions.get(agent.agent_id, [])
            self._process_trade_decisions(agent.agent_id, actions, round_num)

        # Judicial complaints (agents file after seeing trade outcomes)
        if "judicial" in self.mechanism_names:
            complaint_actions = await self._call_agents_phase("complaint", round_num)
            self._process_complaint_actions(complaint_actions, round_num)

        # Escrow: process defection payouts before consumption (same-round compensation)
        for mech in self.mechanisms:
            if mech.name == "escrow":
                mech.on_round_end(self.market, round_num)

        # Snapshot penalties before consumption pops them
        self._pre_consumption_penalties = dict(self.market._penalty_ledger)

        # --- Phase 4: Consumption ---
        round_utilities: dict[int, float] = {}
        for agent in self.agents:
            consumed_utility = 0.0
            inv = self.market.inventories[agent.agent_id]
            for need in agent.needs:
                qty = inv.get(need, 0)
                consumed_utility += qty * UTILITY_CONSUME
                inv[need] = 0  # consume all held units of needed goods

            # Deduct production cost (utility-based)
            units_produced = self.market.production_per_round[-1].get(agent.agent_id, 0)
            consumed_utility -= units_produced * COST_PRODUCE

            # Apply penalties (contract breaches, mediation fees, governance fines)
            penalty = self.market._penalty_ledger.pop(agent.agent_id, 0)
            consumed_utility -= penalty

            round_utilities[agent.agent_id] = consumed_utility
            agent.last_utility = consumed_utility
            agent.total_utility += consumed_utility

        return round_utilities

    async def _call_agents_phase(self, phase: str, round_num: int) -> dict[int, list[dict]]:
        """Build prompts for all agents and call them concurrently."""
        prompts = {}
        for agent in self.agents:
            gov = self.market.governance_states.get(agent.agent_id)
            if gov and gov.status == "suspended":
                continue

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

            prompt = build_prompt(
                agent_id=agent.agent_id,
                specialty=agent.specialty,
                needs=agent.needs,
                last_utility=agent.last_utility,
                total_utility=agent.total_utility,
                market=self.market,
                mechanisms=self.mechanism_names,
                stage_overrides=stage_overrides,
                specialties=self.specialties,
                round_num=round_num,
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

    def _inject_troll_proposals(self, agent: TrollAgent, round_num: int) -> None:
        """Trolls propose trades to every neighbor, offering their specialty good."""
        neighbors = self.market.network.get(agent.agent_id, set())
        other_goods = [g for g in GOODS if g != agent.specialty]
        for target_id in neighbors:
            if target_id in self.troll_ids:
                continue
            want_good = other_goods[target_id % len(other_goods)]
            trade = TradeOffer(
                trade_id=self.market.new_trade_id(),
                proposer_id=agent.agent_id,
                target_id=target_id,
                offer_good=agent.specialty,
                offer_qty=2,
                want_good=want_good,
                want_qty=2,
                round_num=round_num,
            )
            self.market.post_trade_offer(trade)

    def _process_trade_proposals(self, proposer_id: int, actions: list[dict], round_num: int) -> None:
        # Track committed inventory to prevent over-promising
        committed: dict[str, int] = {g: 0 for g in GOODS}
        for act in actions:
            if act.get("action") == "propose_trade":
                try:
                    target = int(act["target"])
                    offer = act["offer"]
                    qty = max(0, int(offer["quantity"]))
                    good = offer["good"]
                    want = act["want"]
                    want_good = want["good"]
                    want_qty = max(0, int(want["quantity"]))
                    if qty == 0 or want_qty == 0:
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
                        want_good=want_good,
                        want_qty=want_qty,
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
                        return f"{qty}×{asset}"

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

    def _process_network_actions(
        self, comm_actions: dict[int, list[dict]], round_num: int
    ) -> None:
        sever_used: dict[int, int] = {}
        request_used: dict[int, int] = {}
        for agent in sorted(self.agents, key=lambda a: a.agent_id):
            actions = comm_actions.get(agent.agent_id, [])
            for act in actions:
                action_type = act.get("action")
                try:
                    if action_type == "sever_link":
                        target = int(act["target"])
                        self.market.sever_link(agent.agent_id, target, round_num, sever_used)
                    elif action_type == "request_link":
                        target = int(act["target"])
                        self.market.request_link(agent.agent_id, target, round_num, request_used)
                except (KeyError, ValueError, TypeError):
                    pass

    def _process_sanction_actions(
        self, comm_actions: dict[int, list[dict]], round_num: int
    ) -> None:
        for agent in sorted(self.agents, key=lambda a: a.agent_id):
            actions = comm_actions.get(agent.agent_id, [])
            for act in actions:
                if act.get("action") != "sanction":
                    continue
                try:
                    target = int(act["target"])
                    amount = int(act["amount"])
                except (KeyError, ValueError, TypeError):
                    continue
                if target not in self.market.agent_ids or target == agent.agent_id or amount <= 0:
                    continue
                damage = amount * SANCTION_COST_RATIO
                self.market._penalty_ledger[agent.agent_id] = (
                    self.market._penalty_ledger.get(agent.agent_id, 0) + amount
                )
                self.market._penalty_ledger[target] = (
                    self.market._penalty_ledger.get(target, 0) + damage
                )
                self.market.sanction_log.append({
                    "round": round_num,
                    "punisher": agent.agent_id,
                    "target": target,
                    "spent": amount,
                    "damage": damage,
                })
                self.market.public_feed.append(Message(
                    sender_id=-1,
                    text=f"Agent {target} was sanctioned this round (-{damage} utility).",
                    round_num=round_num,
                    channel="public",
                ))

    def _process_complaint_actions(
        self, complaint_actions: dict[int, list[dict]], round_num: int
    ) -> None:
        seen_complaints: set[tuple[int, str]] = set()
        for agent in sorted(self.agents, key=lambda a: a.agent_id):
            actions = complaint_actions.get(agent.agent_id, [])
            for act in actions:
                if act.get("action") != "file_complaint":
                    continue
                try:
                    target = int(act["target"])
                    trade_id = str(act["trade_id"])
                except (KeyError, ValueError, TypeError):
                    continue
                if target not in self.market.agent_ids or target == agent.agent_id:
                    continue
                if (agent.agent_id, trade_id) in seen_complaints:
                    continue
                seen_complaints.add((agent.agent_id, trade_id))

                self.market._penalty_ledger[agent.agent_id] = (
                    self.market._penalty_ledger.get(agent.agent_id, 0) + JUDICIAL_FILING_FEE
                )

                cited_trade = next(
                    (t for t in self.market.trade_history
                     if t.trade_id == trade_id),
                    None,
                )

                filer_is_party = (
                    cited_trade is not None
                    and (agent.agent_id == cited_trade.proposer_id
                         or agent.agent_id == cited_trade.target_id)
                )

                if (filer_is_party
                        and cited_trade.status == "defected"
                        and cited_trade.defected_by == target):
                    self.market._penalty_ledger[target] = (
                        self.market._penalty_ledger.get(target, 0) + JUDICIAL_PENALTY
                    )
                    self.market._penalty_ledger[agent.agent_id] = (
                        self.market._penalty_ledger.get(agent.agent_id, 0) - JUDICIAL_COMPENSATION
                    )
                    verdict = "GUILTY"
                else:
                    self.market._penalty_ledger[agent.agent_id] = (
                        self.market._penalty_ledger.get(agent.agent_id, 0) + JUDICIAL_FALSE_FINE
                    )
                    verdict = "DISMISSED"

                self.market.complaint_log.append({
                    "round": round_num,
                    "filer": agent.agent_id,
                    "target": target,
                    "trade_id": trade_id,
                    "verdict": verdict,
                })

                self.market.public_feed.append(Message(
                    sender_id=-1,
                    text=f"Court ruling: Agent {agent.agent_id} filed complaint against Agent {target} → {verdict}.",
                    round_num=round_num,
                    channel="public",
                ))

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
                target_delegated = action_type == "delegate_to_mediator"
                use_mediator = (target_delegated or offer.proposer_delegated) and self.market.active_mediator is not None

                if use_mediator:
                    self._execute_mediated_trade(offer, round_num, target_delegated=target_delegated)
                else:
                    self._execute_standard_trade(offer, agent_id, defect=False, round_num=round_num)

            elif action_type == "defect_trade":
                if offer.proposer_delegated and self.market.active_mediator:
                    if self.market.active_mediator.action_one == "cancel":
                        offer.status = "rejected"
                        self.market.trade_history.append(offer)
                    else:
                        self._execute_standard_trade(offer, agent_id, defect=True, round_num=round_num)
                else:
                    self._execute_standard_trade(offer, agent_id, defect=True, round_num=round_num)

    def _execute_standard_trade(
        self, offer: TradeOffer, accepting_agent: int, defect: bool, round_num: int
    ) -> None:
        if defect:
            # Target takes proposer's goods without delivering their own
            self.market.transfer_goods(
                offer.proposer_id, accepting_agent, offer.offer_good, offer.offer_qty
            )
            self.market.record_trade_outcome(offer, defected_by=accepting_agent)
        else:
            proposer_can = self.market.can_deliver_asset(
                offer.proposer_id, offer.offer_good, offer.offer_qty
            )
            target_can = self.market.can_deliver_asset(
                accepting_agent, offer.want_good, offer.want_qty
            )
            if not proposer_can:
                self.market.record_trade_outcome(offer, defected_by=offer.proposer_id)
                return
            if not target_can:
                self.market.record_trade_outcome(offer, defected_by=accepting_agent)
                return
            ok1 = self.market.transfer_goods(
                offer.proposer_id, accepting_agent, offer.offer_good, offer.offer_qty
            )
            ok2 = self.market.transfer_goods(
                accepting_agent, offer.proposer_id, offer.want_good, offer.want_qty
            )
            if ok1 and ok2:
                self.market.record_trade_outcome(offer)
            else:
                defector = accepting_agent if not ok2 else offer.proposer_id
                self.market.record_trade_outcome(offer, defected_by=defector)

    def _execute_mediated_trade(self, offer: TradeOffer, round_num: int, target_delegated: bool = True) -> None:
        active = self.market.active_mediator
        both_delegated = offer.proposer_delegated and target_delegated
        action = active.action_both if both_delegated else active.action_one

        trade_succeeded = False

        if action in ("execute_fair", "execute_split"):
            proposer_ready = self.market.can_deliver_asset(offer.proposer_id, offer.offer_good, offer.offer_qty)
            target_ready = self.market.can_deliver_asset(offer.target_id, offer.want_good, offer.want_qty)
            if proposer_ready and target_ready:
                if action == "execute_split":
                    half_offer = max(1, offer.offer_qty // 2)
                    half_want = max(1, offer.want_qty // 2)
                    self.market.transfer_goods(offer.proposer_id, offer.target_id, offer.offer_good, half_offer)
                    self.market.transfer_goods(offer.target_id, offer.proposer_id, offer.want_good, half_want)
                    offer.offer_qty = half_offer
                    offer.want_qty = half_want
                else:
                    self.market.transfer_goods(offer.proposer_id, offer.target_id, offer.offer_good, offer.offer_qty)
                    self.market.transfer_goods(offer.target_id, offer.proposer_id, offer.want_good, offer.want_qty)
                offer.status = "mediated"
                self.market.trade_history.append(offer)
                self.market._update_reputation(offer.proposer_id, success=True)
                self.market._update_reputation(offer.target_id, success=True)
                trade_succeeded = True
            else:
                defected_by = offer.proposer_id if not proposer_ready else offer.target_id
                self.market.record_trade_outcome(offer, defected_by=defected_by)
        elif action == "cancel":
            offer.status = "rejected"
            self.market.trade_history.append(offer)

        if trade_succeeded:
            if offer.proposer_delegated:
                self.market._penalty_ledger[offer.proposer_id] = (
                    self.market._penalty_ledger.get(offer.proposer_id, 0) + MEDIATION_FEE
                )
            if target_delegated:
                self.market._penalty_ledger[offer.target_id] = (
                    self.market._penalty_ledger.get(offer.target_id, 0) + MEDIATION_FEE
                )
