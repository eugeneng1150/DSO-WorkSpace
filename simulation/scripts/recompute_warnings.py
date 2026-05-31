"""Recompute whistleblowing metrics in existing log files using tightened detection.

Old logic: any public message with a negative keyword counted as a warning.
New logic: requires BOTH a negative keyword AND a named agent (e.g. "Agent 6").

Usage:
    python -m simulation.scripts.recompute_warnings [--model gpt-5.4-mini]

Rewrites JSON log files in-place with corrected metrics.
"""
from __future__ import annotations
import json
import re
import sys
from pathlib import Path

BASE_DIR = Path(__file__).parent.parent / "data" / "runs"

NEGATIVE_KEYWORDS = ["defect", "cheat", "short", "failed", "breach", "warn", "didn't deliver", "stole"]


def _is_negative_mention(text: str) -> bool:
    return any(k in text.lower() for k in NEGATIVE_KEYWORDS)


def _extract_mentioned_agent(text: str):
    match = re.search(r'Agent (\d+)', text)
    return int(match.group(1)) if match else None


def recompute_file(filepath: Path) -> dict:
    with open(filepath) as f:
        data = json.load(f)

    troll_ids = set(data.get("session_log", {}).get("troll_ids", []))

    # Replay all public messages round by round
    warnings_cumulative: dict[int, int] = {}
    negative_mentions_all: list[dict] = []
    defections_cumulative: dict[int, int] = {}

    for rnd in data["rounds"]:
        round_num = rnd["round"]

        # Rebuild defections_suffered from trades
        for trade in rnd.get("trades", []):
            defected_by = trade.get("defected_by")
            if defected_by is not None:
                victim = trade["target"] if defected_by == trade["proposer"] else trade["proposer"]
                defections_cumulative[victim] = defections_cumulative.get(victim, 0) + 1

        # Recompute warnings from public messages with tightened logic
        round_neg_mentions = []
        for msg in rnd.get("public_messages", []):
            sender = msg["sender"]
            text = msg["text"]
            target = _extract_mentioned_agent(text)
            if _is_negative_mention(text) and target is not None:
                warnings_cumulative[sender] = warnings_cumulative.get(sender, 0) + 1
                round_neg_mentions.append({
                    "sender": sender,
                    "target": target,
                    "round": round_num,
                })

        negative_mentions_all.extend(round_neg_mentions)

        # Update round data
        rnd["warnings_broadcast_cumulative"] = {str(k): v for k, v in warnings_cumulative.items()}
        rnd["negative_mentions"] = negative_mentions_all.copy()

        # Recompute intermediate metrics
        total_defections = sum(v for k, v in defections_cumulative.items() if k not in troll_ids)
        total_warnings = sum(v for k, v in warnings_cumulative.items() if k not in troll_ids)
        whistleblowing_rate = total_warnings / max(total_defections, 1)

        # Recompute false accusation rate using system reputation from log
        rep = rnd.get("reputation", {})
        neg_non_troll = [m for m in negative_mentions_all if m.get("sender") not in troll_ids]
        false_accusations = sum(
            1 for m in neg_non_troll
            if float(rep.get(str(m.get("target")), 1.0)) > 0.7
        )
        false_accusation_rate = false_accusations / max(len(neg_non_troll), 1)

        accurate_warnings = sum(
            1 for m in neg_non_troll
            if float(rep.get(str(m.get("target")), 1.0)) < 0.5
        )
        warning_accuracy = accurate_warnings / max(total_warnings, 1)

        rnd["metrics"]["whistleblowing_rate"] = round(whistleblowing_rate, 4)
        rnd["metrics"]["false_accusation_rate"] = round(false_accusation_rate, 4)
        rnd["metrics"]["warning_accuracy"] = round(warning_accuracy, 4)

    # Write back
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)

    final = data["rounds"][-1]["metrics"]
    return {
        "whistleblowing_rate": final["whistleblowing_rate"],
        "false_accusation_rate": final["false_accusation_rate"],
        "warning_accuracy": final["warning_accuracy"],
    }


def main():
    model = "gpt-5.4-mini"
    if "--model" in sys.argv:
        idx = sys.argv.index("--model")
        model = sys.argv[idx + 1]

    data_dir = BASE_DIR / model
    if not data_dir.exists():
        print(f"No data directory: {data_dir}")
        return

    files = sorted(data_dir.glob("*_run_*.json"))
    if not files:
        print(f"No log files in {data_dir}")
        return

    print(f"Recomputing warnings for {len(files)} files in {data_dir}...")
    for f in files:
        if f.name.endswith("_traces.jsonl"):
            continue
        result = recompute_file(f)
        print(f"  {f.name}: whistleblowing={result['whistleblowing_rate']:.4f}, "
              f"false_acc={result['false_accusation_rate']:.4f}, "
              f"warning_acc={result['warning_accuracy']:.4f}")

    print("Done.")


if __name__ == "__main__":
    main()
