"""LLM analyst agent: reads JSON logs, computes summary stats, reports findings."""
from __future__ import annotations
import json
import os
from pathlib import Path
from datetime import datetime

import numpy as np
from openai import OpenAI

from ..config import AZURE_ENDPOINT, MODEL

DATA_DIR = Path(__file__).parent.parent / "data" / "runs"
OUT_DIR = Path(__file__).parent.parent / "data"

CONDITIONS = ["B", "R", "C", "M", "RC", "RM", "CM", "RCM"]
METRICS = ["efficiency", "equality", "sustainability", "peace"]
INTERMEDIATE = ["whistleblowing_rate", "false_accusation_rate", "warning_accuracy"]

client = OpenAI(
    api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
    base_url=AZURE_ENDPOINT,
)


def _load_all_runs() -> dict[str, list[dict]]:
    data = {}
    for condition in CONDITIONS:
        files = sorted(DATA_DIR.glob(f"{condition}_run_*.json"))
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

        # Stability: fraction of runs where all 4 metrics > 0.5 at end
        stable_runs = sum(
            1 for run in runs
            if all(
                run["rounds"][-1]["metrics"].get(m, 0) >= 0.5
                for m in METRICS
            )
        )
        cond_summary["stable_runs"] = stable_runs
        cond_summary["total_runs"] = len(runs)
        cond_summary["stability_rate"] = round(stable_runs / max(len(runs), 1), 3)

        # Total defections across all rounds and runs
        total_defections = sum(
            rnd.get("defections", 0)
            for run in runs
            for rnd in run["rounds"]
        )
        cond_summary["total_defections"] = total_defections

        summary[condition] = cond_summary

    return summary


def _build_analyst_prompt(summary: dict) -> str:
    summary_text = json.dumps(summary, indent=2)
    return f"""You are a research analyst reviewing the results of a multi-agent marketplace simulation.

The simulation tests 8 conditions (B=baseline, R=+Reputation, C=+Contracting, M=+Mediation, RC, RM, CM, RCM).
Each condition runs 10 independent sessions of 30 rounds with 9 LLM agents trading 3 goods.

Research question: Which formal mechanism (or combination) allows a society of self-interested agents
to maintain market stability? Market stability = all four social metrics (Efficiency, Equality,
Sustainability, Peace) above 0.5 by end of simulation.

Social metrics:
- Efficiency: fraction of possible gains from trade realised
- Equality: how evenly utility is distributed (1 = perfectly equal)
- Sustainability: whether production is maintained vs round 1 baseline
- Peace: fraction of trades completing without defection

Intermediate variables (to decompose mechanism effects):
- Whistleblowing rate: warnings broadcast / defections suffered
- False accusation rate: unverified negative public mentions / total negative mentions
- Warning accuracy: accurate warnings / total warnings broadcast

Simulation summary statistics:
{summary_text}

Write a structured findings report covering:

1. **Which conditions achieved market stability?** (stability_rate and final metric values)
2. **Which single mechanism was most effective?** Compare R, C, M individually vs baseline B.
3. **Do mechanism combinations outperform single mechanisms?** Compare RC, RM, CM, RCM vs their components.
4. **What is the minimum sufficient mechanism set?**
5. **Intermediate variable analysis**: Did mechanisms work through direct defection reduction (Peace up)
   or through improved information propagation (whistleblowing rate changed)?
6. **Unexpected patterns or anomalies** in the data.
7. **Implications for the research question**.

Be specific — cite numbers from the summary. Flag where data is insufficient to draw conclusions.
"""


def run_analyst(model: str = MODEL, save: bool = True) -> str:
    print("Loading run logs...")
    all_runs = _load_all_runs()
    if not all_runs:
        return "No run logs found. Run the simulation first."

    print(f"Loaded runs for conditions: {list(all_runs.keys())}")
    summary = _summarize(all_runs)

    print("Calling analyst LLM...")
    prompt = _build_analyst_prompt(summary)
    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=0.3,
    )
    report = response.choices[0].message.content

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
