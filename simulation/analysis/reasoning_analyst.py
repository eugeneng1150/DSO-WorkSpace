"""Reasoning analyst: samples agent CoT traces and extracts behavioral insights."""
from __future__ import annotations
import json
import os
from datetime import datetime
from pathlib import Path

from openai import OpenAI

from ..config import AZURE_ENDPOINT, MODEL, CONDITIONS

DATA_DIR = Path(__file__).parent.parent / "data" / "runs"
OUT_DIR = Path(__file__).parent.parent / "data"

_MECHANISM_LABELS = {
    "B":   "no mechanisms (baseline)",
    "R":   "reputation system",
    "C":   "contracting",
    "M":   "mediation",
    "RC":  "reputation + contracting",
    "RM":  "reputation + mediation",
    "CM":  "contracting + mediation",
    "RCM": "reputation + contracting + mediation",
}

client = OpenAI(
    api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
    base_url=AZURE_ENDPOINT,
)


def _load_traces(condition: str, run_idx: int) -> list[dict]:
    path = DATA_DIR / f"{condition}_run_{run_idx:02d}_traces.jsonl"
    if not path.exists():
        return []
    with open(path) as f:
        return [json.loads(line) for line in f if line.strip()]


def _load_run(condition: str, run_idx: int) -> dict:
    path = DATA_DIR / f"{condition}_run_{run_idx:02d}.json"
    if not path.exists():
        return {}
    with open(path) as f:
        return json.load(f)


def _sample_traces(traces: list[dict], rounds_data: list[dict], n: int = 24) -> list[dict]:
    """Pick traces from early rounds, late rounds, and high-defection rounds."""
    if not rounds_data:
        return traces[:n]

    max_round = max(r["round"] for r in rounds_data)
    defection_rounds = {
        r["round"] for r in sorted(rounds_data, key=lambda x: -x.get("defections", 0))[:3]
        if r.get("defections", 0) > 0
    }
    early = {1, 2, 3}
    late = {max_round - 2, max_round - 1, max_round}
    priority_rounds = early | late | defection_rounds

    # Gather traces from priority rounds first, then fill from remaining
    priority = [t for t in traces if t["round"] in priority_rounds and t.get("reasoning")]
    remaining = [t for t in traces if t["round"] not in priority_rounds and t.get("reasoning")]

    sampled = priority[:n]
    if len(sampled) < n:
        sampled += remaining[: n - len(sampled)]
    return sampled


def _format_traces(traces: list[dict]) -> str:
    lines = []
    for t in traces:
        lines.append(
            f"\n--- Round {t['round']} | {t['phase']} | "
            f"Agent {t['agent_id']} ({t['specialty']} specialist) ---\n"
            + t["reasoning"][:600]
        )
    return "\n".join(lines)


def _build_prompt(condition: str, traces: list[dict], run_data: dict) -> str:
    rounds = run_data.get("rounds", [])
    final_metrics = rounds[-1]["metrics"] if rounds else {}
    total_defections = sum(r.get("defections", 0) for r in rounds)
    mechanism_label = _MECHANISM_LABELS.get(condition, condition)

    def _fmt(v):
        return f"{v:.3f}" if isinstance(v, (int, float)) else "N/A"

    return f"""You are analyzing reasoning traces from a multi-agent marketplace simulation.

Setup: 9 LLM agents trade 3 goods (A, B, C) over 30 rounds. Each agent specializes in \
producing one good and needs the other two. Agents can cooperate (fair trade) or defect \
(take goods without reciprocating).

Condition: {condition} — {mechanism_label}
Final metrics: efficiency={_fmt(final_metrics.get('efficiency'))}, \
equality={_fmt(final_metrics.get('equality'))}, \
sustainability={_fmt(final_metrics.get('sustainability'))}, \
peace={_fmt(final_metrics.get('peace'))}
Total defections across all rounds: {total_defections}

AGENT REASONING TRACES (sampled from early, late, and high-defection rounds):
{_format_traces(traces)}

Analyze these traces and report:

1. **Dominant strategies**: How do agents decide to cooperate or defect? What drives the decision?
2. **Mechanism use**: Do agents explicitly reason about the available mechanisms \
({mechanism_label})? Do they engage with them strategically or ignore them?
3. **Trust and reputation**: How do agents assess partner trustworthiness? \
Do they track history or treat each trade independently?
4. **Defection triggers**: What reasoning patterns appear before defection decisions?
5. **Norm formation**: Any evidence of implicit coordination or shared expectations emerging?
6. **Reasoning depth**: Are agents reasoning coherently about their situation, \
or showing shallow/repetitive thinking?
7. **One-sentence verdict**: What primarily drives cooperation or defection in this condition?

Quote specific agent reasoning to support your claims. Be concise.
"""


def run_reasoning_analyst(
    condition: str | None = None,
    run_idx: int = 0,
    save: bool = True,
) -> str:
    targets = [condition] if condition else CONDITIONS
    sections = []

    for cond in targets:
        print(f"[{cond}] Loading traces (run {run_idx})...")
        traces = _load_traces(cond, run_idx)
        if not traces:
            sections.append(f"## Condition {cond}\n\nNo traces found for run {run_idx}.")
            continue

        run_data = _load_run(cond, run_idx)
        rounds_data = run_data.get("rounds", [])
        sampled = _sample_traces(traces, rounds_data)
        print(f"  {len(sampled)} traces sampled from {len(traces)} total.")

        prompt = _build_prompt(cond, sampled, run_data)
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )
        sections.append(f"## Condition {cond} — {_MECHANISM_LABELS.get(cond, cond)}\n\n"
                        + response.choices[0].message.content)

    report = "# Reasoning Analysis Report\n\n" + "\n\n---\n\n".join(sections)

    if save:
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        out_path = OUT_DIR / f"reasoning_report_{timestamp}.md"
        out_path.parent.mkdir(parents=True, exist_ok=True)
        with open(out_path, "w") as f:
            f.write(report)
        print(f"Report saved → {out_path}")

    return report


if __name__ == "__main__":
    print(run_reasoning_analyst())
