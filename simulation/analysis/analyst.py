"""Unified analyst: cross-condition, cross-troll-count comparison with behavioral traces.

Auto-detects all troll counts (0, 2, 4, 6...) in the data directory and produces
one holistic report comparing how mechanisms degrade under escalating adversarial pressure.
"""
from __future__ import annotations
import json
import os
import re
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

def _detect_troll_counts() -> list[int]:
    """Scan DATA_DIR and return sorted list of troll counts found (e.g. [0, 2, 4])."""
    counts = set()
    for f in config.DATA_DIR.glob("*_run_*.json"):
        if "traces" in f.name:
            continue
        m = re.search(r"_t(\d+)_run_", f.name)
        if m:
            counts.add(int(m.group(1)))
        else:
            counts.add(0)
    return sorted(counts)


def _load_runs_for_troll_count(condition: str, n_trolls: int) -> list[dict]:
    if n_trolls == 0:
        files = sorted(config.DATA_DIR.glob(f"{condition}_run_*.json"))
    else:
        files = sorted(config.DATA_DIR.glob(f"{condition}_t{n_trolls}_run_*.json"))
    files = [f for f in files if "traces" not in f.name]
    runs = []
    for f in files:
        with open(f) as fp:
            runs.append(json.load(fp))
    return runs


def _load_traces_for_troll_count(condition: str, n_trolls: int) -> list[dict]:
    if n_trolls == 0:
        files = sorted(config.DATA_DIR.glob(f"{condition}_run_*_traces.jsonl"))
    else:
        files = sorted(config.DATA_DIR.glob(f"{condition}_t{n_trolls}_run_*_traces.jsonl"))
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

def _summarize_condition(condition: str, runs: list[dict]) -> dict:
    cond = {}
    troll_ids = _get_troll_ids(runs[0])
    n_trolls = len(troll_ids)

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

    if troll_ids:
        n_rounds = len(runs[0]["rounds"])
        half = n_rounds // 2
        damaging_trades = 0
        damaging_last_half = 0
        for run in runs:
            for r, rnd in enumerate(run["rounds"]):
                trades = rnd.get("trades", [])
                t_ids = _get_troll_ids(run)
                for t in trades:
                    if str(t["proposer"]) not in t_ids and str(t["target"]) in t_ids:
                        damaging_trades += 1
                        if r >= half:
                            damaging_last_half += 1
        last_half_rounds = (n_rounds - half) * len(runs)
        cond["damaging_troll_trades"] = damaging_trades
        cond["avg_damaging_last_half"] = round(damaging_last_half / max(last_half_rounds, 1), 2)

    util_vals = []
    for run in runs:
        tids = _get_troll_ids(run)
        for rnd in run["rounds"]:
            utils = rnd.get("utilities", {})
            non_troll = [float(v) for k, v in utils.items() if k not in tids]
            if non_troll:
                util_vals.append(np.mean(non_troll))
    cond["mean_utility"] = round(float(np.mean(util_vals)), 2) if util_vals else 0.0

    return cond


def _build_round_table(condition: str, runs: list[dict]) -> str:
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

def _sample_interesting_traces(condition: str, runs: list[dict], n_trolls: int, max_per_condition: int = 6) -> list[str]:
    traces = _load_traces_for_troll_count(condition, n_trolls)
    if not traces:
        return []

    troll_ids = _get_troll_ids(runs[0]) if runs else set()
    n_rounds = len(runs[0]["rounds"]) if runs else 30

    rounds_data = runs[0]["rounds"] if runs else []
    defection_rounds = sorted(
        [(r["round"], r.get("defections", 0)) for r in rounds_data if r.get("defections", 0) > 2],
        key=lambda x: -x[1]
    )
    priority_rounds = {1, 2, n_rounds, n_rounds - 1}
    if defection_rounds:
        priority_rounds.add(defection_rounds[0][0])
    priority_rounds.add(n_rounds // 2)

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

def _build_analyst_prompt(
    troll_counts: list[int],
    summaries: dict[int, dict[str, dict]],
    round_tables: dict[int, dict[str, str]],
    traces: dict[int, dict[str, list[str]]],
) -> str:
    # Build summary block organized by troll count
    summary_block = ""
    for n_trolls in troll_counts:
        if n_trolls not in summaries:
            continue
        label = f"{n_trolls} trolls ({18 + n_trolls} total agents)" if n_trolls > 0 else "0 trolls (18 agents, no adversaries)"
        summary_block += f"\n### {label}\n{json.dumps(summaries[n_trolls], indent=2)}\n"

    # Build round tables block
    tables_block = ""
    for n_trolls in troll_counts:
        if n_trolls not in round_tables:
            continue
        label = f"{n_trolls} trolls" if n_trolls > 0 else "0 trolls"
        for cond in CONDITIONS:
            if cond in round_tables[n_trolls]:
                mech_label = _MECHANISM_LABELS.get(cond, cond)
                tables_block += f"\n### {cond} — {mech_label} ({label})\n{round_tables[n_trolls][cond]}\n"

    # Build traces block
    traces_block = ""
    for n_trolls in troll_counts:
        if n_trolls not in traces:
            continue
        label = f"{n_trolls} trolls" if n_trolls > 0 else "0 trolls"
        for cond in CONDITIONS:
            if cond in traces[n_trolls] and traces[n_trolls][cond]:
                traces_block += f"\n### {cond} ({label}) — Sample Agent Reasoning\n"
                traces_block += "\n\n".join(traces[n_trolls][cond])
                traces_block += "\n"

    troll_counts_str = ", ".join(str(t) for t in troll_counts)

    return f"""You are a research analyst reviewing a multi-agent marketplace simulation comparing 7 institutional mechanisms for sustaining cooperation among self-interested LLM agents under escalating adversarial pressure.

SETUP:
- 18 LLM agents (GPT-5.4-nano) + trolls added on top (IDs 18+)
- Troll counts tested: {troll_counts_str}
- 3 perishable goods (A, B, C), barter economy, 30 rounds
- Production cost: 1 utility/unit, consumption gain: +3 utility/needed unit, 20% spoilage/round
- Agents see only "Round N" — no total rounds, no market health metrics
- Trolls defect on ALL trades, propose trades to all neighbors, broadcast lies
- All metrics exclude trolls
- "Damaging troll trades" = trades where a non-troll proposed to a troll and the troll stole goods

CONDITIONS:
{json.dumps(_MECHANISM_LABELS, indent=2)}

INFORMATION GRADIENT (B → NR → GR):
- B: private experience only (lifetime partner summary + last 5 rounds detail)
- NR: private experience + 10-round gossip history + network reshaping (sever/request links)
- GR: private experience + system-computed reputation scores visible to all

SUMMARY STATISTICS (by troll count):
{summary_block}

PER-ROUND TABLES:
{tables_block}

AGENT REASONING TRACES (sampled for interesting behavior):
{traces_block}

Write a single comprehensive report with these sections:

1. **EXECUTIVE SUMMARY** (3-4 sentences): Headline findings across all troll counts.

2. **MECHANISM RANKING**: Rank all 7 conditions by overall effectiveness. For each, state cooperation rate, mean utility, troll isolation, and one-line verdict.

3. **ESCALATION ANALYSIS**: How does each mechanism degrade as troll count increases ({troll_counts_str})? Which mechanisms are robust vs fragile? Present as a comparison table or structured comparison showing the trajectory for each mechanism.

4. **TROLL RESILIENCE**: Which mechanisms actually isolated trolls? Compare damaging troll trades across conditions and troll counts. Why did some mechanisms fail despite having information?

5. **INFORMATION GRADIENT (B → NR → GR)**: Does more information lead to better outcomes? How does this change under escalating adversarial pressure?

6. **BEHAVIORAL INSIGHTS** (use the CoT traces): Quote specific agent reasoning showing:
   - How agents decide to cooperate vs defect
   - How agents react to troll encounters
   - Whether agents use available mechanisms strategically
   - How behavior changes between 2-troll and 4-troll scenarios
   Use exact quotes, citing round, agent ID, and troll count.

7. **MECHANISM-SPECIFIC FINDINGS**: For each condition, what worked and what didn't?

8. **BREAKING POINTS**: At what troll count does each mechanism fail? Which mechanisms have the highest breaking point?

9. **IMPLICATIONS**: What does this mean for the research question? What should be tested next?

Be specific — cite numbers and quote traces. Flag where 1 run is insufficient for statistical claims.
"""


def run_analyst(model: str = ANALYST_MODEL, save: bool = True) -> str:
    print("Loading run logs...")

    troll_counts = _detect_troll_counts()
    if not troll_counts:
        return "No run logs found. Run the simulation first."
    print(f"Troll counts detected: {troll_counts}")

    summaries: dict[int, dict[str, dict]] = {}
    round_tables: dict[int, dict[str, str]] = {}
    traces: dict[int, dict[str, list[str]]] = {}

    for n_trolls in troll_counts:
        summaries[n_trolls] = {}
        round_tables[n_trolls] = {}
        traces[n_trolls] = {}

        for condition in CONDITIONS:
            runs = _load_runs_for_troll_count(condition, n_trolls)
            if not runs:
                continue

            summaries[n_trolls][condition] = _summarize_condition(condition, runs)
            round_tables[n_trolls][condition] = _build_round_table(condition, runs)
            sampled = _sample_interesting_traces(condition, runs, n_trolls)
            if sampled:
                traces[n_trolls][condition] = sampled
                print(f"  [{condition}, {n_trolls} trolls] {len(sampled)} traces sampled")

    print("Calling analyst LLM...")
    prompt = _build_analyst_prompt(troll_counts, summaries, round_tables, traces)

    response = client.messages.create(
        model=model,
        max_tokens=8192,
        messages=[{"role": "user", "content": prompt}],
    )
    report = response.content[0].text

    if save:
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        model_tag = config.DATA_DIR.name
        trolls_label = "_".join(f"t{t}" for t in troll_counts)
        out_path = OUT_DIR / f"analyst_report_{model_tag}_{trolls_label}_{timestamp}.md"
        with open(out_path, "w") as f:
            f.write(f"# Analyst Report — {model_tag}\n\n")
            f.write(f"Generated: {datetime.utcnow().isoformat()}\n")
            f.write(f"Troll counts: {troll_counts}\n\n")
            f.write(report)
        print(f"Report saved → {out_path}")

    return report


if __name__ == "__main__":
    print(run_analyst())
