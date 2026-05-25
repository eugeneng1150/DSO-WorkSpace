"""Recompute Peace as cumulative metric from existing run logs."""
import json
from pathlib import Path

from .config import DATA_DIR, CONDITIONS


def recompute_run(filepath: Path) -> bool:
    with open(filepath) as f:
        data = json.load(f)

    cumulative_attempted = 0
    cumulative_defected = 0

    for rnd in data["rounds"]:
        cumulative_attempted += rnd["trade_count"]
        cumulative_defected += rnd["defections"]
        old_peace = rnd["metrics"]["peace"]
        new_peace = round(1.0 - (cumulative_defected / cumulative_attempted), 4) if cumulative_attempted > 0 else 1.0
        rnd["metrics"]["peace"] = new_peace

    if data["rounds"]:
        data["final_metrics"]["peace"] = data["rounds"][-1]["metrics"]["peace"]

    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)
    return True


def main():
    for condition in CONDITIONS:
        runs = sorted(DATA_DIR.glob(f"{condition}_run_*.json"))
        for fp in runs:
            recompute_run(fp)
            final = json.loads(fp.read_text())["final_metrics"]["peace"]
            print(f"  {fp.name}: final Peace = {final:.4f}")


if __name__ == "__main__":
    main()
