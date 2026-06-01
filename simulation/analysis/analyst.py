"""Unified analyst: cross-condition comparison + behavioral deep-dive with traces.

Produces one holistic report combining:
1. Summary statistics across all conditions
2. Troll resilience metrics
3. Sampled CoT traces and quotes showing interesting behaviors
"""
from __future__ import annotations
import json
import os
from pathlib import Path
from datetime import datetime

import numpy as np
import anthropic

from .. import config
from ..config import ANALYST_ENDPOINT, ANALYST_MODEL, COOPERATION_THRESHOLD, CONDITIONS

OUT_DIR = Path(__file__).parent.parent / "data"
METRICS = ["sustainability", "peace", "gini"]
INTERMEDIATE = ["whistleblowing_rate", "false_accusation_rate", "warning_accuracy"]

_MECHANISM_LABELS = {
    "B":  "baseline (no mechanisms)",
    "GR": "global reputation (system-computed scores visible to all)",
    "C":  "contracting (binding contracts, 6 utility breach penalty)",
    "M":  "mediation (agent-designed mediator, free delegation)",
    "G":  "governance (oracle detects defection >40% and predatory targeting, escalates to fines/suspension)",
    "NR": "network rewiring + local reputation (sever/request links, 10-round gossip history, no system scores)",
    "S":  "costly sanctions (spend 1 utility → target loses 3, anonymous, publicly announced)",
}

client = anthropic.Anthropic(
    api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
    base_url=ANALYST_ENDPOINT,
)


# ── Data loading ─────────────────────────────────────────────────────────────

def _load_runs(condition: str) -> list[dict]:
    files = sorted(config.DATA_DIR.glob(f"{condition}_run_*.json"))
    if not files:
        files = sorted(config.DATA_DIR.glob(f"{condition}_t*_run_*.json"))
    runs = []
    for f in files:
        with open(f) as fp:
            runs.append(json.load(fp))
    return runs


def _load_traces(condition: str) -> list[dict]:
    """Load traces from all matching trace files for a condition."""
    files = sorted(config.DATA_DIR.glob(f"{condition}_*_traces.jsonl"))
    traces = []
    for f in files:
        with open(f) as fp:
            for line in fp:
                if line.strip():
                    traces.append(json.loads(line))
    return traces


def _get_troll_ids(run: dict) -> set[str]:
    return set(str(tid) for tid in run.get("session_log", {}).get("troll_ids", []))


# ── Summary statistics ───────────────────────────────────────────────────────

def _summarize_all() -> dict:
    summary = {}
    for condition in CONDITIONS:
        runs = _load_runs(condition)
        if not runs:
            continue
        cond = {}

        for metric in METRICS + INTERMEDIATE:
            all_vals = [
                rnd["metrics"].get(metric, 0)
                for run in runs for rnd in run["rounds"]
                if rnd["metrics"].get(metric) is not None
            ]
            cond[metric] = {
                "mean": round(float(np.mean(all_vals)), 4) if all_vals else None,
                "final": round(float(np.mean([
                    run["rounds"][-1]["metrics"].get(metric, 0) for run in runs
                ])), 4),
            }

        cooperative = sum(
            1 for run in runs
            if all(run["rounds"][-1]["metrics"].get(m, 0) > COOPERATION_THRESHOLD for m in ["sustainability", "peace"])
        )
        cond["cooperation_achieved"] = f"{cooperative}/{len(runs)} runs"

        # Troll metrics
        troll_ids = _get_troll_ids(runs[0])
        if troll_ids:
            n_rounds = len(runs[0]["rounds"])
            half = n_rounds // 2
            troll_trades_last_half = 0
            last_half_rounds = 0
            total_troll_def = 0
            for run in runs:
                for r, rnd in enumerate(run["rounds"]):
                    trades = rnd.get("trades", [])
                    for t in trades:
                        involves_troll = str(t["proposer"]) in troll_ids or str(t["target"]) in troll_ids
                        if involves_troll:
                            if t.get("defected_by") is not None:
                                total_troll_def += 1
                            if r >= half:
                                troll_trades_last_half += 1
                last_half_rounds += (n_rounds - half)
            cond["troll_defections"] = total_troll_def
            cond["avg_troll_trades_last_half"] = round(troll_trades_last_half / max(last_half_rounds, 1), 2)

        # Per-round utility (non-troll)
        util_vals = []
        for run in runs:
            tids = _get_troll_ids(run)
            for rnd in run["rounds"]:
                utils = rnd.get("utilities", {})
                non_troll = [float(v) for k, v in utils.items() if k not in tids]
                if non_troll:
                    util_vals.append(np.mean(non_troll))
        cond["mean_utility"] = round(float(np.mean(util_vals)), 2) if util_vals else 0.0

        summary[condition] = cond
    return summary


def _build_round_table(condition: str, runs: list[dict]) -> str:
    """Compact per-round table for one condition."""
    n_rounds = len(runs[0]["rounds"])
    troll_ids = _get_troll_ids(runs[0])
    lines = [f"{'Rnd':>3} | {'Peace':>6} | {'Sustain':>7} | {'Gini':>5} | {'Defect':>6} | {'Trades':>6} | {'AvgUtil':>7}"]
    lines.append(f"{'-'*3}-+-{'-'*6}-+-{'-'*7}-+-{'-'*5}-+-{'-'*6}-+-{'-'*6}-+-{'-'*7}")
    for r in range(n_rounds):
        peace, sust, gini, defects, trades, utils = [], [], [], [], [], []
        for run in runs:
            if r >= len(run["rounds"]):
                continue
            rnd = run["rounds"][r]
            peace.append(rnd["metrics"].get("peace", 0))
            sust.append(rnd["metrics"].get("sustainability", 0))
            gini.append(rnd["metrics"].get("gini", 0))
            defects.append(rnd.get("defections", 0))
            trades.append(rnd.get("trade_count", 0))
            rnd_utils = rnd.get("utilities", {})
            non_troll = [float(v) for k, v in rnd_utils.items() if k not in troll_ids]
            if non_troll:
                utils.append(np.mean(non_troll))
        lines.append(
            f"{r+1:>3} | {np.mean(peace):>6.3f} | {np.mean(sust):>7.3f} | {np.mean(gini):>5.3f} | "
            f"{np.mean(defects):>6.1f} | {np.mean(trades):>6.1f} | {np.mean(utils):>7.2f}"
        )
    return "\n".join(lines)


# ── Trace sampling ───────────────────────────────────────────────────────────

def _sample_interesting_traces(condition: str, runs: list[dict], max_per_condition: int = 8) -> list[str]:
    """Sample interesting CoT traces: first defection, troll encounters, late-game behavior."""
    traces = _load_traces(condition)
    if not traces:
        return []

    troll_ids = _get_troll_ids(runs[0]) if runs else set()
    n_rounds = len(runs[0]["rounds"]) if runs else 30

    # Priority: round 1, first big defection round, mid-game, final rounds
    rounds_data = runs[0]["rounds"] if runs else []
    defection_rounds = sorted(
        [(r["round"], r.get("defections", 0)) for r in rounds_data if r.get("defections", 0) > 2],
        key=lambda x: -x[1]
    )
    priority_rounds = {1, 2, n_rounds, n_rounds - 1}
    if defection_rounds:
        priority_rounds.add(defection_rounds[0][0])
    priority_rounds.add(n_rounds // 2)

    # Find traces mentioning trolls or defection
    interesting = []
    regular = []
    for t in traces:
        reasoning = t.get("reasoning", "")
        if not reasoning or len(reasoning) < 50:
            continue
        is_interesting = (
            t["round"] in priority_rounds
            or any(f"Agent {tid}" in reasoning for tid in troll_ids)
            or "defect" in reasoning.lower()
            or "trust" in reasoning.lower()
            or "sever" in reasoning.lower()
            or "punish" in reasoning.lower()
            or "sanction" in reasoning.lower()
        )
        entry = (
            f"[Round {t['round']}, Agent {t['agent_id']} ({t['specialty']} specialist), {t['phase']}]\n"
            f"{reasoning[:600]}"
        )
        if is_interesting:
            interesting.append((t["round"], entry))
        else:
            regular.append((t["round"], entry))

    # Deduplicate by round — max 2 per round
    seen_rounds: dict[int, int] = {}
    selected = []
    for rnd, entry in sorted(interesting, key=lambda x: x[0]):
        count = seen_rounds.get(rnd, 0)
        if count < 2:
            selected.append(entry)
            seen_rounds[rnd] = count + 1
        if len(selected) >= max_per_condition:
            break

    if len(selected) < max_per_condition:
        for rnd, entry in regular[:max_per_condition - len(selected)]:
            selected.append(entry)

    return selected


# ── Prompt construction ──────────────────────────────────────────────────────

def _build_analyst_prompt(summary: dict, round_tables: dict[str, str], traces: dict[str, list[str]]) -> str:
    summary_text = json.dumps(summary, indent=2)

    tables_block = ""
    for cond in CONDITIONS:
        if cond in round_tables:
            label = _MECHANISM_LABELS.get(cond, cond)
            tables_block += f"\n### {cond} — {label}\n{round_tables[cond]}\n"

    traces_block = ""
    for cond in CONDITIONS:
        if cond in traces and traces[cond]:
            traces_block += f"\n### {cond} — Sample Agent Reasoning\n"
            traces_block += "\n\n".join(traces[cond])
            traces_block += "\n"

    return f"""You are a research analyst reviewing a multi-agent marketplace simulation comparing 7 institutional mechanisms for sustaining cooperation among self-interested LLM agents.

SETUP:
- 18 LLM agents (GPT-5.4-nano) + 2 troll agents (deterministic defectors, IDs 18-19) = 20 total
- 3 perishable goods (A, B, C), barter economy, 30 rounds
- Production cost: 1 utility/unit, consumption gain: +3 utility/needed unit, 20% spoilage/round
- Agents see only "Round N" — no total rounds, no market health metrics
- Trolls defect on ALL trades, propose trades to all neighbors, broadcast lies
- All metrics exclude trolls

CONDITIONS:
{json.dumps(_MECHANISM_LABELS, indent=2)}

INFORMATION GRADIENT (B → NR → GR):
- B: private experience only (lifetime partner summary + last 5 rounds detail)
- NR: private experience + 10-round gossip history + network reshaping (sever/request links)
- GR: private experience + system-computed reputation scores visible to all

SUMMARY STATISTICS:
{summary_text}

PER-ROUND TABLES:
{tables_block}

AGENT REASONING TRACES (sampled for interesting behavior — defection decisions, troll encounters, trust reasoning):
{traces_block}

Write a single comprehensive report with these sections:

1. **EXECUTIVE SUMMARY** (3-4 sentences): Which mechanisms worked, which failed, what's the headline finding?

2. **MECHANISM RANKING**: Rank all 7 conditions by overall effectiveness. For each, state: cooperation rate, mean utility, troll isolation (if applicable), and one-line verdict.

3. **TROLL RESILIENCE**: Which mechanisms actually isolated trolls? How fast? Compare avg troll trades/round in the last half across conditions. Why did some mechanisms fail to isolate trolls despite having information?

4. **INFORMATION GRADIENT (B → NR → GR)**: Does more information lead to better outcomes? GR gives a system score, NR gives gossip + structural power, B gives nothing. What do the results show?

5. **BEHAVIORAL INSIGHTS** (use the CoT traces): Quote specific agent reasoning that shows:
   - How agents decide to cooperate vs defect
   - How agents react to being defected on (especially by trolls)
   - Whether agents use available mechanisms strategically or ignore them
   - Any surprising behaviors, emergent norms, or interesting failures
   Use exact quotes from the traces, citing round and agent ID.

6. **MECHANISM-SPECIFIC FINDINGS**: For each condition, what worked and what didn't? Why did C (contracting) produce such low utility? Why didn't M (mediation) agents delegate? Did S (sanctions) agents actually punish?

7. **IMPLICATIONS**: What does this mean for the research question "which mechanism sustains cooperation under adversarial pressure?" What should be tested next?

Be specific — cite numbers and quote traces. Flag where 1 run is insufficient for statistical claims.
"""


def run_analyst(model: str = ANALYST_MODEL, save: bool = True) -> str:
    print("Loading run logs...")
    all_data: dict[str, list[dict]] = {}
    for condition in CONDITIONS:
        runs = _load_runs(condition)
        if runs:
            all_data[condition] = runs

    if not all_data:
        return "No run logs found. Run the simulation first."

    print(f"Loaded: {list(all_data.keys())}")

    summary = _summarize_all()
    print("Summary computed.")

    round_tables = {}
    for cond, runs in all_data.items():
        round_tables[cond] = _build_round_table(cond, runs)

    traces = {}
    for cond, runs in all_data.items():
        traces[cond] = _sample_interesting_traces(cond, runs)
        n = len(traces[cond])
        if n:
            print(f"  [{cond}] {n} interesting traces sampled")

    print("Calling analyst LLM...")
    prompt = _build_analyst_prompt(summary, round_tables, traces)

    response = client.messages.create(
        model=model,
        max_tokens=8192,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )
    report = response.content[0].text

    if save:
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        model_tag = config.DATA_DIR.name
        out_path = OUT_DIR / f"analyst_report_{model_tag}_{timestamp}.md"
        with open(out_path, "w") as f:
            f.write(f"# Analyst Report — {model_tag}\n\n")
            f.write(f"Generated: {datetime.utcnow().isoformat()}\n\n")
            f.write(report)
        print(f"Report saved → {out_path}")

    return report


if __name__ == "__main__":
    print(run_analyst())
