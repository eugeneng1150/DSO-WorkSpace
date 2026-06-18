"""Adversarial red-teaming comparison plots.

Overlays dumb trolls (baseline) with each adversarial version (v1, v2, ...)
on the same chart so you can see how each prompt iteration degrades utility.
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


def _discover_versions() -> list[str]:
    """Find all adversarial version tags from data files (e.g. M_tprog_adv_v1_run_00.json -> 'v1')."""
    versions = set()
    for f in config.DATA_DIR.glob("M_tprog_adv_*_run_*.json"):
        name = f.stem
        parts = name.split("_tprog_adv_")[1]
        version = parts.split("_run_")[0]
        versions.add(version)
    # Also check for legacy _tprog_smart files (pre-versioning)
    if list(config.DATA_DIR.glob("M_tprog_smart_run_*.json")):
        versions.add("smart")
    return sorted(versions)


def plot_adversarial_comparison(save: bool = True) -> None:
    """Generate comparison plots: dumb trolls vs each adversarial version."""
    out_dir = _get_out_dir()
    versions = _discover_versions()

    if not versions:
        print("No adversarial run data found. Run with --smart-trolls --adv-version v1 first.")
        return

    print(f"Found adversarial versions: {versions}")

    # --- Colors ---
    base_color = "#888888"
    version_colors = {
        "smart": "#e74c3c",
        "v1": "#e74c3c",
        "v2": "#e67e22",
        "v3": "#9b59b6",
        "v4": "#2ecc71",
        "v5": "#3498db",
    }

    # --- Load baseline (dumb trolls) ---
    dumb_runs = _load_runs("M_tprog_run_*.json")
    dumb_per_round = _utility_trajectory(dumb_runs)
    dumb_cum = _cumulative_trajectory(dumb_per_round)

    # --- Load each adversarial version ---
    adv_data = {}
    for v in versions:
        if v == "smart":
            runs = _load_runs("M_tprog_smart_run_*.json")
        else:
            runs = _load_runs(f"M_tprog_adv_{v}_run_*.json")
        if runs:
            per_round = _utility_trajectory(runs)
            adv_data[v] = {
                "per_round": per_round,
                "cumulative": _cumulative_trajectory(per_round),
                "runs": runs,
            }

    # ============================================================
    # Plot 1: Per-round utility (smoothed) — all versions overlaid
    # ============================================================
    fig, ax = plt.subplots(figsize=(14, 6))

    if dumb_per_round:
        rounds = list(range(1, len(dumb_per_round) + 1))
        smoothed = np.convolve(dumb_per_round, np.ones(5) / 5, mode="same")
        smoothed[0], smoothed[1] = dumb_per_round[0], dumb_per_round[1]
        smoothed[-1], smoothed[-2] = dumb_per_round[-1], dumb_per_round[-2]
        ax.plot(rounds, smoothed, color=base_color, linewidth=2.5, label="Dumb trolls (baseline)",
                linestyle="--", alpha=0.8)

    for v, data in adv_data.items():
        color = version_colors.get(v, "#e74c3c")
        label = f"Adversarial {v}" if v != "smart" else "Adversarial (unversioned)"
        per_round = data["per_round"]
        rounds = list(range(1, len(per_round) + 1))
        smoothed = np.convolve(per_round, np.ones(5) / 5, mode="same")
        smoothed[0], smoothed[1] = per_round[0], per_round[1]
        smoothed[-1], smoothed[-2] = per_round[-1], per_round[-2]
        ax.plot(rounds, smoothed, color=color, linewidth=2.0, label=label)

    ax.axhline(0, color="black", linestyle="-", linewidth=0.5, alpha=0.4)

    # Injection markers
    for inject_round in [51, 101, 151]:
        ax.axvline(inject_round, color="red", linestyle=":", alpha=0.4, linewidth=1)
    ax.text(51, ax.get_ylim()[1] * 0.95, "+4 trolls", fontsize=8, color="red", alpha=0.6)
    ax.text(101, ax.get_ylim()[1] * 0.95, "+4 trolls", fontsize=8, color="red", alpha=0.6)
    ax.text(151, ax.get_ylim()[1] * 0.95, "+8 trolls", fontsize=8, color="red", alpha=0.6)

    ax.set_xlabel("Round")
    ax.set_ylabel("Avg utility per honest agent")
    ax.set_title("Adversarial Red-Teaming: Utility Degradation by Prompt Version\n(Mediation mechanism, 5-round rolling average)")
    ax.legend(loc="lower left")
    ax.grid(True, alpha=0.3)
    plt.tight_layout()

    if save:
        path = out_dir / "adversarial_utility_comparison.png"
        fig.savefig(path, dpi=150)
        print(f"  Saved → {path}")
    plt.close(fig)

    # ============================================================
    # Plot 2: Cumulative utility — all versions overlaid
    # ============================================================
    fig, ax = plt.subplots(figsize=(14, 6))

    if dumb_cum:
        rounds = list(range(1, len(dumb_cum) + 1))
        ax.plot(rounds, dumb_cum, color=base_color, linewidth=2.5, label="Dumb trolls (baseline)",
                linestyle="--", alpha=0.8)
        ax.text(len(dumb_cum), dumb_cum[-1], f"  {dumb_cum[-1]:.0f}",
                fontsize=9, fontweight="bold", color=base_color, va="center")

    for v, data in adv_data.items():
        color = version_colors.get(v, "#e74c3c")
        label = f"Adversarial {v}" if v != "smart" else "Adversarial (unversioned)"
        cum = data["cumulative"]
        rounds = list(range(1, len(cum) + 1))
        ax.plot(rounds, cum, color=color, linewidth=2.0, label=label)
        ax.text(len(cum), cum[-1], f"  {cum[-1]:.0f}",
                fontsize=9, fontweight="bold", color=color, va="center")

    for inject_round in [51, 101, 151]:
        ax.axvline(inject_round, color="red", linestyle=":", alpha=0.4, linewidth=1)

    ax.set_xlabel("Round")
    ax.set_ylabel("Cumulative avg utility per honest agent")
    ax.set_title("Adversarial Red-Teaming: Cumulative Utility by Prompt Version\n(Mediation mechanism)")
    ax.legend(loc="upper left")
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
    headers = ["Version", "Round", "Winner Designer", "action_both", "action_one", "Trolls/Total"]

    for v, data in adv_data.items():
        for run in data["runs"]:
            revotes = run.get("session_log", {}).get("revotes", [])
            for rv in revotes:
                flipped = "execute_fair" if rv["action_one"] != "cancel" else "cancel"
                table_data.append([
                    v,
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
    # Plot 4: Mediator design timeline — who won each revote
    # ============================================================
    fig, ax = plt.subplots(figsize=(14, 5))

    # Baseline: no revotes, just a flat line at "safe"
    if dumb_runs:
        n_rounds_base = len(dumb_runs[0].get("rounds", []))
        elected = dumb_runs[0].get("session_log", {}).get("elected_mediator", {})
        is_safe = 1 if elected.get("action_one", "cancel") == "cancel" else 0
        ax.plot(range(1, n_rounds_base + 1), [is_safe] * n_rounds_base,
                color=base_color, linewidth=2.5, linestyle="--", alpha=0.6,
                label="Dumb trolls (no revotes)")

    for v, data in adv_data.items():
        color = version_colors.get(v, "#e74c3c")
        label = f"Adversarial {v}" if v != "smart" else "Adversarial (unversioned)"

        for run in data["runs"]:
            rounds_data = run.get("rounds", [])
            n_rounds = len(rounds_data)
            design_timeline = []

            # Build per-round mediator status: 1 = safe (cancel), 0 = exploitable (execute_fair)
            for rnd in rounds_data:
                mediator = rnd.get("active_mediator", {})
                if mediator and mediator.get("action_one") == "cancel":
                    design_timeline.append(1)
                elif mediator:
                    design_timeline.append(0)
                else:
                    design_timeline.append(1)  # default safe

            ax.plot(range(1, n_rounds + 1), design_timeline,
                    color=color, linewidth=2.0, label=label, drawstyle="steps-post")

            # Mark revote rounds
            revotes = run.get("session_log", {}).get("revotes", [])
            for rv in revotes:
                r = rv["round"]
                is_safe_rv = 1 if rv["action_one"] == "cancel" else 0
                marker_color = "green" if is_safe_rv else "red"
                ax.scatter(r, is_safe_rv, color=marker_color, s=40, zorder=5,
                           edgecolors="black", linewidths=0.5)

    for inject_round in [51, 101, 151]:
        ax.axvline(inject_round, color="red", linestyle=":", alpha=0.4, linewidth=1)
    ax.text(51, 1.08, "+4 trolls", fontsize=8, color="red", alpha=0.6)
    ax.text(101, 1.08, "+4 trolls", fontsize=8, color="red", alpha=0.6)
    ax.text(151, 1.08, "+8 trolls", fontsize=8, color="red", alpha=0.6)

    ax.set_yticks([0, 1])
    ax.set_yticklabels(["EXPLOITABLE\n(action_one=execute_fair)", "SAFE\n(action_one=cancel)"])
    ax.set_ylim(-0.15, 1.25)
    ax.set_xlabel("Round")
    ax.set_title("Mediator Design Over Time\n(green dot = safe revote, red dot = exploitable revote)")
    ax.legend(loc="lower left")
    ax.grid(True, alpha=0.3, axis="x")
    plt.tight_layout()

    if save:
        path = out_dir / "adversarial_mediator_timeline.png"
        fig.savefig(path, dpi=150)
        print(f"  Saved → {path}")
    plt.close(fig)

    print(f"\nAdversarial plots saved to: {out_dir}")
