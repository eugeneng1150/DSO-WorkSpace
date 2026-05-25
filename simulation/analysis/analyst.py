"""LLM analyst agent: reads JSON logs, computes summary stats, reports findings."""
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
METRICS = ["sustainability", "peace"]
INTERMEDIATE = ["whistleblowing_rate", "false_accusation_rate", "warning_accuracy"]

client = anthropic.Anthropic(
    api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
    base_url=ANALYST_ENDPOINT,
)

def _load_all_runs() -> dict[str, list[dict]]:
    data = {}
    for condition in CONDITIONS:
        files = sorted(config.DATA_DIR.glob(f"{condition}_run_*.json"))
        runs = []
        for f in files:
            with open(f) as fp:
                runs.append(json.load(fp))
        if runs:
            data[condition] = runs
    return data


def _summarize(all_runs: dict[str, list[dict]]) -> dict:
    """Compute per-condition summary statistics."""
    summary = {}
    for condition, runs in all_runs.items():
        cond_summary = {}

        for metric in METRICS + INTERMEDIATE:
            # Mean across all rounds and runs
            all_vals = []
            for run in runs:
                for rnd in run["rounds"]:
                    v = rnd["metrics"].get(metric)
                    if v is not None:
                        all_vals.append(v)
            cond_summary[metric] = {
                "mean": round(float(np.mean(all_vals)), 4) if all_vals else None,
                "std": round(float(np.std(all_vals)), 4) if all_vals else None,
                "final_mean": round(
                    float(np.mean([run["rounds"][-1]["metrics"].get(metric, 0) for run in runs])), 4
                ),
            }

        # Marketplace cooperation: final Sustainability and Peace both exceed threshold.
        cooperative_runs = sum(
            1 for run in runs
            if all(
                run["rounds"][-1]["metrics"].get(m, 0) > COOPERATION_THRESHOLD
                for m in METRICS
            )
        )
        cond_summary["cooperative_runs"] = cooperative_runs
        cond_summary["total_runs"] = len(runs)
        cond_summary["marketplace_cooperation_rate"] = round(cooperative_runs / max(len(runs), 1), 3)

        # Total defections across all rounds and runs
        total_defections = sum(
            rnd.get("defections", 0)
            for run in runs
            for rnd in run["rounds"]
        )
        cond_summary["total_defections"] = total_defections

        summary[condition] = cond_summary

    return summary


def _build_round_table(all_runs: dict[str, list[dict]]) -> str:
    """Build a per-round table for each condition showing defections and avg utility."""
    lines = []
    for condition, runs in sorted(all_runs.items()):
        n_runs = len(runs)
        max_rounds = max(len(run["rounds"]) for run in runs)
        lines.append(f"\n### Condition {condition} ({n_runs} runs)")
        lines.append(f"{'Round':>5} | {'Defections':>10} | {'Avg Utility':>11} | {'Peace':>6} | {'Sustainability':>14}")
        lines.append(f"{'-'*5}-+-{'-'*10}-+-{'-'*11}-+-{'-'*6}-+-{'-'*14}")
        for r in range(max_rounds):
            defections = []
            utilities = []
            peace_vals = []
            sust_vals = []
            for run in runs:
                if r < len(run["rounds"]):
                    rnd = run["rounds"][r]
                    defections.append(rnd.get("defections", 0))
                    if "utilities" in rnd:
                        utilities.extend(float(v) for v in rnd["utilities"].values())
                    peace_vals.append(rnd["metrics"].get("peace", 0))
                    sust_vals.append(rnd["metrics"].get("sustainability", 0))
            avg_def = sum(defections) / len(defections) if defections else 0
            avg_util = sum(utilities) / len(utilities) if utilities else 0
            avg_peace = sum(peace_vals) / len(peace_vals) if peace_vals else 0
            avg_sust = sum(sust_vals) / len(sust_vals) if sust_vals else 0
            lines.append(
                f"{r+1:>5} | {avg_def:>10.1f} | {avg_util:>11.2f} | {avg_peace:>6.3f} | {avg_sust:>14.3f}"
            )
    return "\n".join(lines)


def _build_analyst_prompt(summary: dict, round_table: str) -> str:
    summary_text = json.dumps(summary, indent=2)
    conditions_list = ", ".join(summary.keys())
    n_conditions = len(summary)
    return f"""You are a research analyst reviewing the results of a multi-agent marketplace simulation.

The simulation tests {n_conditions} conditions: {conditions_list}.
Mechanisms: R=reputation, C=contracting, M=mediation, G=governance, N=network rewiring,
NR=network rewiring + reputation, S=costly sanctions (agent-initiated punishment).
Single-letter conditions isolate one mechanism; multi-letter conditions combine them; B=baseline (none).
N is a standalone condition inspired by RepuNet — agents can sever and request trade links each round.
NR combines network rewiring with reputation scores. S lets agents spend utility to punish others (1:3 ratio).

Each condition runs multiple independent sessions of 30 rounds with 18 LLM agents trading 3 goods.

Research question: Which formal mechanism (or combination) allows self-interested agents
to maintain marketplace cooperation in a repeated trading environment?

Marketplace cooperation is achieved when final-round Sustainability and Peace both exceed 0.5.

Primary metrics:
- Sustainability: whether production is maintained vs round 1 baseline
- Peace: fraction of trades completing without defection

Intermediate variables (to decompose mechanism effects):
- Whistleblowing rate: warnings broadcast / defections suffered
- False accusation rate: unverified negative public mentions / total negative mentions
- Warning accuracy: accurate warnings / total warnings broadcast

Simulation summary statistics:
{summary_text}

Per-round breakdown (averaged across runs for each condition):
{round_table}

Write a structured findings report covering:

1. **Which conditions achieved marketplace cooperation?** (marketplace_cooperation_rate and final metric values)
2. **Which single mechanism was most effective?** Compare each isolated mechanism vs baseline B.
3. **Do mechanism combinations outperform single mechanisms?** (Only if combination data is present.)
4. **What is the minimum sufficient mechanism set?**
5. **How does N (network rewiring) compare?** Did structural partner selection outperform or underperform
   institutional mechanisms (R, C, M, G)?
6. **How does NR (network rewiring + reputation) compare to N alone?** Does adding reputation improve outcomes?
7. **How does S (sanctions) compare?** Did agents actually spend utility to punish, and did it deter defection?
8. **Round-by-round trends**: Using the per-round table, identify which conditions show cooperation
   improving over time vs deteriorating. Note any turning points or phase transitions.
9. **Intermediate variable analysis**: Did mechanisms work through direct defection reduction (Peace up)
   or through improved information propagation (whistleblowing rate changed)?
10. **Unexpected patterns or anomalies** in the data.
11. **Implications for the research question**.

Be specific — cite numbers from the summary and round tables. Flag where data is insufficient to draw conclusions.
"""


def run_analyst(model: str = ANALYST_MODEL, save: bool = True) -> str:
    print("Loading run logs...")
    all_runs = _load_all_runs()
    if not all_runs:
        return "No run logs found. Run the simulation first."

    print(f"Loaded runs for conditions: {list(all_runs.keys())}")
    summary = _summarize(all_runs)

    round_table = _build_round_table(all_runs)
    print("\n=== Per-Round Breakdown ===")
    print(round_table)
    print()

    print("Calling analyst LLM...")
    prompt = _build_analyst_prompt(summary, round_table)
    response = client.messages.create(
        model=model,
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )
    report = response.content[0].text

    if save:
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        out_path = OUT_DIR / f"analyst_report_{timestamp}.md"
        with open(out_path, "w") as f:
            f.write(f"# Analyst Report\n\nGenerated: {datetime.utcnow().isoformat()}\n\n")
            f.write(report)
        print(f"Report saved → {out_path}")

    return report


if __name__ == "__main__":
    print(run_analyst())
