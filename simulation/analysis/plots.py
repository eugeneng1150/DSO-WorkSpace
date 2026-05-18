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
CONDITIONS = ["B", "R", "C", "M", "RC", "RM", "CM", "RCM"]
COLORS = dict(zip(CONDITIONS, cm.tab10(np.linspace(0, 1, len(CONDITIONS)))))
STABILITY_THRESHOLD = 0.5


def _load_runs(condition: str) -> list[dict]:
    files = sorted(DATA_DIR.glob(f"{condition}_run_*.json"))
    runs = []
    for f in files:
        with open(f) as fp:
            runs.append(json.load(fp))
    return runs


def _mean_metric_over_rounds(runs: list[dict], metric: str) -> list[float]:
    if not runs:
        return []
    n_rounds = len(runs[0]["rounds"])
    values = []
    for r in range(n_rounds):
        round_vals = [run["rounds"][r]["metrics"].get(metric, 0) for run in runs if r < len(run["rounds"])]
        values.append(np.mean(round_vals) if round_vals else 0.0)
    return values


def _mean_round_field(runs: list[dict], field: str) -> list[float]:
    """Average a numeric round-level field (not inside metrics) over rounds."""
    if not runs:
        return []
    n_rounds = len(runs[0]["rounds"])
    values = []
    for r in range(n_rounds):
        vals = [run["rounds"][r].get(field, 0) for run in runs if r < len(run["rounds"])]
        values.append(np.mean(vals) if vals else 0.0)
    return values


# ── Existing plots (updated for 8 conditions) ────────────────────────────────

def plot_metric_trajectories(save: bool = True) -> None:
    """2x2 panel: one subplot per metric, all conditions over rounds."""
    fig, axes = plt.subplots(2, 2, figsize=(14, 10))
    axes = axes.flatten()

    for ax, metric in zip(axes, METRICS):
        for condition in CONDITIONS:
            runs = _load_runs(condition)
            if not runs:
                continue
            trajectory = _mean_metric_over_rounds(runs, metric)
            rounds = list(range(1, len(trajectory) + 1))
            ax.plot(rounds, trajectory, label=condition, color=COLORS[condition], linewidth=1.8)

        ax.axhline(STABILITY_THRESHOLD, color="black", linestyle="--", linewidth=0.8, alpha=0.5, label="stability threshold")
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

    fig, ax = plt.subplots(figsize=(8, 6))
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
    """Bar chart: mean defection rate per condition at final round."""
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

    fig, ax = plt.subplots(figsize=(10, 5))
    x = np.arange(len(labels))
    ax.bar(x, means, yerr=stds, capsize=5, color=[COLORS[c] for c in labels], alpha=0.85)
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
            vals = []
            for run in runs:
                for rnd in run["rounds"]:
                    v = rnd["metrics"].get(var)
                    if v is not None:
                        vals.append(v)
            means.append(np.mean(vals) if vals else 0.0)
            labels.append(condition)

        x = np.arange(len(labels))
        ax.bar(x, means, color=[COLORS[c] for c in labels], alpha=0.85)
        ax.set_xticks(x)
        ax.set_xticklabels(labels)
        ax.set_title(var.replace("_", " ").title())
        ax.set_ylim(0, max(means) * 1.2 if means else 1)
        ax.grid(axis="y", alpha=0.3)

    fig.suptitle("Intermediate Variables by Condition", fontsize=13, fontweight="bold")
    plt.tight_layout()
    _maybe_save(fig, "intermediate_variables.png", save)


# ── New plots ─────────────────────────────────────────────────────────────────

def plot_stability_rates(save: bool = True) -> None:
    """Bar chart: fraction of runs achieving market stability per condition."""
    labels, rates = [], []
    for condition in CONDITIONS:
        runs = _load_runs(condition)
        if not runs:
            continue
        stable = sum(
            1 for run in runs
            if all(
                run["rounds"][-1]["metrics"].get(m, 0) >= STABILITY_THRESHOLD
                for m in METRICS
            )
        )
        labels.append(condition)
        rates.append(stable / len(runs))

    fig, ax = plt.subplots(figsize=(10, 5))
    x = np.arange(len(labels))
    bars = ax.bar(x, rates, color=[COLORS[c] for c in labels], alpha=0.85)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("Stability rate (fraction of runs)")
    ax.set_ylim(0, 1.1)
    ax.axhline(1.0, color="green", linestyle="--", linewidth=0.8, alpha=0.5)
    for bar, rate in zip(bars, rates):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.02,
                f"{rate:.0%}", ha="center", va="bottom", fontsize=9, fontweight="bold")
    ax.set_title("Market Stability Rate by Condition\n(all 4 metrics ≥ 0.5 at round 30)", fontweight="bold")
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    _maybe_save(fig, "stability_rates.png", save)


def plot_defection_trajectory(save: bool = True) -> None:
    """Line chart: defection count per round over time per condition."""
    fig, ax = plt.subplots(figsize=(12, 6))
    for condition in CONDITIONS:
        runs = _load_runs(condition)
        if not runs:
            continue
        trajectory = _mean_round_field(runs, "defections")
        rounds = list(range(1, len(trajectory) + 1))
        ax.plot(rounds, trajectory, label=condition, color=COLORS[condition], linewidth=1.8)

    ax.set_xlabel("Round")
    ax.set_ylabel("Mean defections per round")
    ax.set_title("Defection Count Over Rounds by Condition", fontweight="bold")
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    _maybe_save(fig, "defection_trajectory.png", save)


def plot_trade_volume(save: bool = True) -> None:
    """Line chart: trade count per round over time per condition."""
    fig, ax = plt.subplots(figsize=(12, 6))
    for condition in CONDITIONS:
        runs = _load_runs(condition)
        if not runs:
            continue
        trajectory = _mean_round_field(runs, "trade_count")
        rounds = list(range(1, len(trajectory) + 1))
        ax.plot(rounds, trajectory, label=condition, color=COLORS[condition], linewidth=1.8)

    ax.set_xlabel("Round")
    ax.set_ylabel("Mean trades per round")
    ax.set_title("Trade Volume Over Rounds by Condition", fontweight="bold")
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    _maybe_save(fig, "trade_volume.png", save)


def plot_contract_utilisation(save: bool = True) -> None:
    """For contracting conditions: contracts proposed/executed/breached per round."""
    contracting_conditions = [c for c in CONDITIONS if "C" in c]
    if not contracting_conditions:
        return

    fig, axes = plt.subplots(1, len(contracting_conditions),
                              figsize=(5 * len(contracting_conditions), 5), sharey=True)
    if len(contracting_conditions) == 1:
        axes = [axes]

    for ax, condition in zip(axes, contracting_conditions):
        runs = _load_runs(condition)
        if not runs:
            continue

        def _count_field(runs, key):
            n_rounds = len(runs[0]["rounds"])
            out = []
            for r in range(n_rounds):
                vals = [len(run["rounds"][r].get(key, [])) for run in runs if r < len(run["rounds"])]
                out.append(np.mean(vals) if vals else 0.0)
            return out

        rounds = list(range(1, len(runs[0]["rounds"]) + 1))
        proposed  = _count_field(runs, "contracts_proposed")
        active    = _count_field(runs, "contracts_active")
        executed  = _count_field(runs, "contracts_executed_this_round")
        breached  = _count_field(runs, "contracts_breached_this_round")

        ax.plot(rounds, proposed, label="Proposed", linewidth=1.5, linestyle="--")
        ax.plot(rounds, active,   label="Active",   linewidth=1.5)
        ax.plot(rounds, executed, label="Executed", linewidth=1.5)
        ax.plot(rounds, breached, label="Breached", linewidth=1.5, color="red")
        ax.set_title(f"Condition {condition}")
        ax.set_xlabel("Round")
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)

    axes[0].set_ylabel("Mean contract count")
    fig.suptitle("Contract Utilisation by Round", fontsize=13, fontweight="bold")
    plt.tight_layout()
    _maybe_save(fig, "contract_utilisation.png", save)


def plot_mediation_utilisation(save: bool = True) -> None:
    """For mediation conditions: fraction of trades mediated per round."""
    mediation_conditions = [c for c in CONDITIONS if "M" in c]
    if not mediation_conditions:
        return

    fig, ax = plt.subplots(figsize=(12, 6))
    for condition in mediation_conditions:
        runs = _load_runs(condition)
        if not runs:
            continue
        n_rounds = len(runs[0]["rounds"])
        fractions = []
        for r in range(n_rounds):
            mediated = np.mean([run["rounds"][r].get("mediated_trade_count", 0)
                                for run in runs if r < len(run["rounds"])])
            total = np.mean([run["rounds"][r].get("trade_count", 0)
                             for run in runs if r < len(run["rounds"])])
            fractions.append(mediated / total if total > 0 else 0.0)
        rounds = list(range(1, n_rounds + 1))
        ax.plot(rounds, fractions, label=condition, color=COLORS[condition], linewidth=1.8)

    ax.set_xlabel("Round")
    ax.set_ylabel("Fraction of trades mediated")
    ax.set_ylim(0, 1.05)
    ax.set_title("Mediation Utilisation Over Rounds", fontweight="bold")
    ax.legend(fontsize=9)
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    _maybe_save(fig, "mediation_utilisation.png", save)


def plot_reputation_trajectories(save: bool = True) -> None:
    """For reputation conditions: mean and min reputation score over rounds."""
    reputation_conditions = [c for c in CONDITIONS if "R" in c]
    if not reputation_conditions:
        return

    fig, axes = plt.subplots(1, len(reputation_conditions),
                              figsize=(5 * len(reputation_conditions), 5), sharey=True)
    if len(reputation_conditions) == 1:
        axes = [axes]

    for ax, condition in zip(axes, reputation_conditions):
        runs = _load_runs(condition)
        if not runs:
            continue
        n_rounds = len(runs[0]["rounds"])
        mean_rep, min_rep = [], []
        for r in range(n_rounds):
            all_scores = []
            min_scores = []
            for run in runs:
                if r >= len(run["rounds"]):
                    continue
                rep = run["rounds"][r].get("reputation", {})
                scores = list(rep.values())
                if scores:
                    all_scores.extend(scores)
                    min_scores.append(min(scores))
            mean_rep.append(np.mean(all_scores) if all_scores else 1.0)
            min_rep.append(np.mean(min_scores) if min_scores else 1.0)

        rounds = list(range(1, n_rounds + 1))
        ax.plot(rounds, mean_rep, label="Mean reputation", color=COLORS[condition], linewidth=1.8)
        ax.plot(rounds, min_rep, label="Min reputation", color=COLORS[condition],
                linewidth=1.5, linestyle="--", alpha=0.7)
        ax.axhline(0.5, color="black", linestyle=":", linewidth=0.8, alpha=0.5)
        ax.set_title(f"Condition {condition}")
        ax.set_xlabel("Round")
        ax.set_ylim(0, 1.05)
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.3)

    axes[0].set_ylabel("Reputation score")
    fig.suptitle("Reputation Score Trajectories", fontsize=13, fontweight="bold")
    plt.tight_layout()
    _maybe_save(fig, "reputation_trajectories.png", save)


def plot_utility_distribution(save: bool = True) -> None:
    """Boxplot: final round utility distribution across agents per condition."""
    labels, all_utils = [], []
    for condition in CONDITIONS:
        runs = _load_runs(condition)
        if not runs:
            continue
        utils = []
        for run in runs:
            final_round = run["rounds"][-1]
            utils.extend(final_round.get("utilities", {}).values())
        labels.append(condition)
        all_utils.append(utils)

    fig, ax = plt.subplots(figsize=(12, 6))
    bp = ax.boxplot(all_utils, labels=labels, patch_artist=True, notch=False)
    for patch, condition in zip(bp["boxes"], labels):
        patch.set_facecolor(COLORS[condition])
        patch.set_alpha(0.7)
    ax.axhline(0, color="black", linestyle="--", linewidth=0.8, alpha=0.4)
    ax.set_ylabel("Agent utility (final round)")
    ax.set_title("Utility Distribution Across Agents by Condition (Final Round)", fontweight="bold")
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    _maybe_save(fig, "utility_distribution.png", save)


def plot_all(save: bool = True) -> None:
    plot_metric_trajectories(save)
    plot_final_metrics_heatmap(save)
    plot_defection_rates(save)
    plot_intermediate_variables(save)
    plot_stability_rates(save)
    plot_defection_trajectory(save)
    plot_trade_volume(save)
    plot_contract_utilisation(save)
    plot_mediation_utilisation(save)
    plot_reputation_trajectories(save)
    plot_utility_distribution(save)
    print(f"Plots saved to {OUT_DIR}")


def _maybe_save(fig: plt.Figure, filename: str, save: bool) -> None:
    if save:
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        fig.savefig(OUT_DIR / filename, dpi=150, bbox_inches="tight")
        plt.close(fig)
    else:
        plt.show()
