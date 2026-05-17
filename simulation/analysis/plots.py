"""Generate charts from JSON run logs."""
from __future__ import annotations
import json
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np

DATA_DIR = Path(__file__).parent.parent / "data" / "runs"
OUT_DIR = Path(__file__).parent.parent / "data" / "plots"

METRICS = ["efficiency", "equality", "sustainability", "peace"]
INTERMEDIATE = ["whistleblowing_rate", "false_accusation_rate", "warning_accuracy"]
CONDITIONS = ["B", "R", "C", "M", "RC", "CM", "RCM"]
COLORS = cm.tab10(np.linspace(0, 1, len(CONDITIONS)))


def _load_runs(condition: str) -> list[dict]:
    files = sorted(DATA_DIR.glob(f"{condition}_run_*.json"))
    runs = []
    for f in files:
        with open(f) as fp:
            runs.append(json.load(fp))
    return runs


def _mean_metric_over_rounds(runs: list[dict], metric: str) -> list[float]:
    """Average metric value per round across all runs."""
    if not runs:
        return []
    n_rounds = len(runs[0]["rounds"])
    values = []
    for r in range(n_rounds):
        round_vals = [run["rounds"][r]["metrics"].get(metric, 0) for run in runs if r < len(run["rounds"])]
        values.append(np.mean(round_vals) if round_vals else 0.0)
    return values


def plot_metric_trajectories(save: bool = True) -> None:
    """One subplot per metric: all conditions over rounds."""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes = axes.flatten()

    for ax, metric in zip(axes, METRICS):
        for color, condition in zip(COLORS, CONDITIONS):
            runs = _load_runs(condition)
            if not runs:
                continue
            trajectory = _mean_metric_over_rounds(runs, metric)
            rounds = list(range(1, len(trajectory) + 1))
            ax.plot(rounds, trajectory, label=condition, color=color, linewidth=1.8)

        ax.axhline(0.5, color="black", linestyle="--", linewidth=0.8, alpha=0.5, label="stability threshold")
        ax.set_title(metric.capitalize())
        ax.set_xlabel("Round")
        ax.set_ylabel(metric)
        ax.set_ylim(0, 1.05)
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)

    fig.suptitle("Social Metrics Over Rounds by Condition", fontsize=14, fontweight="bold")
    plt.tight_layout()
    _maybe_save(fig, "metric_trajectories.png", save)


def plot_final_metrics_heatmap(save: bool = True) -> None:
    """Heatmap: conditions × metrics, value = mean final metric."""
    data = np.zeros((len(CONDITIONS), len(METRICS)))
    for i, condition in enumerate(CONDITIONS):
        runs = _load_runs(condition)
        for j, metric in enumerate(METRICS):
            vals = [r["final_metrics"].get(metric, 0) for r in runs]
            data[i, j] = np.mean(vals) if vals else 0.0

    fig, ax = plt.subplots(figsize=(8, 5))
    im = ax.imshow(data, cmap="RdYlGn", vmin=0, vmax=1, aspect="auto")
    ax.set_xticks(range(len(METRICS)))
    ax.set_xticklabels([m.capitalize() for m in METRICS])
    ax.set_yticks(range(len(CONDITIONS)))
    ax.set_yticklabels(CONDITIONS)
    plt.colorbar(im, ax=ax, label="Mean value (final round)")
    for i in range(len(CONDITIONS)):
        for j in range(len(METRICS)):
            ax.text(j, i, f"{data[i, j]:.2f}", ha="center", va="center", fontsize=9)
    ax.set_title("Final Round Metrics by Condition", fontweight="bold")
    plt.tight_layout()
    _maybe_save(fig, "final_metrics_heatmap.png", save)


def plot_defection_rates(save: bool = True) -> None:
    """Bar chart: mean defection rate per condition."""
    means, stds, labels = [], [], []
    for condition in CONDITIONS:
        runs = _load_runs(condition)
        if not runs:
            continue
        peace_vals = [r["final_metrics"].get("peace", 0) for r in runs]
        defection_vals = [1 - p for p in peace_vals]
        means.append(np.mean(defection_vals))
        stds.append(np.std(defection_vals))
        labels.append(condition)

    fig, ax = plt.subplots(figsize=(9, 5))
    x = np.arange(len(labels))
    ax.bar(x, means, yerr=stds, capsize=5, color=COLORS[:len(labels)], alpha=0.85)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("Defection rate (1 - Peace)")
    ax.set_ylim(0, 1)
    ax.set_title("Mean Defection Rate by Condition (Final Round)", fontweight="bold")
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    _maybe_save(fig, "defection_rates.png", save)


def plot_intermediate_variables(save: bool = True) -> None:
    """Bar chart: whistleblowing, false accusation, warning accuracy per condition."""
    fig, axes = plt.subplots(1, 3, figsize=(14, 5))
    for ax, var in zip(axes, INTERMEDIATE):
        means, labels = [], []
        for condition in CONDITIONS:
            runs = _load_runs(condition)
            if not runs:
                continue
            # Average across all rounds and runs
            vals = []
            for run in runs:
                for rnd in run["rounds"]:
                    v = rnd["metrics"].get(var)
                    if v is not None:
                        vals.append(v)
            means.append(np.mean(vals) if vals else 0.0)
            labels.append(condition)

        x = np.arange(len(labels))
        ax.bar(x, means, color=COLORS[:len(labels)], alpha=0.85)
        ax.set_xticks(x)
        ax.set_xticklabels(labels)
        ax.set_title(var.replace("_", " ").title())
        ax.set_ylim(0, 1)
        ax.grid(axis="y", alpha=0.3)

    fig.suptitle("Intermediate Variables by Condition", fontsize=13, fontweight="bold")
    plt.tight_layout()
    _maybe_save(fig, "intermediate_variables.png", save)


def plot_all(save: bool = True) -> None:
    plot_metric_trajectories(save)
    plot_final_metrics_heatmap(save)
    plot_defection_rates(save)
    plot_intermediate_variables(save)
    print(f"Plots saved to {OUT_DIR}")


def _maybe_save(fig: plt.Figure, filename: str, save: bool) -> None:
    if save:
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        fig.savefig(OUT_DIR / filename, dpi=150, bbox_inches="tight")
        plt.close(fig)
    else:
        plt.show()
