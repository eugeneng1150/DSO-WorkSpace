"""Central market state: inventories, message queues, trade ledger, contracts, mediation."""
from __future__ import annotations
import re
import uuid
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Message:
    sender_id: int
    text: str
    round_num: int
    channel: str   # "private" | "public"
    recipient_id: Optional[int] = None   # set for private messages


@dataclass
class TradeOffer:
    trade_id: str
    proposer_id: int
    target_id: int
    offer_good: str
    offer_qty: int
    request_good: str
    request_qty: int
    round_num: int
    status: str = "pending"   # pending | accepted | rejected | completed | defected | mediated


@dataclass
class Contract:
    contract_id: str
    proposer_id: int
    counterparty_id: int
    proposer_delivers_good: str
    proposer_delivers_qty: int
    counterparty_delivers_good: str
    counterparty_delivers_qty: int
    breach_penalty: int
    execution_round: int
    status: str = "proposed"   # proposed | signed | rejected | executed | breached


@dataclass
class MediatorDesign:
    designer_id: int
    action_both: str    # execute_fair | execute_split | cancel
    action_one: str
    rationale: str
    approvals: int = 0


class Market:
    def __init__(self, agent_ids: list[int], goods: list[str]):
        self.agent_ids = agent_ids
        self.goods = goods
        self.round_num = 0

        # Inventories: agent_id -> {good: qty}
        self.inventories: dict[int, dict[str, int]] = {
            aid: {g: 0 for g in goods} for aid in agent_ids
        }

        # Message queues (reset each round)
        self.private_inboxes: dict[int, list[Message]] = {aid: [] for aid in agent_ids}
        self.public_feed: list[Message] = []

        # Trade ledger
        self.pending_offers: dict[int, list[TradeOffer]] = {aid: [] for aid in agent_ids}
        self.trade_history: list[TradeOffer] = []

        # Contracts (contracting mechanism)
        self.contracts: dict[str, Contract] = {}

        # Mediation state (mediation mechanism)
        self.mediator_designs: list[MediatorDesign] = []
        self.active_mediator: Optional[MediatorDesign] = None
        self.mediation_votes: dict[int, list[int]] = {}  # voter_id -> [designer_ids]

        # Reputation scores (reputation mechanism): agent_id -> score [0,1]
        self.system_reputation: dict[int, float] = {aid: 1.0 for aid in agent_ids}
        self._trade_counts: dict[int, dict[str, int]] = {
            aid: {"success": 0, "total": 0} for aid in agent_ids
        }

        # Per-round metrics log
        self.metrics_log: list[dict] = []

        # Production baseline (round 1 avg, set after round 1)
        self._production_baseline: Optional[float] = None
        self.production_per_round: list[dict[int, int]] = []  # list of {agent_id: units_produced}

        # Defection tracking for intermediate variables
        self.defections_suffered: dict[int, int] = {aid: 0 for aid in agent_ids}
        self.warnings_broadcast: dict[int, int] = {aid: 0 for aid in agent_ids}
        self.negative_mentions: list[dict] = []  # {sender, target, round, verified}

    def new_round(self, round_num: int):
        self.round_num = round_num
        for aid in self.agent_ids:
            self.private_inboxes[aid] = []
            self.pending_offers[aid] = []
        self.public_feed = []

    def post_message(self, msg: Message):
        if msg.channel == "public":
            self.public_feed.append(msg)
            if self._is_negative_mention(msg.text):
                self.warnings_broadcast[msg.sender_id] = (
                    self.warnings_broadcast.get(msg.sender_id, 0) + 1
                )
                target = self._extract_mentioned_agent(msg.text)
                if target is not None:
                    self.negative_mentions.append({
                        "sender": msg.sender_id,
                        "target": target,
                        "round": msg.round_num,
                    })
        else:
            self.private_inboxes[msg.recipient_id].append(msg)

    def _is_negative_mention(self, text: str) -> bool:
        keywords = ["defect", "cheat", "short", "failed", "breach", "warn", "didn't deliver", "stole"]
        return any(k in text.lower() for k in keywords)

    def _extract_mentioned_agent(self, text: str) -> Optional[int]:
        match = re.search(r'Agent (\d+)', text)
        return int(match.group(1)) if match else None

    def post_trade_offer(self, offer: TradeOffer):
        self.pending_offers[offer.target_id].append(offer)

    def new_trade_id(self) -> str:
        return "t_" + uuid.uuid4().hex[:6]

    def new_contract_id(self) -> str:
        return "c_" + uuid.uuid4().hex[:6]

    def record_trade_outcome(self, trade: TradeOffer, defected_by: Optional[int] = None):
        trade.status = "defected" if defected_by else "completed"
        self.trade_history.append(trade)
        if defected_by is not None:
            victim = trade.target_id if defected_by == trade.proposer_id else trade.proposer_id
            self.defections_suffered[victim] = self.defections_suffered.get(victim, 0) + 1
            self._update_reputation(defected_by, success=False)
            self._update_reputation(victim, success=True)
        else:
            self._update_reputation(trade.proposer_id, success=True)
            self._update_reputation(trade.target_id, success=True)

    def _update_reputation(self, agent_id: int, success: bool, decay: float = 0.1):
        counts = self._trade_counts[agent_id]
        counts["total"] += 1
        if success:
            counts["success"] += 1
        # Exponential recency weighting: blend new outcome into running score
        old = self.system_reputation[agent_id]
        new_obs = 1.0 if success else 0.0
        self.system_reputation[agent_id] = (1 - decay) * old + decay * new_obs

    def get_partner_history(self, agent_id: int, window: int = 5) -> dict[int, list[TradeOffer]]:
        recent = [t for t in self.trade_history if t.round_num > self.round_num - window]
        history: dict[int, list[TradeOffer]] = {}
        for t in recent:
            if t.proposer_id == agent_id or t.target_id == agent_id:
                partner = t.target_id if t.proposer_id == agent_id else t.proposer_id
                history.setdefault(partner, []).append(t)
        return history

    def transfer_goods(self, from_id: int, to_id: int, good: str, qty: int) -> bool:
        if self.inventories[from_id][good] < qty:
            return False
        self.inventories[from_id][good] -= qty
        self.inventories[to_id][good] += qty
        return True
