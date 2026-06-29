"""Central market state: inventories, message queues, trade ledger, contracts, mediation."""
from __future__ import annotations
import random
import re
import uuid
from dataclasses import dataclass
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
    want_good: str
    want_qty: int
    round_num: int
    proposer_delegated: bool = False
    status: str = "pending"   # pending | accepted | rejected | completed | defected | mediated
    defected_by: Optional[int] = None


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


def generate_network(
    agent_ids: list[int],
    specialties: dict[int, str],
    min_neighbors: int = 4,
    max_neighbors: int = 6,
) -> dict[int, set[int]]:
    """Generate a static trade network guaranteeing each agent can reach both other goods."""
    goods_to_agents: dict[str, list[int]] = {}
    for aid, good in specialties.items(): # Build reverse index of goods to agent IDs
        goods_to_agents.setdefault(good, []).append(aid)

    all_goods = list(goods_to_agents.keys())
    adj: dict[int, set[int]] = {aid: set() for aid in agent_ids}

    def _add_edge(a: int, b: int):
        adj[a].add(b)
        adj[b].add(a)

    # Step 1: guarantee each agent has at least 3 neighbors per other good
    cross_good_min = min(3, len(next(iter(goods_to_agents.values()))))
    for aid in agent_ids:
        my_good = specialties[aid]
        for g in all_goods:
            if g == my_good:
                continue
            current = [x for x in adj[aid] if specialties[x] == g]
            needed = cross_good_min - len(current)
            for _ in range(needed):
                candidates = [x for x in goods_to_agents[g] if x not in adj[aid] and len(adj[x]) < max_neighbors]
                if not candidates:
                    candidates = [x for x in goods_to_agents[g] if x not in adj[aid]]
                if not candidates:
                    break
                candidates.sort(key=lambda x: len(adj[x]))
                _add_edge(aid, candidates[0])

    # Step 2: add random edges until each agent has min_neighbors
    for aid in agent_ids:
        while len(adj[aid]) < min_neighbors:
            candidates = [x for x in agent_ids if x != aid and x not in adj[aid] and len(adj[x]) < max_neighbors]
            if not candidates:
                break
            _add_edge(aid, random.choice(candidates))

    return adj


class Market:
    def __init__(self, agent_ids: list[int], goods: list[str],
                 network: dict[int, set[int]] | None = None):
        self.agent_ids = agent_ids
        self.goods = goods
        self.round_num = 0

        # Social network: agent_id -> set of neighbor agent_ids
        self.network: dict[int, set[int]] = network or {aid: set(agent_ids) - {aid} for aid in agent_ids}

        # Inventories: agent_id -> {good: qty}
        self.inventories: dict[int, dict[str, int]] = {
            aid: {g: 0 for g in goods} for aid in agent_ids
        }
        # Tokens removed — pure barter economy

        # Message queues (reset each round)
        self.private_inboxes: dict[int, list[Message]] = {aid: [] for aid in agent_ids}
        self.public_feed: list[Message] = []
        self.public_message_history: list[list[Message]] = []  # rolling buffer of past rounds' public messages

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
        self.negative_mentions: list[dict] = []  # {sender, target, round}

        # Penalty ledger (shared by contracting, mediation, governance)
        self._penalty_ledger: dict[int, float] = {}

        # Governance state (governance mechanism — populated by GovernanceMechanism.on_session_start)
        self.governance_states: dict = {}
        self.governance_log: list[dict] = []

        # Troll agent IDs (set by Game after construction)
        self.troll_ids: list[int] = []

        # Network rewiring state (network_rewiring mechanism)
        self.network_events: list[dict] = []
        self.network_degree_history: list[dict] = []

        # SAC trust filtering state (sac mechanism)
        self.sac_trust_scores: dict[int, float] = {}
        self.sac_low_trust: dict[int, set[int]] = {}
        self.sac_log: list[dict] = []

    def new_round(self, round_num: int):
        from ..config import MESSAGE_HISTORY_WINDOW
        # Archive current round's public messages before clearing
        if self.public_feed:
            self.public_message_history.append(list(self.public_feed))
        while len(self.public_message_history) > MESSAGE_HISTORY_WINDOW:
            self.public_message_history.pop(0)

        self.round_num = round_num
        for aid in self.agent_ids:
            self.private_inboxes[aid] = []
            self.pending_offers[aid] = []
        self.public_feed = []

    def get_message_history(self) -> list[Message]:
        """Return flattened list of public messages from the rolling history buffer."""
        return [msg for round_msgs in self.public_message_history for msg in round_msgs]

    def post_message(self, msg: Message):
        if msg.channel == "public":
            self.public_feed.append(msg)
            target = self._extract_mentioned_agent(msg.text)
            if self._is_negative_mention(msg.text) and target is not None:
                self.warnings_broadcast[msg.sender_id] = (
                    self.warnings_broadcast.get(msg.sender_id, 0) + 1
                )
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

    def are_neighbors(self, agent_a: int, agent_b: int) -> bool:
        return agent_b in self.network.get(agent_a, set())

    def sever_link(self, initiator: int, target: int, round_num: int,
                   sever_used: dict[int, int]) -> bool:
        from ..config import NET_MAX_SEVER_PER_ROUND
        if sever_used.get(initiator, 0) >= NET_MAX_SEVER_PER_ROUND:
            return False
        if not self.are_neighbors(initiator, target):
            return False
        self.network[initiator].discard(target)
        self.network[target].discard(initiator)
        sever_used[initiator] = sever_used.get(initiator, 0) + 1
        self.network_events.append({
            "round": round_num, "type": "sever",
            "initiator": initiator, "target": target, "outcome": "applied",
        })
        return True

    def request_link(self, initiator: int, target: int, round_num: int,
                     request_used: dict[int, int]) -> bool:
        from ..config import NET_MAX_REQUEST_PER_ROUND, MAX_NEIGHBORS
        if request_used.get(initiator, 0) >= NET_MAX_REQUEST_PER_ROUND:
            return False
        if target not in self.agent_ids:
            return False
        if initiator == target:
            return False
        if self.are_neighbors(initiator, target):
            return False
        if len(self.network.get(initiator, set())) >= MAX_NEIGHBORS:
            return False
        if len(self.network.get(target, set())) >= MAX_NEIGHBORS:
            self.network_events.append({
                "round": round_num, "type": "request",
                "initiator": initiator, "target": target, "outcome": "rejected_capacity",
            })
            return False
        self.network[initiator].add(target)
        self.network[target].add(initiator)
        request_used[initiator] = request_used.get(initiator, 0) + 1
        self.network_events.append({
            "round": round_num, "type": "request",
            "initiator": initiator, "target": target, "outcome": "applied",
        })
        return True

    def post_trade_offer(self, offer: TradeOffer):
        if not self.are_neighbors(offer.proposer_id, offer.target_id):
            return
        self.pending_offers[offer.target_id].append(offer)

    def new_trade_id(self) -> str:
        return "t_" + uuid.uuid4().hex[:6]

    def new_contract_id(self) -> str:
        return "c_" + uuid.uuid4().hex[:6]

    def record_trade_outcome(self, trade: TradeOffer, defected_by: Optional[int] = None):
        trade.status = "defected" if defected_by else "completed"
        trade.defected_by = defected_by
        self.trade_history.append(trade)
        if defected_by is not None:
            victim = trade.target_id if defected_by == trade.proposer_id else trade.proposer_id
            self.defections_suffered[victim] = self.defections_suffered.get(victim, 0) + 1
            self._update_reputation(defected_by, success=False)
        else:
            self._update_reputation(trade.proposer_id, success=True)
            self._update_reputation(trade.target_id, success=True)

    def _update_reputation(self, agent_id: int, success: bool):
        counts = self._trade_counts[agent_id]
        counts["total"] += 1
        if success:
            counts["success"] += 1
        self.system_reputation[agent_id] = counts["success"] / counts["total"]

    def get_partner_history(self, agent_id: int, window: int = 5) -> dict[int, list[TradeOffer]]:
        recent = [t for t in self.trade_history if t.round_num > self.round_num - window]
        history: dict[int, list[TradeOffer]] = {}
        for t in recent:
            if t.proposer_id == agent_id or t.target_id == agent_id:
                partner = t.target_id if t.proposer_id == agent_id else t.proposer_id
                history.setdefault(partner, []).append(t)
        return history

    def get_partner_summary(self, agent_id: int) -> dict[int, dict]:
        """Lifetime per-partner stats from full trade history."""
        summary: dict[int, dict] = {}
        for t in self.trade_history:
            if t.status == "rejected":
                continue
            if t.proposer_id != agent_id and t.target_id != agent_id:
                continue
            partner = t.target_id if t.proposer_id == agent_id else t.proposer_id
            if partner not in summary:
                summary[partner] = {
                    "trades": 0,
                    "defections_by_them": 0,
                    "defections_by_me": 0,
                    "last_defection_round": None,
                }
            s = summary[partner]
            s["trades"] += 1
            if t.defected_by == partner:
                s["defections_by_them"] += 1
                s["last_defection_round"] = t.round_num
            elif t.defected_by == agent_id:
                s["defections_by_me"] += 1
        return summary

    def get_exchange_rates(self, window: int = 5) -> dict[str, dict]:
        recent = [t for t in self.trade_history
                  if t.round_num > self.round_num - window
                  and t.status in ("completed", "mediated")]
        rates: dict[str, dict] = {}
        for t in recent:
            key = f"{t.offer_good}_for_{t.want_good}"
            rates.setdefault(key, {"ratios": [], "trade_count": 0})
            if t.want_qty > 0:
                rates[key]["ratios"].append(t.offer_qty / t.want_qty)
            rates[key]["trade_count"] += 1
        for key in rates:
            ratios = rates[key]["ratios"]
            rates[key]["avg_ratio"] = round(sum(ratios) / len(ratios), 1) if ratios else 0
            del rates[key]["ratios"]
        return rates

    def can_deliver_asset(self, agent_id: int, asset: str, qty: int) -> bool:
        return self.inventories[agent_id].get(asset, 0) >= qty

    def transfer_goods(self, from_id: int, to_id: int, good: str, qty: int) -> bool:
        if self.inventories[from_id][good] < qty:
            return False
        self.inventories[from_id][good] -= qty
        self.inventories[to_id][good] += qty
        return True

