"""Assembles the final prompt string for each agent call.

Loads templates from prompts/, selects the correct mechanism block and stage,
fills all {variable} placeholders from current market + agent state.
"""
from __future__ import annotations
from pathlib import Path
from typing import TYPE_CHECKING

from ..config import (
    MEDIATION_FEE, MEMORY_WINDOW, GOV_WARNING_EXPIRY,
    GOV_CLEAN_ROUNDS_TO_DEESCALATE,
    SANCTION_COST_RATIO,
)

if TYPE_CHECKING:
    from .market import Market, Contract, TradeOffer

PROMPTS_DIR = Path(__file__).parent.parent.parent / "prompts"


def _load(filename: str) -> str:
    return (PROMPTS_DIR / filename).read_text()


# Cache templates at import time
_BASE = _load("base_agent.txt")
_BASELINE = _load("baseline.txt")
_REPUTATION = _load("reputation.txt")
_CONTRACTING = _load("contracting.txt")
_MEDIATION = _load("mediation.txt")
_GOVERNANCE = _load("governance.txt")
_NETWORK_REWIRING = _load("network_rewiring.txt")
_SANCTION = _load("sanction.txt")
_LOCAL_REPUTATION = _load("local_reputation.txt")


def _extract_stage(template: str, stage_label: str) -> str:
    """Extract a single STAGE N block from a multi-stage template.

    Template format:
        ----
        STAGE N: TITLE
        Description lines (skipped)
        ----
        Content (extracted)
    """
    lines = template.splitlines(keepends=True)
    in_stage = False
    past_header = False
    result = []
    for line in lines:
        if f"STAGE {stage_label}" in line:
            in_stage = True
        elif in_stage and not past_header:
            if line.strip() and set(line.strip()).issubset(set("-=")):
                past_header = True
        elif in_stage and past_header:
            if "STAGE" in line and f"STAGE {stage_label}" not in line:
                break
            if line.strip() and set(line.strip()).issubset(set("-=")):
                continue
            result.append(line)
    return "".join(result).strip()


def _fmt_inventory(market: "Market", agent_id: int) -> tuple[str, str, str]:
    inv = market.inventories[agent_id]
    return str(inv.get("A", 0)), str(inv.get("B", 0)), str(inv.get("C", 0))


def _fmt_partner_summary(market: "Market", agent_id: int) -> str:
    summary = market.get_partner_summary(agent_id)
    if not summary:
        return "  No trade history yet."
    lines = []
    for partner_id, s in sorted(summary.items()):
        total = s["trades"]
        theirs = s["defections_by_them"]
        rate = f"{theirs}/{total}"
        pct = f" ({100 * theirs // total}%)" if total > 0 else ""
        last = f", last defection round {s['last_defection_round']}" if s["last_defection_round"] else ""
        lines.append(f"  Agent {partner_id}: {total} trades, {rate} defections by them{pct}{last}")
    return "\n".join(lines)


def _fmt_partner_history(market: "Market", agent_id: int) -> str:
    history = market.get_partner_history(agent_id, window=MEMORY_WINDOW)
    if not history:
        return "  No trade history yet."
    lines = []
    for partner_id, trades in history.items():
        lines.append(f"  Agent {partner_id}:")
        for t in trades[-5:]:
            outcome = t.status.upper()
            lines.append(
                f"    Round {t.round_num}: offered {t.offer_qty}×{t.offer_good} "
                f"for {t.want_qty}×{t.want_good} — {outcome}"
            )
    return "\n".join(lines)


def _fmt_inbox(market: "Market", agent_id: int) -> str:
    msgs = market.private_inboxes[agent_id]
    if not msgs:
        return "  (none)"
    return "\n".join(f"  [Agent {m.sender_id}]: {m.text}" for m in msgs)


def _fmt_public_feed(market: "Market") -> str:
    if not market.public_feed:
        return "  (none)"
    def _sender_label(sender_id: int) -> str:
        return "System" if sender_id < 0 else f"Agent {sender_id}"
    return "\n".join(
        f"  [{_sender_label(m.sender_id)}, Round {m.round_num}]: {m.text}"
        for m in market.public_feed
    )


def _fmt_neighbors(market: "Market", agent_id: int, specialties: dict[int, str]) -> str:
    neighbors = sorted(market.network.get(agent_id, set()))
    if not neighbors:
        return "  (none)"
    lines = []
    for nid in neighbors:
        good = specialties.get(nid, "?")
        lines.append(f"  Agent {nid} (produces Good {good})")
    return "\n".join(lines)


def _fmt_pending_offers(market: "Market", agent_id: int) -> str:
    offers = market.pending_offers[agent_id]
    if not offers:
        return "  (none)"
    return "\n".join(
        f"  Trade {o.trade_id}: Agent {o.proposer_id} offers "
        f"{o.offer_qty}×Good {o.offer_good}, wants {o.want_qty}×Good {o.want_good}"
        f"{' (proposer delegated to mediator)' if o.proposer_delegated else ''}"
        for o in offers
    )


def _fmt_exchange_rates(market: "Market") -> str:
    rates = market.get_exchange_rates()
    if not rates:
        return "  No recent trades yet."
    lines = []
    for key, info in rates.items():
        offer_good, want_good = key.split("_for_")
        if info["trade_count"] > 0:
            lines.append(
                f"  {offer_good}→{want_good}: avg {info['avg_ratio']:.1f}:1 "
                f"({info['trade_count']} trades)"
            )
    return "\n".join(lines) if lines else "  No recent trades yet."


def _fmt_reputation_table(market: "Market", agent_id: int) -> str:
    lines = []
    for aid, score in market.system_reputation.items():
        if aid == agent_id:
            continue
        counts = market._trade_counts[aid]
        lines.append(
            f"  Agent {aid}:  {score:.2f}  "
            f"({counts['success']}/{counts['total']} trades delivered)"
        )
    return "\n".join(lines) if lines else "  No trade data yet."


def _fmt_public_mentions(market: "Market", agent_id: int) -> str:
    mentions: dict[int, list[str]] = {}
    for msg in market.public_feed:
        # Heuristic: public mentions about other agents
        for aid in market.agent_ids:
            if aid != agent_id and f"Agent {aid}" in msg.text:
                mentions.setdefault(aid, []).append(
                    f"  [Round {msg.round_num}, Agent {msg.sender_id}]: \"{msg.text}\""
                )
    if not mentions:
        return "  No public mentions yet."
    lines = []
    for aid, stmts in mentions.items():
        lines.append(f"  Agent {aid}:")
        lines.extend(stmts[-3:])
    return "\n".join(lines)


def _fmt_message_history(market: "Market", agent_id: int) -> str:
    """Format rolling public message history (last N rounds) for local reputation."""
    messages = market.get_message_history()
    if not messages:
        return "  (no public messages yet)"
    lines = []
    for msg in messages:
        if msg.sender_id == agent_id:
            continue
        sender = f"Agent {msg.sender_id}" if msg.sender_id >= 0 else "System"
        lines.append(f"  [Round {msg.round_num}, {sender}]: \"{msg.text}\"")
    return "\n".join(lines) if lines else "  (no public messages from other agents)"


def _fmt_recent_sanctions(market: "Market") -> str:
    if not hasattr(market, "sanction_log") or not market.sanction_log:
        return "  No sanctions yet."
    recent = [s for s in market.sanction_log if s["round"] >= market.round_num - 5]
    if not recent:
        return "  No recent sanctions."
    lines = []
    for s in recent[-10:]:
        lines.append(f"  Round {s['round']}: Agent {s['target']} sanctioned (lost {s['damage']} utility)")
    return "\n".join(lines)


def _fmt_active_contracts(contracts: list["Contract"], agent_id: int) -> str:
    if not contracts:
        return "  (none)"
    def fmt_asset(qty: int, asset: str) -> str:
        return f"{qty}×Good {asset}"

    lines = []
    for c in contracts:
        if c.proposer_id == agent_id:
            my_del = fmt_asset(c.proposer_delivers_qty, c.proposer_delivers_good)
            their_del = fmt_asset(c.counterparty_delivers_qty, c.counterparty_delivers_good)
            partner = c.counterparty_id
        else:
            my_del = fmt_asset(c.counterparty_delivers_qty, c.counterparty_delivers_good)
            their_del = fmt_asset(c.proposer_delivers_qty, c.proposer_delivers_good)
            partner = c.proposer_id
        lines.append(
            f"  Contract {c.contract_id}:\n"
            f"    You deliver:  {my_del}  →  Agent {partner}\n"
            f"    They deliver: {their_del}  →  You\n"
            f"    Breach penalty: {c.breach_penalty} utility points\n"
            f"    Status: ACTIVE — both parties signed"
        )
    return "\n".join(lines)


def _fmt_mediator_designs(market: "Market") -> str:
    if not market.mediator_designs:
        return "  No designs submitted yet."
    lines = []
    for d in market.mediator_designs:
        lines.append(
            f"  Design by Agent {d.designer_id}:\n"
            f"    2 delegating → {d.action_both}\n"
            f"    1 delegating → {d.action_one}\n"
            f"    Rationale: \"{d.rationale}\""
        )
    return "\n".join(lines)


def _fmt_governance_notice(market: "Market", agent_id: int) -> tuple[str, str]:
    if not market.governance_states:
        return "", ""

    state = market.governance_states.get(agent_id)
    if state is None:
        return "", ""

    signal_names = {
        "D1_defection_rate": "D1: High defection rate",
        "D4_predatory_targeting": "D4: Predatory targeting",
    }
    signal_list = ", ".join(signal_names.get(s, s) for s in state.triggered_signals) or "None"

    if state.status == "active":
        status_block = "  Status: CLEAR — no regulatory action. Continue trading normally."
        guidance = "Maintain cooperative behavior to avoid regulatory scrutiny."
    elif state.status == "warning":
        rounds_needed = max(0, GOV_WARNING_EXPIRY - state.clean_rounds)
        status_block = (
            f"  Status: UNDER REVIEW — the regulator has flagged your recent activity.\n"
            f"  Signals detected: {signal_list}\n"
            f"  WARNING: continued flagged behavior will result in fines.\n"
            f"  Clean rounds to clear: {rounds_needed}"
        )
        guidance = (
            f"To return to CLEAR status: complete {GOV_WARNING_EXPIRY} consecutive rounds with zero defections "
            "and maintain normal production/trade levels."
        )
    elif state.status == "fined":
        from ..config import GOV_FINE_SCHEDULE
        fine_amount = GOV_FINE_SCHEDULE.get(state.fine_tier, 0)
        rounds_to_drop = max(0, GOV_CLEAN_ROUNDS_TO_DEESCALATE - state.clean_rounds)
        status_block = (
            f"  Status: PENALISED — Tier {state.fine_tier} fine active.\n"
            f"  Utility penalty this round: -{fine_amount}\n"
            f"  Signals detected: {signal_list}\n"
            f"  Clean rounds toward de-escalation: {state.clean_rounds}/{GOV_CLEAN_ROUNDS_TO_DEESCALATE}\n"
            f"  WARNING: continued violations will escalate. Tier 3 leads to suspension."
        )
        guidance = (
            f"To reduce your fine tier: maintain {rounds_to_drop} more consecutive clean rounds "
            f"(no oracle signals). Each {GOV_CLEAN_ROUNDS_TO_DEESCALATE} clean rounds drops "
            f"your tier by 1. Reaching Tier 0 clears all fines."
        )
    elif state.status == "suspended":
        status_block = (
            f"  Status: SUSPENDED — you are removed from the market.\n"
            f"  Rounds remaining: {state.suspension_rounds_left}\n"
            f"  You cannot produce or trade until your suspension expires."
        )
        guidance = ""
    else:
        status_block = f"  Status: {state.status.upper()}"
        guidance = ""

    return status_block, guidance


def _build_mechanism_block(
    mechanisms: list[str],
    market: "Market",
    agent_id: int,
    stage_overrides: dict[str, str] | None = None,
) -> str:
    """Compose mechanism block from active mechanisms. stage_overrides: {mechanism: stage_label}"""
    if not mechanisms:
        return _BASELINE

    blocks = []
    for mech in mechanisms:
        if mech == "reputation":
            block = _REPUTATION
            block = block.replace("{system_reputation_table}", _fmt_reputation_table(market, agent_id))
            block = block.replace("{public_mentions_table}", _fmt_public_mentions(market, agent_id))
            blocks.append(block)

        elif mech == "contracting":
            stage = (stage_overrides or {}).get("contracting", "3")
            raw = _extract_stage(_CONTRACTING, stage)

            if stage == "2":
                # Fill contract review variables from pending contracts
                pending = [
                    c for c in market.contracts.values()
                    if c.counterparty_id == agent_id and c.status == "proposed"
                ]
                if pending:
                    c = pending[0]
                    raw = raw.replace("{proposer_id}", str(c.proposer_id))
                    raw = raw.replace("{their_delivery_good}", c.proposer_delivers_good)
                    raw = raw.replace("{their_delivery_qty}", str(c.proposer_delivers_qty))
                    raw = raw.replace("{my_delivery_good}", c.counterparty_delivers_good)
                    raw = raw.replace("{my_delivery_qty}", str(c.counterparty_delivers_qty))
                    raw = raw.replace("{penalty}", str(c.breach_penalty))
                    raw = raw.replace("{execution_round}", str(c.execution_round))
                    raw = raw.replace("{contract_id}", c.contract_id)

            elif stage == "3":
                active = [
                    c for c in market.contracts.values()
                    if (c.proposer_id == agent_id or c.counterparty_id == agent_id)
                    and c.status == "signed"
                    and c.execution_round == market.round_num
                ]
                raw = raw.replace("{active_contracts_list}", _fmt_active_contracts(active, agent_id))

            elif stage == "4":
                rejected = [
                    c for c in market.contracts.values()
                    if c.proposer_id == agent_id and c.status == "rejected"
                    and c.execution_round == market.round_num
                ]
                if rejected:
                    c = rejected[0]
                    raw = raw.replace("{proposer_id}", str(c.proposer_id))
                    raw = raw.replace("{your_delivery_good}", c.proposer_delivers_good)
                    raw = raw.replace("{your_delivery_qty}", str(c.proposer_delivers_qty))
                    raw = raw.replace("{their_delivery_good}", c.counterparty_delivers_good)
                    raw = raw.replace("{their_delivery_qty}", str(c.counterparty_delivers_qty))
                    raw = raw.replace("{penalty}", str(c.breach_penalty))

            blocks.append(raw)

        elif mech == "mediation":
            stage = (stage_overrides or {}).get("mediation", "3")
            raw = _extract_stage(_MEDIATION, stage)

            active = market.active_mediator
            fee = str(MEDIATION_FEE)

            if stage == "1":
                raw = raw.replace("{mediation_fee}", fee)

            elif stage == "2":
                raw = raw.replace("{mediator_designs_list}", _fmt_mediator_designs(market))

            elif stage == "3":
                both = active.action_both if active else "execute_fair"
                one = active.action_one if active else "cancel"
                raw = raw.replace("{mediator_action_both}", both)
                raw = raw.replace("{mediator_action_one}", one)
                raw = raw.replace("{mediation_fee}", fee)
                raw = raw.replace("{pending_trades_list}", _fmt_pending_offers(market, agent_id))

            blocks.append(raw)

        elif mech == "governance":
            block = _GOVERNANCE
            status_block, guidance = _fmt_governance_notice(market, agent_id)
            block = block.replace("{governance_status_block}", status_block)
            block = block.replace("{governance_guidance}", guidance)
            blocks.append(block)

        elif mech == "network_rewiring":
            block = _NETWORK_REWIRING
            block = block.replace("{neighbor_count}", str(len(market.network.get(agent_id, set()))))
            blocks.append(block)

        elif mech == "sanction":
            block = _SANCTION
            block = block.replace("{sanction_cost_ratio}", str(SANCTION_COST_RATIO))
            block = block.replace("{recent_sanctions_log}", _fmt_recent_sanctions(market))
            blocks.append(block)

        elif mech == "local_reputation":
            block = _LOCAL_REPUTATION
            block = block.replace("{message_history}", _fmt_message_history(market, agent_id))
            blocks.append(block)

    return "\n\n".join(blocks)


def _build_mechanism_actions(mechanisms: list[str]) -> str:
    actions = []
    if "contracting" in mechanisms:
        actions.extend([
            '  {"action": "propose_contract", "target": <neighbor_id>, "terms": {"i_deliver": {"good": "A"|"B"|"C", "quantity": int}, "they_deliver": {"good": "A"|"B"|"C", "quantity": int}, "breach_penalty": int, "execution_round": int}}',
            '  {"action": "sign_contract", "contract_id": "..."}',
            '  {"action": "reject_contract", "contract_id": "..."}',
        ])
    if "mediation" in mechanisms:
        actions.append('  {"action": "delegate_to_mediator", "trade_id": "..."}')
    if "network_rewiring" in mechanisms:
        actions.extend([
            '  {"action": "sever_link",   "target": <neighbor_id>}',
            '  {"action": "request_link", "target": <any_agent_id>}',
        ])
    if "sanction" in mechanisms:
        actions.append('  {"action": "sanction", "target": <any_agent_id>, "amount": <int>}  [you spend amount, target loses amount × 3]')

    if not actions:
        return ""

    return (
        "Available actions for active mechanisms:\n"
        + "\n".join(actions)
        + "\n"
    )


def build_prompt(
    agent_id: int,
    specialty: str,
    needs: tuple[str, str],
    last_utility: float,
    total_utility: float,
    metrics: dict[str, float],
    market: "Market",
    mechanisms: list[str],
    stage_overrides: dict[str, str] | None = None,
    specialties: dict[int, str] | None = None,
    round_num: int = 1,
    total_rounds: int = 30,
) -> str:
    inv_a, inv_b, inv_c = _fmt_inventory(market, agent_id)

    mechanism_block = _build_mechanism_block(mechanisms, market, agent_id, stage_overrides)
    mechanism_actions = _build_mechanism_actions(mechanisms)

    prompt = _BASE
    prompt = prompt.replace("{agent_id}", str(agent_id))
    prompt = prompt.replace("{specialty}", specialty)
    prompt = prompt.replace("{need_1}", needs[0])
    prompt = prompt.replace("{need_2}", needs[1])
    prompt = prompt.replace("{inv_A}", inv_a)
    prompt = prompt.replace("{inv_B}", inv_b)
    prompt = prompt.replace("{inv_C}", inv_c)
    prompt = prompt.replace("{last_utility}", f"{last_utility:.1f}")
    prompt = prompt.replace("{total_utility}", f"{total_utility:.1f}")
    prompt = prompt.replace("{round_num}", str(round_num))
    prompt = prompt.replace("{partner_summary}", _fmt_partner_summary(market, agent_id))
    prompt = prompt.replace("{partner_history}", _fmt_partner_history(market, agent_id))
    prompt = prompt.replace("{private_inbox}", _fmt_inbox(market, agent_id))
    prompt = prompt.replace("{public_feed}", _fmt_public_feed(market))
    prompt = prompt.replace("{pending_offers}", _fmt_pending_offers(market, agent_id))
    prompt = prompt.replace("{exchange_rates}", _fmt_exchange_rates(market))
    prompt = prompt.replace("{neighbors}", _fmt_neighbors(market, agent_id, specialties or {}))
    prompt = prompt.replace("{mechanism_block}", mechanism_block)
    prompt = prompt.replace("{mechanism_actions}", mechanism_actions)

    return prompt
