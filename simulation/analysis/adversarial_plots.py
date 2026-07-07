"""Adversarial red-teaming comparison plots.

Two-line story: dumb trolls (baseline) → v6 (best attack).
Keeps revote outcomes table and mediation utilisation chart.
"""
from __future__ import annotations
import json
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np

from .. import config


def _get_out_dir() -> Path:
    model_tag = config.DATA_DIR.name
    out = Path(__file__).parent.parent / "data" / "plots" / model_tag / "adversarial"
    out.mkdir(parents=True, exist_ok=True)
    return out


def _load_runs(pattern: str) -> list[dict]:
    files = sorted(config.DATA_DIR.glob(pattern))
    runs = []
    for f in files:
        with open(f) as fp:
            runs.append(json.load(fp))
    return runs


def _get_troll_ids(run: dict) -> set[str]:
    raw = run.get("session_log", {}).get("troll_ids", [])
    return {str(x) for x in raw}


def _utility_trajectory(runs: list[dict]) -> list[float]:
    if not runs:
        return []
    n_rounds = max(len(run["rounds"]) for run in runs)
    trajectory = []
    for r in range(n_rounds):
        round_vals = []
        for run in runs:
            if r < len(run["rounds"]):
                troll_ids = _get_troll_ids(run)
                utilities = run["rounds"][r].get("utilities", {})
                non_troll = [float(v) for k, v in utilities.items() if k not in troll_ids]
                if non_troll:
                    round_vals.append(np.mean(non_troll))
        trajectory.append(np.mean(round_vals) if round_vals else 0.0)
    return trajectory


def _cumulative_trajectory(per_round: list[float]) -> list[float]:
    cum = []
    total = 0.0
    for v in per_round:
        total += v
        cum.append(total)
    return cum


def _smooth(data: list[float], window: int = 5) -> np.ndarray:
    """Apply rolling average, preserving edges."""
    if len(data) < window:
        return np.array(data)
    smoothed = np.convolve(data, np.ones(window) / window, mode="same")
    for i in range(min(2, len(data))):
        smoothed[i] = data[i]
    for i in range(1, min(3, len(data))):
        smoothed[-i] = data[-i]
    return smoothed


def _add_injection_markers(ax, y_pos: float | None = None):
    """Add troll injection vertical lines and labels."""
    for inject_round, label in [(51, "+4 trolls"), (101, "+4 trolls"), (151, "+8 trolls")]:
        ax.axvline(inject_round, color="red", linestyle=":", alpha=0.4, linewidth=1)
    if y_pos is None:
        y_pos = ax.get_ylim()[1] * 0.95
    ax.text(52, y_pos, "+4T", fontsize=8, color="red", alpha=0.6)
    ax.text(102, y_pos, "+4T", fontsize=8, color="red", alpha=0.6)
    ax.text(152, y_pos, "+8T", fontsize=8, color="red", alpha=0.6)


CLR_DUMB = "#888888"
CLR_V6 = "#c0392b"


def plot_adversarial_comparison(save: bool = True) -> None:
    """Generate comparison plots: dumb trolls vs v6."""
    out_dir = _get_out_dir()

    dumb_runs = _load_runs("M_tprog_run_*.json")
    v6_runs = _load_runs("M_tprog_adv_v6_run_*.json")

    dumb_pr = _utility_trajectory(dumb_runs)
    v6_pr = _utility_trajectory(v6_runs)

    if not dumb_pr and not v6_pr:
        print("No adversarial run data found.")
        return

    print(f"Loaded: dumb={len(dumb_runs)} runs, v6={len(v6_runs)} runs")

    # ============================================================
    # Plot 1: Per-round utility (smoothed) — 3 lines
    # ============================================================
    fig, ax = plt.subplots(figsize=(14, 6))

    if dumb_pr:
        rounds = list(range(1, len(dumb_pr) + 1))
        ax.plot(rounds, _smooth(dumb_pr), color=CLR_DUMB, linewidth=2.5,
                label="M + dumb trolls (baseline)", linestyle="--", alpha=0.8)

    if v6_pr:
        rounds = list(range(1, len(v6_pr) + 1))
        ax.plot(rounds, _smooth(v6_pr), color=CLR_V6, linewidth=2.5,
                label="M + v6 adversarial (best attack)")

    ax.axhline(0, color="black", linestyle="-", linewidth=0.5, alpha=0.4)
    _add_injection_markers(ax)

    ax.set_xlabel("Round")
    ax.set_ylabel("Avg utility per honest agent")
    ax.set_title("Adversarial Red-Teaming: Baseline → Attack → Defense\n(Mediation mechanism, 5-round rolling average)")
    ax.legend(loc="lower left", fontsize=10)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()

    if save:
        path = out_dir / "adversarial_utility_comparison.png"
        fig.savefig(path, dpi=150)
        print(f"  Saved → {path}")
    plt.close(fig)

    # ============================================================
    # Plot 2: Cumulative utility — 3 lines
    # ============================================================
    fig, ax = plt.subplots(figsize=(14, 6))

    for label, pr, color, ls in [
        ("M + dumb trolls (baseline)", dumb_pr, CLR_DUMB, "--"),
        ("M + v6 adversarial (best attack)", v6_pr, CLR_V6, "-"),
    ]:
        if not pr:
            continue
        cum = _cumulative_trajectory(pr)
        rounds = list(range(1, len(cum) + 1))
        ax.plot(rounds, cum, color=color, linewidth=2.5, label=label, linestyle=ls,
                alpha=0.9 if ls == "-" else 0.8)
        ax.text(len(cum) + 1, cum[-1], f"  {cum[-1]:.0f}",
                fontsize=9, fontweight="bold", color=color, va="center")

    _add_injection_markers(ax)
    ax.set_xlabel("Round")
    ax.set_ylabel("Cumulative avg utility per honest agent")
    ax.set_title("Cumulative Honest-Agent Utility: Baseline → Attack → Defense\n(Mediation mechanism)")
    ax.legend(loc="upper left", fontsize=10)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()

    if save:
        path = out_dir / "adversarial_cumulative_comparison.png"
        fig.savefig(path, dpi=150)
        print(f"  Saved → {path}")
    plt.close(fig)

    # ============================================================
    # Plot 3: Revote outcomes table
    # ============================================================
    fig, ax = plt.subplots(figsize=(14, 4))
    ax.axis("off")

    table_data = []
    headers = ["Condition", "Round", "Winner Designer", "action_both", "action_one", "Trolls/Total"]

    for tag, runs in [("M+v6", v6_runs)]:
        for run in runs:
            revotes = run.get("session_log", {}).get("revotes", [])
            for rv in revotes:
                table_data.append([
                    tag,
                    str(rv["round"]),
                    str(rv["designer_id"]),
                    rv["action_both"],
                    rv["action_one"],
                    f"{rv['n_trolls']}/{rv['n_agents']}",
                ])

    if table_data:
        table = ax.table(cellText=table_data, colLabels=headers, loc="center",
                         cellLoc="center")
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 1.4)
        for i, row in enumerate(table_data):
            if row[4] != "cancel":
                for j in range(len(headers)):
                    table[i + 1, j].set_facecolor("#ffcccc")
        ax.set_title("Mediation Re-Vote Outcomes (red = exploitable design won)", fontweight="bold", pad=20)
    else:
        ax.text(0.5, 0.5, "No re-vote data found", ha="center", va="center", fontsize=14)

    plt.tight_layout()
    if save:
        path = out_dir / "adversarial_revote_outcomes.png"
        fig.savefig(path, dpi=150, bbox_inches="tight")
        print(f"  Saved → {path}")
    plt.close(fig)

    # ============================================================
    # Plot 4: Mediation utilisation — 3 lines
    # ============================================================
    fig, ax = plt.subplots(figsize=(14, 6))

    def _mediation_fraction(runs):
        if not runs:
            return []
        n_rounds = max(len(run["rounds"]) for run in runs)
        fractions = []
        for r in range(n_rounds):
            mediated_vals = []
            total_vals = []
            for run in runs:
                if r >= len(run["rounds"]):
                    continue
                rnd = run["rounds"][r]
                mediated = rnd.get("mediated_trade_count", 0)
                total = rnd.get("trade_count", 0)
                mediated_vals.append(mediated)
                total_vals.append(total)
            total = np.mean(total_vals) if total_vals else 0
            med = np.mean(mediated_vals) if mediated_vals else 0
            fractions.append(med / total if total > 0 else 0.0)
        return fractions

    for label, runs, color, ls in [
        ("M + dumb trolls", dumb_runs, CLR_DUMB, "--"),
        ("M + v6 adversarial", v6_runs, CLR_V6, "-"),
    ]:
        fracs = _mediation_fraction(runs)
        if not fracs:
            continue
        rounds = list(range(1, len(fracs) + 1))
        ax.plot(rounds, _smooth(fracs), color=color, linewidth=2.5,
                label=label, linestyle=ls, alpha=0.9 if ls == "-" else 0.8)

    _add_injection_markers(ax, y_pos=1.0)
    ax.set_xlabel("Round")
    ax.set_ylabel("Fraction of trades mediated")
    ax.set_ylim(0, 1.05)
    ax.set_title("Mediation Utilisation: Baseline → Attack → Defense\n(5-round rolling average)")
    ax.legend(loc="lower left", fontsize=10)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()

    if save:
        path = out_dir / "adversarial_mediation_utilisation.png"
        fig.savefig(path, dpi=150)
        print(f"  Saved → {path}")
    plt.close(fig)

    print(f"\nAdversarial plots saved to: {out_dir}")
