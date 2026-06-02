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
from ..config import ANALYST_ENDPOINT, ANALYST_MODEL, COOPERATION_THRESHOLD, CONDITIONS

_BASE_DATA_DIR = Path(__file__).parent.parent / "data" / "runs"
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
    """Scan a model's data dir and return sorted troll counts found."""
    counts = set()
    for f in model_dir.glob("*_run_*.json"):
        if "traces" in f.name:
            continue
        m = re.search(r"_t(\d+)_run_", f.name)
        if m:
            counts.add(int(m.group(1)))
        else:
            counts.add(0)
    return sorted(counts)


def _conditions_for(model_dir: Path, n_trolls: int) -> list[str]:
    """Return which conditions have data for a given model and troll count."""
    available = []
    for cond in CONDITIONS:
        if n_trolls > 0:
            files = list(model_dir.glob(f"{cond}_t{n_trolls}_run_*.json"))
        else:
            files = [f for f in model_dir.glob(f"{cond}_run_*.json") if "traces" not in f.name and "_t" not in f.name]
        files = [f for f in files if "traces" not in f.name]
        if files:
            available.append(cond)
    return available


# ── Data loading ─────────────────────────────────────────────────────────────

def _load_runs(model_dir: Path, condition: str, n_trolls: int) -> list[dict]:
    if n_trolls > 0:
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
    if n_trolls > 0:
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

def _summarize_condition(condition: str, runs: list[dict]) -> dict:
    cond = {}
    troll_ids = _get_troll_ids(runs[0])

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


def _build_round_table(runs: list[dict]) -> str:
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
            label = f"{tc} trolls" if tc > 0 else "0 trolls"
            lines.append(f"  {model} @ {label}: {', '.join(conds)} ({len(conds)}/7 conditions)")
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
            label = f"{n_trolls} trolls" if n_trolls > 0 else "0 trolls"
            summary_block += f"\n### {label}\n{json.dumps(summaries[model][n_trolls], indent=2)}\n"

    # Build round tables block (only for the common troll count with most coverage)
    tables_block = ""
    for model in models:
        if model not in round_tables:
            continue
        for n_trolls in sorted(round_tables[model].keys()):
            label = f"{n_trolls} trolls" if n_trolls > 0 else "0 trolls"
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
            label = f"{n_trolls} trolls" if n_trolls > 0 else "0 trolls"
            for cond in CONDITIONS:
                if cond in traces[model].get(n_trolls, {}):
                    entries = traces[model][n_trolls][cond]
                    if entries:
                        traces_block += f"\n### {model} / {cond} ({label}) — Sample Agent Reasoning\n"
                        traces_block += "\n\n".join(entries)
                        traces_block += "\n"

    all_troll_counts = sorted(set(tc for tc_map in avail.values() for tc in tc_map))
    troll_counts_str = ", ".join(str(t) for t in all_troll_counts)

    return f"""You are a research analyst reviewing a multi-agent marketplace simulation comparing 7 institutional mechanisms for sustaining cooperation among self-interested LLM agents under escalating adversarial pressure.

SETUP:
- 18 LLM agents + trolls added on top (IDs 18+)
- Models tested: {', '.join(models)}
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

DATA AVAILABILITY (not all model×troll×condition cells have data):
{avail_block}

IMPORTANT: Only make claims about data that exists. If a model is missing data for a troll count or condition, say so explicitly. Do not extrapolate results from one model to another.

SUMMARY STATISTICS (by model and troll count):
{summary_block}

PER-ROUND TABLES:
{tables_block}

AGENT REASONING TRACES (sampled for interesting behavior):
{traces_block}

Write a single comprehensive report with these sections:

1. **EXECUTIVE SUMMARY** (4-5 sentences): Headline findings across all models and troll counts. What is the single most important takeaway?

2. **DATA COVERAGE**: Briefly state what data exists and what is missing. Flag any conclusions that are limited by single-run or single-model evidence.

3. **CROSS-MODEL MECHANISM RANKING (4 trolls)**: This is the one troll count with complete data across all models. Rank all 7 conditions. For each, compare performance across models. Highlight which mechanisms are consistent winners vs model-dependent. Present as a comparison table.

4. **MODEL COMPARISON**: How do the models differ in baseline cooperative behavior? Which models need mechanisms more? How does the marginal benefit of each mechanism change across models?

5. **ESCALATION ANALYSIS**: Where troll escalation data exists (primarily nano: t2→t4), how does each mechanism degrade? Which mechanisms are robust vs fragile? Note data gaps.

6. **MECHANISM-SPECIFIC FINDINGS**: For each of the 7 conditions, synthesize findings across all available models:
   - What worked and what didn't?
   - Is the mechanism's effect consistent or model-dependent?
   - What is the failure mode (if any)?

7. **BEHAVIORAL INSIGHTS** (use the CoT traces): Compare how agents from different models reason under the same mechanism. Quote specific examples showing:
   - How agent reasoning style differs across models
   - Whether more capable models use mechanisms more strategically
   - How agents react to trolls differently across models
   Use exact quotes, citing model, round, agent ID.

8. **KEY CROSS-MODEL PATTERNS**: What patterns hold across ALL models? What patterns are model-specific? This section should directly inform which findings are publishable vs preliminary.

9. **IMPLICATIONS & NEXT STEPS**: What should be tested next? Consider: missing data cells, replication needs, mechanism combinations, higher troll counts.

Be specific — cite numbers and quote traces. Flag every claim that relies on a single run. Distinguish between "consistent across models" and "observed in one model only."
"""


def run_analyst(model: str = ANALYST_MODEL, save: bool = True) -> str:
    """Run cross-model analysis across all available data."""
    print("Discovering models and data...")

    models = _discover_models()
    if not models:
        return "No run logs found. Run the simulation first."
    print(f"Models found: {models}")

    avail = _build_availability_map(models)
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

                summaries[model_name][n_trolls][condition] = _summarize_condition(condition, runs)
                round_tables[model_name][n_trolls][condition] = _build_round_table(runs)
                sampled = _sample_interesting_traces(model_dir, condition, runs, n_trolls)
                if sampled:
                    traces[model_name][n_trolls][condition] = sampled
                    print(f"  [{model_name}/{condition}, {n_trolls}T] {len(sampled)} traces")

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
        trolls_label = "_".join(f"t{t}" for t in all_trolls)
        out_path = OUT_DIR / f"analyst_report_cross-model_{trolls_label}_{timestamp}.md"
        with open(out_path, "w") as f:
            f.write(f"# Cross-Model Analyst Report\n\n")
            f.write(f"Generated: {datetime.utcnow().isoformat()}\n")
            f.write(f"Models: {', '.join(models)}\n")
            f.write(f"Troll counts: {all_trolls}\n\n")
            f.write(f"## Data Availability\n\n")
            f.write(_format_availability(avail))
            f.write("\n\n---\n\n")
            f.write(report)
        print(f"Report saved → {out_path}")

    return report


if __name__ == "__main__":
    print(run_analyst())
