"""Assembles the final prompt string for each agent call.

Loads templates from prompts/, selects the correct mechanism block and stage,
fills all {variable} placeholders from current market + agent state.
"""
from __future__ import annotations
from pathlib import Path
from typing import TYPE_CHECKING

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


def _extract_stage(template: str, stage_label: str) -> str:
    """Extract a single STAGE N block from a multi-stage template."""
    lines = template.splitlines(keepends=True)
    in_stage = False
    result = []
    for line in lines:
        if f"STAGE {stage_label}" in line and "---" in line:
            in_stage = True
        elif in_stage and line.startswith("---") and "STAGE" in line:
            break
        elif in_stage:
            result.append(line)
    return "".join(result).strip()


def _fmt_inventory(market: "Market", agent_id: int) -> tuple[str, str, str]:
    inv = market.inventories[agent_id]
    return str(inv.get("A", 0)), str(inv.get("B", 0)), str(inv.get("C", 0))


def _fmt_partner_history(market: "Market", agent_id: int) -> str:
    history = market.get_partner_history(agent_id)
    if not history:
        return "  No trade history yet."
    lines = []
    for partner_id, trades in history.items():
        lines.append(f"  Agent {partner_id}:")
        for t in trades[-5:]:
            outcome = t.status.upper()
            lines.append(
                f"    Round {t.round_num}: offered {t.offer_qty}×{t.offer_good} "
                f"for {t.price} tokens — {outcome}"
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
    return "\n".join(
        f"  [Agent {m.sender_id}, Round {m.round_num}]: {m.text}"
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
        f"{o.offer_qty}×Good {o.offer_good} for {o.price} tokens"
        f"{' (seller delegated to mediator)' if o.proposer_delegated else ''}"
        for o in offers
    )


def _fmt_market_prices(market: "Market") -> str:
    prices = market.get_market_prices()
    lines = []
    for good, info in prices.items():
        if info["avg_price"] is not None:
            lines.append(f"  Good {good}: avg {info['avg_price']:.1f} tokens/unit ({info['trade_count']} trades)")
        else:
            lines.append(f"  Good {good}: no recent trades")
    return "\n".join(lines)


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
    for msg in market.public_feed + [
        m for inbox in market.private_inboxes.values() for m in inbox
        if m.channel == "public"
    ]:
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


def _fmt_active_contracts(contracts: list["Contract"], agent_id: int) -> str:
    if not contracts:
        return "  (none)"
    def fmt_asset(qty: int, asset: str) -> str:
        return f"{qty} tokens" if asset == "TOKENS" else f"{qty}×Good {asset}"

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
            fee = str(1)  # from config; avoid circular import

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

    return "\n\n".join(blocks)


def _build_mechanism_actions(mechanisms: list[str], agent_id: int) -> str:
    actions = []
    if "contracting" in mechanisms:
        actions.extend([
            f'  {{"action": "propose_contract", "target": "{agent_id}", "terms": {{"i_deliver": {{"good": "A"|"B"|"C"|"TOKENS", "quantity": int}}, "they_deliver": {{"good": "A"|"B"|"C"|"TOKENS", "quantity": int}}, "breach_penalty": int, "execution_round": int}}}}',
            '  {"action": "sign_contract", "contract_id": "..."}',
            '  {"action": "reject_contract", "contract_id": "..."}',
        ])
    if "mediation" in mechanisms:
        actions.append('  {"action": "delegate_to_mediator", "trade_id": "..."}')

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
    mechanism_actions = _build_mechanism_actions(mechanisms, agent_id)

    prompt = _BASE
    prompt = prompt.replace("{agent_id}", str(agent_id))
    prompt = prompt.replace("{specialty}", specialty)
    prompt = prompt.replace("{need_1}", needs[0])
    prompt = prompt.replace("{need_2}", needs[1])
    prompt = prompt.replace("{inv_A}", inv_a)
    prompt = prompt.replace("{inv_B}", inv_b)
    prompt = prompt.replace("{inv_C}", inv_c)
    prompt = prompt.replace("{tokens}", str(market.tokens.get(agent_id, 0)))
    prompt = prompt.replace("{last_utility}", f"{last_utility:.1f}")
    prompt = prompt.replace("{total_utility}", f"{total_utility:.1f}")
    prompt = prompt.replace("{sustainability:.2f}", f"{metrics.get('sustainability', 0):.2f}")
    prompt = prompt.replace("{peace:.2f}", f"{metrics.get('peace', 0):.2f}")
    prompt = prompt.replace("{round_num}", str(round_num))
    prompt = prompt.replace("{total_rounds}", str(total_rounds))
    prompt = prompt.replace("{rounds_remaining}", str(total_rounds - round_num))
    prompt = prompt.replace("{partner_history}", _fmt_partner_history(market, agent_id))
    prompt = prompt.replace("{private_inbox}", _fmt_inbox(market, agent_id))
    prompt = prompt.replace("{public_feed}", _fmt_public_feed(market))
    prompt = prompt.replace("{pending_offers}", _fmt_pending_offers(market, agent_id))
    prompt = prompt.replace("{market_prices}", _fmt_market_prices(market))
    prompt = prompt.replace("{neighbors}", _fmt_neighbors(market, agent_id, specialties or {}))
    prompt = prompt.replace("{mechanism_block}", mechanism_block)
    prompt = prompt.replace("{mechanism_actions}", mechanism_actions)

    return prompt
