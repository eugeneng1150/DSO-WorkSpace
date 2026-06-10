"""Unified cross-model analyst: compares mechanisms across models and troll counts.

Auto-discovers all model directories under data/runs/ and produces one holistic
report comparing how mechanisms perform across different LLM backends and
escalating adversarial pressure.
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
from ..config import ANALYST_ENDPOINT, ANALYST_MODEL, CONDITIONS

_BASE_DATA_DIR = Path(__file__).parent.parent / "data" / "runs"
OUT_DIR = Path(__file__).parent.parent / "data"
METRICS = ["gini", "mean_utility"]
INTERMEDIATE = ["whistleblowing_rate", "false_accusation_rate", "warning_accuracy"]

PROGRESSIVE_SENTINEL = -1
TROLL_PHASES = [(1, 50, 0), (51, 100, 4), (101, 150, 8), (151, 200, 16)]

_MECHANISM_LABELS = {
    "B":  "baseline (no mechanisms)",
    "GR": "global reputation (system-computed scores visible to all)",
    "C":  "contracting (binding contracts, 6 utility breach penalty)",
    "M":  "mediation (agent-designed mediator, free delegation)",
    "G":  "governance (oracle detects defection >40% and predatory targeting, escalates to fines/suspension)",
    "NR": "network rewiring + local reputation (sever/request links, 10-round gossip history, no system scores)",
    "S":  "costly sanctions (spend 1 utility → target loses 3, anonymous, publicly announced)",
    "J":  "judicial (complaint-driven enforcement — victims file complaints, court verifies and fines defectors 5 utility)",
    "E":  "escrow (shared insurance pool — starts at 100, pays victims 4 per defection, pool collapse resets ALL agents' utility to 0)",
}

client = anthropic.Anthropic(
    api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
    base_url=ANALYST_ENDPOINT,
)


# ── Model discovery ─────────────────────────────────────────────────────────

def _discover_models() -> list[str]:
    """Return sorted list of model tags that have run data."""
    if not _BASE_DATA_DIR.exists():
        return []
    return sorted(
        d.name for d in _BASE_DATA_DIR.iterdir()
        if d.is_dir() and any(d.glob("*_run_*.json"))
    )


def _detect_troll_counts_for_model(model_dir: Path) -> list[int]:
    """Scan a model's data dir and return sorted troll counts found.

    Returns PROGRESSIVE_SENTINEL (-1) for progressive troll runs (_tprog files).
    """
    counts = set()
    for f in model_dir.glob("*_run_*.json"):
        if "traces" in f.name:
            continue
        if "_tprog_" in f.name:
            counts.add(PROGRESSIVE_SENTINEL)
        elif re.search(r"_t(\d+)_run_", f.name):
            counts.add(int(re.search(r"_t(\d+)_run_", f.name).group(1)))
        else:
            counts.add(0)
    return sorted(counts)


def _conditions_for(model_dir: Path, n_trolls: int) -> list[str]:
    """Return which conditions have data for a given model and troll count."""
    available = []
    for cond in CONDITIONS:
        if n_trolls == PROGRESSIVE_SENTINEL:
            files = list(model_dir.glob(f"{cond}_tprog_run_*.json"))
        elif n_trolls > 0:
            files = list(model_dir.glob(f"{cond}_t{n_trolls}_run_*.json"))
        else:
            files = [f for f in model_dir.glob(f"{cond}_run_*.json") if "traces" not in f.name and "_t" not in f.name]
        files = [f for f in files if "traces" not in f.name]
        if files:
            available.append(cond)
    return available


# ── Data loading ─────────────────────────────────────────────────────────────

def _load_runs(model_dir: Path, condition: str, n_trolls: int) -> list[dict]:
    if n_trolls == PROGRESSIVE_SENTINEL:
        files = sorted(model_dir.glob(f"{condition}_tprog_run_*.json"))
    elif n_trolls > 0:
        files = sorted(model_dir.glob(f"{condition}_t{n_trolls}_run_*.json"))
    else:
        files = sorted(f for f in model_dir.glob(f"{condition}_run_*.json") if "_t" not in f.name)
    files = [f for f in files if "traces" not in f.name]
    runs = []
    for f in files:
        with open(f) as fp:
            runs.append(json.load(fp))
    return runs


def _load_traces(model_dir: Path, condition: str, n_trolls: int) -> list[dict]:
    if n_trolls == PROGRESSIVE_SENTINEL:
        files = sorted(model_dir.glob(f"{condition}_tprog_run_*_traces.jsonl"))
    elif n_trolls > 0:
        files = sorted(model_dir.glob(f"{condition}_t{n_trolls}_run_*_traces.jsonl"))
    else:
        files = sorted(f for f in model_dir.glob(f"{condition}_run_*_traces.jsonl") if "_t" not in f.name)
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

def _summarize_condition(condition: str, runs: list[dict], progressive: bool = False) -> dict:
    cond = {}
    troll_ids = _get_troll_ids(runs[0])

    if progressive:
        return _summarize_condition_progressive(condition, runs)

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


def _summarize_condition_progressive(condition: str, runs: list[dict]) -> dict:
    """Summarize a progressive troll run by splitting into 4 phases."""
    cond = {"progressive": True, "phases": {}}

    for start, end, n_trolls in TROLL_PHASES:
        phase_key = f"phase_{start}_{end}_t{n_trolls}"
        phase = {}

        for metric in METRICS:
            vals = []
            for run in runs:
                tids = _get_troll_ids(run)
                for rnd in run["rounds"]:
                    rnd_num = rnd.get("round", rnd.get("round_number", 0))
                    if start <= rnd_num <= end:
                        v = rnd["metrics"].get(metric)
                        if v is not None:
                            vals.append(float(v))
            phase[metric] = {
                "mean": round(float(np.mean(vals)), 4) if vals else None,
            }

        util_vals = []
        for run in runs:
            tids = _get_troll_ids(run)
            for rnd in run["rounds"]:
                rnd_num = rnd.get("round", rnd.get("round_number", 0))
                if start <= rnd_num <= end:
                    utils = rnd.get("utilities", {})
                    non_troll = [float(v) for k, v in utils.items() if k not in tids]
                    if non_troll:
                        util_vals.append(np.mean(non_troll))
        phase["non_troll_mean_utility"] = round(float(np.mean(util_vals)), 2) if util_vals else 0.0

        damaging = 0
        for run in runs:
            tids = _get_troll_ids(run)
            for rnd in run["rounds"]:
                rnd_num = rnd.get("round", rnd.get("round_number", 0))
                if start <= rnd_num <= end:
                    for t in rnd.get("trades", []):
                        if str(t["proposer"]) not in tids and str(t["target"]) in tids:
                            damaging += 1
        phase["damaging_troll_trades"] = damaging

        cond["phases"][phase_key] = phase

    overall_utils = []
    for run in runs:
        tids = _get_troll_ids(run)
        for rnd in run["rounds"]:
            utils = rnd.get("utilities", {})
            non_troll = [float(v) for k, v in utils.items() if k not in tids]
            if non_troll:
                overall_utils.append(np.mean(non_troll))
    cond["overall_mean_utility"] = round(float(np.mean(overall_utils)), 2) if overall_utils else 0.0

    return cond


def _build_round_table(runs: list[dict]) -> str:
    n_rounds = len(runs[0]["rounds"])
    troll_ids = _get_troll_ids(runs[0])
    lines = [f"{'Rnd':>3} | {'Gini':>5} | {'Defect':>6} | {'Trades':>6} | {'AvgUtil':>7}"]
    lines.append(f"{'-'*3}-+-{'-'*5}-+-{'-'*6}-+-{'-'*6}-+-{'-'*7}")
    for r in range(n_rounds):
        gini, defects, trades, utils = [], [], [], []
        for run in runs:
            if r >= len(run["rounds"]):
                continue
            rnd = run["rounds"][r]
            gini.append(rnd["metrics"].get("gini", 0))
            defects.append(rnd.get("defections", 0))
            trades.append(rnd.get("trade_count", 0))
            rnd_utils = rnd.get("utilities", {})
            non_troll = [float(v) for k, v in rnd_utils.items() if k not in troll_ids]
            if non_troll:
                utils.append(np.mean(non_troll))
        lines.append(
            f"{r+1:>3} | {np.mean(gini):>5.3f} | "
            f"{np.mean(defects):>6.1f} | {np.mean(trades):>6.1f} | {np.mean(utils):>7.2f}"
        )
    return "\n".join(lines)


# ── Trace sampling ───────────────────────────────────────────────────────────

def _sample_interesting_traces(model_dir: Path, condition: str, runs: list[dict], n_trolls: int, max_per: int = 4) -> list[str]:
    traces = _load_traces(model_dir, condition, n_trolls)
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
            f"{reasoning[:500]}"
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
        if len(selected) >= max_per:
            break

    if len(selected) < max_per:
        for _, entry in regular[:max_per - len(selected)]:
            selected.append(entry)

    return selected


# ── Data availability map ────────────────────────────────────────────────────

def _build_availability_map(models: list[str]) -> dict[str, dict[int, list[str]]]:
    """Returns {model: {troll_count: [conditions]}}."""
    avail = {}
    for model in models:
        model_dir = _BASE_DATA_DIR / model
        avail[model] = {}
        for tc in _detect_troll_counts_for_model(model_dir):
            conds = _conditions_for(model_dir, tc)
            if conds:
                avail[model][tc] = conds
    return avail


def _format_availability(avail: dict[str, dict[int, list[str]]]) -> str:
    lines = []
    for model, tc_map in avail.items():
        for tc, conds in sorted(tc_map.items()):
            if tc == PROGRESSIVE_SENTINEL:
                label = "progressive (0→4→8→16 trolls)"
            elif tc > 0:
                label = f"{tc} trolls"
            else:
                label = "0 trolls"
            lines.append(f"  {model} @ {label}: {', '.join(conds)} ({len(conds)}/{len(CONDITIONS)} conditions)")
    return "\n".join(lines)


# ── Prompt construction ──────────────────────────────────────────────────────

def _build_analyst_prompt(
    models: list[str],
    avail: dict[str, dict[int, list[str]]],
    summaries: dict[str, dict[int, dict[str, dict]]],
    round_tables: dict[str, dict[int, dict[str, str]]],
    traces: dict[str, dict[int, dict[str, list[str]]]],
) -> str:
    # Build availability section
    avail_block = _format_availability(avail)

    # Build summary block organized by model → troll count
    summary_block = ""
    for model in models:
        summary_block += f"\n## Model: {model}\n"
        if model not in summaries:
            summary_block += "(no data)\n"
            continue
        for n_trolls in sorted(summaries[model].keys()):
            if n_trolls == PROGRESSIVE_SENTINEL:
                label = "progressive (0→4→8→16 trolls over 200 rounds)"
            elif n_trolls > 0:
                label = f"{n_trolls} trolls"
            else:
                label = "0 trolls"
            summary_block += f"\n### {label}\n{json.dumps(summaries[model][n_trolls], indent=2)}\n"

    # Build round tables block
    tables_block = ""
    for model in models:
        if model not in round_tables:
            continue
        for n_trolls in sorted(round_tables[model].keys()):
            if n_trolls == PROGRESSIVE_SENTINEL:
                label = "progressive"
            elif n_trolls > 0:
                label = f"{n_trolls} trolls"
            else:
                label = "0 trolls"
            for cond in CONDITIONS:
                if cond in round_tables[model][n_trolls]:
                    mech_label = _MECHANISM_LABELS.get(cond, cond)
                    tables_block += f"\n### {model} / {cond} — {mech_label} ({label})\n{round_tables[model][n_trolls][cond]}\n"

    # Build traces block
    traces_block = ""
    for model in models:
        if model not in traces:
            continue
        for n_trolls in sorted(traces[model].keys()):
            if n_trolls == PROGRESSIVE_SENTINEL:
                label = "progressive"
            elif n_trolls > 0:
                label = f"{n_trolls} trolls"
            else:
                label = "0 trolls"
            for cond in CONDITIONS:
                if cond in traces[model].get(n_trolls, {}):
                    entries = traces[model][n_trolls][cond]
                    if entries:
                        traces_block += f"\n### {model} / {cond} ({label}) — Sample Agent Reasoning\n"
                        traces_block += "\n\n".join(entries)
                        traces_block += "\n"

    all_troll_counts = sorted(set(tc for tc_map in avail.values() for tc in tc_map))
    has_progressive = PROGRESSIVE_SENTINEL in all_troll_counts
    fixed_counts = [t for t in all_troll_counts if t != PROGRESSIVE_SENTINEL]
    troll_counts_str = ", ".join(str(t) for t in fixed_counts)
    if has_progressive:
        troll_counts_str = "progressive (0→4→8→16)" + (f", fixed: {troll_counts_str}" if fixed_counts else "")

    return f"""You are a research analyst reviewing a multi-agent marketplace simulation comparing 9 institutional mechanisms for sustaining cooperation among self-interested LLM agents under progressive adversarial stress testing.

SETUP:
- 18 LLM agents, single model (DeepSeek-V3)
- Models tested: {', '.join(models)}
- Troll injection: {troll_counts_str}
- Progressive troll injection schedule: 0 trolls (rounds 1-50) → 4 trolls (rounds 51-100) → 8 trolls (rounds 101-150) → 16 trolls (rounds 151-200)
- Trolls are injected silently mid-game — agents discover them through experience
- 3 perishable goods (A, B, C), barter economy, 200 rounds
- Production cost: 1 utility/unit, consumption gain: +3 utility/needed unit (agents only need ONE other good type for utility, not both), 20% spoilage/round
- Agents see only "Round N" — no total rounds, no market health metrics
- Trolls defect on ALL trades, propose trades to all neighbors, broadcast lies
- Key metrics: mean utility (non-troll) and Gini coefficient
- "Damaging troll trades" = trades where a non-troll proposed to a troll and the troll stole goods

CONDITIONS (9 mechanisms):
{json.dumps(_MECHANISM_LABELS, indent=2)}

MECHANISM CATEGORIES:
- Information mechanisms (B → NR → GR): escalating information transparency
  - B: private experience only (lifetime partner summary + last 5 rounds detail)
  - NR: private experience + 10-round gossip history + network reshaping (sever/request links)
  - GR: private experience + system-computed reputation scores visible to all
- Enforcement mechanisms (C, G, S, J): punitive deterrence
  - C: binding contracts with breach penalty (6 utility)
  - G: oracle-based governance (detects defection >40%, escalates fines/suspension)
  - S: costly peer sanctions (spend 1 → target loses 3, anonymous)
  - J: complaint-driven court (filing fee 1, guilty penalty 5, compensation 3, false complaint fine 2)
- Cooperative mechanisms (M, E): structural cooperation support
  - M: agent-designed mediator (free delegation, mediator acts on behalf)
  - E: shared escrow pool (starts at 100, pays 4 per defection victim, pool=0 → ALL agents' utility reset to 0)

DATA AVAILABILITY (not all model×condition cells have data):
{avail_block}

IMPORTANT: Only make claims about data that exists. If a condition is missing, say so explicitly.

SUMMARY STATISTICS (by model — for progressive runs, stats are broken into 4 phases):
{summary_block}

PER-ROUND TABLES (200 rounds):
{tables_block}

AGENT REASONING TRACES (sampled for interesting behavior):
{traces_block}

Write a single comprehensive report with these sections:

1. **EXECUTIVE SUMMARY** (4-5 sentences): Headline findings. What is the single most important takeaway about mechanism robustness under progressive adversarial pressure?

2. **DATA COVERAGE**: What data exists and what is missing. Flag conclusions limited by single-run evidence.

3. **MECHANISM RANKING**: Rank all 9 conditions by robustness. For each, show raw numeric values for non-troll mean_utility and gini across each phase (0T / 4T / 8T / 16T). Present as a comparison table. Use actual numbers, not ✓/✗.

4. **PROGRESSIVE STRESS ANALYSIS**: How does each mechanism degrade as trolls escalate from 0→4→8→16? Which mechanisms maintain utility and low inequality? Which collapse? At what troll count does each mechanism break down? Use raw numeric values throughout.

5. **MECHANISM-SPECIFIC FINDINGS**: For each of the 9 conditions:
   - What worked and what failed under progressive stress?
   - At which phase did it start to degrade?
   - What is the failure mode?

6. **BEHAVIORAL INSIGHTS** (use the CoT traces): Quote specific examples showing:
   - How agents react when trolls first appear (phase 2 transition)
   - Whether agents use mechanisms strategically to counter trolls
   - How behavior changes under maximum pressure (phase 4, 16 trolls)
   Use exact quotes, citing round and agent ID.

7. **IMPLICATIONS & NEXT STEPS**: What should be tested next? Which mechanisms show promise for real-world multi-agent system design?

Be specific — cite numbers and quote traces. Flag every claim that relies on a single run.
"""


def run_analyst(model: str = ANALYST_MODEL, save: bool = True, filter_models: list[str] | None = None, progressive_only: bool = False) -> str:
    """Run analysis. If filter_models is given, only analyse those model directories.
    If progressive_only is True, only analyse progressive troll runs (_tprog)."""
    print("Discovering models and data...")

    models = _discover_models()
    if not models:
        return "No run logs found. Run the simulation first."
    if filter_models:
        models = [m for m in models if m in filter_models]
        if not models:
            return f"No data found for models: {filter_models}. Available: {_discover_models()}"
    print(f"Models found: {models}")

    avail = _build_availability_map(models)
    if progressive_only:
        avail = {m: {tc: conds for tc, conds in tc_map.items() if tc == PROGRESSIVE_SENTINEL}
                 for m, tc_map in avail.items()}
        avail = {m: tc_map for m, tc_map in avail.items() if tc_map}
    print(f"\nData availability:")
    print(_format_availability(avail))

    summaries: dict[str, dict[int, dict[str, dict]]] = {}
    round_tables: dict[str, dict[int, dict[str, str]]] = {}
    traces: dict[str, dict[int, dict[str, list[str]]]] = {}

    for model_name in models:
        model_dir = _BASE_DATA_DIR / model_name
        summaries[model_name] = {}
        round_tables[model_name] = {}
        traces[model_name] = {}

        for n_trolls in sorted(avail.get(model_name, {}).keys()):
            summaries[model_name][n_trolls] = {}
            round_tables[model_name][n_trolls] = {}
            traces[model_name][n_trolls] = {}

            for condition in CONDITIONS:
                runs = _load_runs(model_dir, condition, n_trolls)
                if not runs:
                    continue

                is_prog = n_trolls == PROGRESSIVE_SENTINEL
                summaries[model_name][n_trolls][condition] = _summarize_condition(condition, runs, progressive=is_prog)
                round_tables[model_name][n_trolls][condition] = _build_round_table(runs)
                sampled = _sample_interesting_traces(model_dir, condition, runs, n_trolls)
                if sampled:
                    traces[model_name][n_trolls][condition] = sampled
                    troll_label = "prog" if is_prog else f"{n_trolls}"
                    print(f"  [{model_name}/{condition}, {troll_label}T] {len(sampled)} traces")

    print("\nCalling analyst LLM...")
    prompt = _build_analyst_prompt(models, avail, summaries, round_tables, traces)

    response = client.messages.create(
        model=model,
        max_tokens=8192,
        messages=[{"role": "user", "content": prompt}],
    )
    report = response.content[0].text

    if save:
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        models_tag = "_".join(models)
        all_trolls = sorted(set(tc for m in avail.values() for tc in m))
        troll_parts = []
        for t in all_trolls:
            troll_parts.append("tprog" if t == PROGRESSIVE_SENTINEL else f"t{t}")
        trolls_label = "_".join(troll_parts)
        out_path = OUT_DIR / f"analyst_report_{models_tag}_{trolls_label}_{timestamp}.md"
        with open(out_path, "w") as f:
            f.write(f"# Analyst Report\n\n")
            f.write(f"Generated: {datetime.utcnow().isoformat()}\n")
            f.write(f"Models: {', '.join(models)}\n")
            troll_display = ["progressive" if t == PROGRESSIVE_SENTINEL else str(t) for t in all_trolls]
            f.write(f"Troll mode: {', '.join(troll_display)}\n\n")
            f.write(f"## Data Availability\n\n")
            f.write(_format_availability(avail))
            f.write("\n\n---\n\n")
            f.write(report)
        print(f"Report saved → {out_path}")

    return report


if __name__ == "__main__":
    print(run_analyst())
