"""Generate charts from JSON run logs."""
from __future__ import annotations
import json
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np

from ..config import COOPERATION_THRESHOLD, CONDITIONS, DATA_DIR

OUT_DIR = Path(__file__).parent.parent / "data" / "plots"

METRICS = ["sustainability", "peace"]
INTERMEDIATE = ["whistleblowing_rate", "false_accusation_rate", "warning_accuracy"]
COLORS = dict(zip(CONDITIONS, cm.tab20(np.linspace(0, 1, len(CONDITIONS)))))

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
    """2×4 grid — one panel per condition, each showing Sustainability and Peace over rounds."""
    n_cols = 4
    n_rows = 2
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(16, 7), sharex=True, sharey=True)
    axes_flat = axes.flatten()

    for ax, condition in zip(axes_flat, CONDITIONS):
        runs = _load_runs(condition)
        if runs:
            for metric, color, label in zip(
                METRICS,
                ["tab:green", "tab:blue"],
                ["Sustainability", "Peace"],
            ):
                trajectory = _mean_metric_over_rounds(runs, metric)
                rounds = list(range(1, len(trajectory) + 1))
                ax.plot(rounds, trajectory, label=label, color=color, linewidth=1.8)

        ax.axhline(COOPERATION_THRESHOLD, color="black", linestyle="--", linewidth=0.8, alpha=0.5)
        ax.set_title(condition, fontweight="bold")
        ax.set_ylim(0, 1.05)
        ax.grid(True, alpha=0.3)

    for ax in axes_flat[len(CONDITIONS):]:
        ax.set_visible(False)

    for ax in axes[-1]:
        ax.set_xlabel("Round")
    for ax in axes[:, 0]:
        ax.set_ylabel("Metric value")

    handles, labels = axes_flat[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=3, fontsize=9, bbox_to_anchor=(0.5, -0.02))
    fig.suptitle("Sustainability and Peace Over Rounds by Condition", fontsize=14, fontweight="bold")
    plt.tight_layout()
    _maybe_save(fig, "metric_trajectories.png", save)


def plot_final_metrics_heatmap(save: bool = True) -> None:
    """Heatmap: conditions × metrics, value = mean over all rounds (not just final round)."""
    data = np.zeros((len(CONDITIONS), len(METRICS)))
    for i, condition in enumerate(CONDITIONS):
        runs = _load_runs(condition)
        for j, metric in enumerate(METRICS):
            vals = [
                rnd["metrics"].get(metric, 0)
                for run in runs
                for rnd in run["rounds"]
            ]
            data[i, j] = np.mean(vals) if vals else 0.0

    fig, ax = plt.subplots(figsize=(8, 6))
    im = ax.imshow(data, cmap="RdYlGn", vmin=0, vmax=1, aspect="auto")
    ax.set_xticks(range(len(METRICS)))
    ax.set_xticklabels([m.capitalize() for m in METRICS])
    ax.set_yticks(range(len(CONDITIONS)))
    ax.set_yticklabels(CONDITIONS)
    plt.colorbar(im, ax=ax, label="Mean value (all rounds)")
    for i in range(len(CONDITIONS)):
        for j in range(len(METRICS)):
            ax.text(j, i, f"{data[i, j]:.2f}", ha="center", va="center", fontsize=9)
    ax.set_title("Mean Metrics Over All Rounds by Condition", fontweight="bold")
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

def plot_marketplace_cooperation_rates(save: bool = True) -> None:
    """Bar chart: fraction of runs achieving marketplace cooperation per condition."""
    labels, rates = [], []
    for condition in CONDITIONS:
        runs = _load_runs(condition)
        if not runs:
            continue
        cooperative = sum(
            1 for run in runs
            if all(
                run["rounds"][-1]["metrics"].get(m, 0) > COOPERATION_THRESHOLD
                for m in METRICS
            )
        )
        labels.append(condition)
        rates.append(cooperative / len(runs))

    fig, ax = plt.subplots(figsize=(10, 5))
    x = np.arange(len(labels))
    bars = ax.bar(x, rates, color=[COLORS[c] for c in labels], alpha=0.85)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("Marketplace cooperation rate")
    ax.set_ylim(0, 1.1)
    ax.axhline(1.0, color="green", linestyle="--", linewidth=0.8, alpha=0.5)
    for bar, rate in zip(bars, rates):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.02,
                f"{rate:.0%}", ha="center", va="bottom", fontsize=9, fontweight="bold")
    ax.set_title("Marketplace Cooperation Rate by Condition\n(Sustainability and Peace > 0.5 at final round)", fontweight="bold")
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    _maybe_save(fig, "marketplace_cooperation_rates.png", save)


def plot_defection_trajectory(save: bool = True) -> None:
    """2×4 grid — one panel per condition showing defection count over rounds."""
    n_cols = 4
    n_rows = 2
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(16, 7), sharex=True)
    axes_flat = axes.flatten()

    for ax, condition in zip(axes_flat, CONDITIONS):
        runs = _load_runs(condition)
        if runs:
            trajectory = _mean_round_field(runs, "defections")
            rounds = list(range(1, len(trajectory) + 1))
            ax.plot(rounds, trajectory, color=COLORS[condition], linewidth=1.8)
            ax.fill_between(rounds, trajectory, alpha=0.15, color=COLORS[condition])
        ax.set_title(condition, fontweight="bold")
        ax.grid(True, alpha=0.3)

    for ax in axes_flat[len(CONDITIONS):]:
        ax.set_visible(False)

    for ax in axes[-1]:
        ax.set_xlabel("Round")
    for ax in axes[:, 0]:
        ax.set_ylabel("Defections per round")

    fig.suptitle("Defection Count Over Rounds by Condition", fontsize=14, fontweight="bold")
    plt.tight_layout()
    _maybe_save(fig, "defection_trajectory.png", save)


def plot_trade_volume(save: bool = True) -> None:
    """2×4 grid — one panel per condition showing trade volume over rounds."""
    n_cols = 4
    n_rows = 2
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(16, 7), sharex=True)
    axes_flat = axes.flatten()

    for ax, condition in zip(axes_flat, CONDITIONS):
        runs = _load_runs(condition)
        if runs:
            trajectory = _mean_round_field(runs, "trade_count")
            rounds = list(range(1, len(trajectory) + 1))
            ax.plot(rounds, trajectory, color=COLORS[condition], linewidth=1.8)
            ax.fill_between(rounds, trajectory, alpha=0.15, color=COLORS[condition])
        ax.set_title(condition, fontweight="bold")
        ax.grid(True, alpha=0.3)

    for ax in axes_flat[len(CONDITIONS):]:
        ax.set_visible(False)

    for ax in axes[-1]:
        ax.set_xlabel("Round")
    for ax in axes[:, 0]:
        ax.set_ylabel("Trades per round")

    fig.suptitle("Trade Volume Over Rounds by Condition", fontsize=14, fontweight="bold")
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


def _load_signals(condition: str) -> list[dict]:
    """Load all signal extraction files for a condition."""
    signals_dir = Path(__file__).parent.parent / "data" / "signals"
    files = sorted(signals_dir.glob(f"{condition}_run_*_signals.json"))
    results = []
    for f in files:
        with open(f) as fp:
            results.append(json.load(fp))
    return results


def _mean_signal_over_rounds(signal_runs: list[dict], signal_name: str) -> list[float]:
    """Average a signal across runs, per round."""
    if not signal_runs:
        return []
    n_rounds = len(signal_runs[0].get("rounds", []))
    values = []
    for r in range(n_rounds):
        round_vals = [
            run["rounds"][r].get("signals", {}).get(signal_name, 0.0)
            for run in signal_runs if r < len(run.get("rounds", []))
        ]
        values.append(np.mean(round_vals) if round_vals else 0.0)
    return values


from .reasoning_analyst import SIGNAL_NAMES
SIGNAL_COLORS = dict(zip(SIGNAL_NAMES, cm.Set2(np.linspace(0, 1, len(SIGNAL_NAMES)))))


def plot_signal_timelines(save: bool = True) -> None:
    """For each condition: signals over time (bottom) vs Peace/Sustainability (top)."""
    signals_dir = Path(__file__).parent.parent / "data" / "signals"
    if not signals_dir.exists():
        print("No signal data found. Run --extract-signals first.")
        return

    fig, axes = plt.subplots(len(CONDITIONS), 2, figsize=(16, 3 * len(CONDITIONS)),
                              sharex=True)
    if len(CONDITIONS) == 1:
        axes = [axes]

    for row, condition in enumerate(CONDITIONS):
        sig_runs = _load_signals(condition)
        metric_runs = _load_runs(condition)
        if not sig_runs or not metric_runs:
            continue

        n_rounds = len(sig_runs[0].get("rounds", []))
        rounds = list(range(1, n_rounds + 1))

        ax_metric = axes[row][0]
        peace = _mean_metric_over_rounds(metric_runs, "peace")
        sust = _mean_metric_over_rounds(metric_runs, "sustainability")
        ax_metric.plot(rounds, peace, label="Peace", linewidth=2, color="tab:blue")
        ax_metric.plot(rounds, sust, label="Sustainability", linewidth=2, color="tab:green")
        ax_metric.axhline(COOPERATION_THRESHOLD, color="black", linestyle="--",
                          linewidth=0.8, alpha=0.5)
        ax_metric.set_ylim(0, 1.05)
        ax_metric.set_ylabel(condition, fontweight="bold", fontsize=11)
        ax_metric.grid(True, alpha=0.3)
        if row == 0:
            ax_metric.set_title("Behavioral Metrics", fontweight="bold")
            ax_metric.legend(fontsize=7)

        ax_signal = axes[row][1]
        for sig_name in SIGNAL_NAMES:
            trajectory = _mean_signal_over_rounds(sig_runs, sig_name)
            if trajectory:
                ax_signal.plot(rounds[:len(trajectory)], trajectory,
                               label=sig_name.replace("_", " "),
                               color=SIGNAL_COLORS[sig_name], linewidth=1.5)
        ax_signal.set_ylim(0, 1.05)
        ax_signal.grid(True, alpha=0.3)
        if row == 0:
            ax_signal.set_title("Social Signals", fontweight="bold")
            ax_signal.legend(fontsize=6, ncol=2)

    axes[-1][0].set_xlabel("Round")
    axes[-1][1].set_xlabel("Round")
    fig.suptitle("Social Signals vs Behavioral Metrics Over Time",
                 fontsize=14, fontweight="bold")
    plt.tight_layout()
    _maybe_save(fig, "signal_timelines.png", save)


def plot_lead_lag_heatmap(save: bool = True) -> None:
    """Heatmap: signals × conditions, cell = best early warning lag (rounds ahead)."""
    from .reasoning_analyst import compute_lead_lag

    signals_dir = Path(__file__).parent.parent / "data" / "signals"
    if not signals_dir.exists():
        print("No signal data found. Run --extract-signals first.")
        return

    conditions_with_signals = [
        c for c in CONDITIONS
        if list(signals_dir.glob(f"{c}_run_*_signals.json"))
    ]
    if not conditions_with_signals:
        print("No signal data found for any condition.")
        return

    lag_data = np.zeros((len(SIGNAL_NAMES), len(conditions_with_signals)))
    corr_data = np.zeros_like(lag_data)

    for j, cond in enumerate(conditions_with_signals):
        lead_lag = compute_lead_lag(cond)
        for i, sig in enumerate(SIGNAL_NAMES):
            peace_corr = lead_lag[sig]["peace"]["best_correlation"]
            sust_corr = lead_lag[sig]["sustainability"]["best_correlation"]
            if peace_corr < sust_corr:
                corr_data[i, j] = peace_corr
                lag_data[i, j] = lead_lag[sig]["peace"]["best_early_warning_lag"]
            else:
                corr_data[i, j] = sust_corr
                lag_data[i, j] = lead_lag[sig]["sustainability"]["best_early_warning_lag"]

    fig, ax = plt.subplots(figsize=(max(8, 2 * len(conditions_with_signals)),
                                     1 + len(SIGNAL_NAMES)))
    im = ax.imshow(-corr_data, cmap="YlOrRd", vmin=0, vmax=1, aspect="auto")
    ax.set_xticks(range(len(conditions_with_signals)))
    ax.set_xticklabels(conditions_with_signals)
    ax.set_yticks(range(len(SIGNAL_NAMES)))
    ax.set_yticklabels([s.replace("_", " ").title() for s in SIGNAL_NAMES])
    plt.colorbar(im, ax=ax, label="Early warning strength (|correlation|)")
    for i in range(len(SIGNAL_NAMES)):
        for j in range(len(conditions_with_signals)):
            c = corr_data[i, j]
            lag = int(lag_data[i, j])
            if c < -0.15:
                ax.text(j, i, f"{lag}r\n{c:.2f}", ha="center", va="center",
                        fontsize=8, fontweight="bold")
            else:
                ax.text(j, i, "—", ha="center", va="center", fontsize=9, color="gray")
    ax.set_title("Early Warning Signals: Lead Time (rounds) & Correlation Strength",
                 fontweight="bold")
    plt.tight_layout()
    _maybe_save(fig, "lead_lag_heatmap.png", save)


def plot_stability_rates(save: bool = True) -> None:
    """Bar chart: fraction of rounds (across all runs) where BOTH sustainability AND peace
    exceed the cooperation threshold, per condition.

    Uses the mean metric value over all rounds — not just the final round — so that peace
    is not evaluated at a single potentially noisy endpoint.
    """
    labels, stable_fractions = [], []

    for condition in CONDITIONS:
        runs = _load_runs(condition)
        if not runs:
            continue

        stable_rounds = 0
        total_rounds = 0
        for run in runs:
            for rnd in run["rounds"]:
                sust = rnd["metrics"].get("sustainability", 0)
                peace = rnd["metrics"].get("peace", 0)
                if sust > COOPERATION_THRESHOLD and peace > COOPERATION_THRESHOLD:
                    stable_rounds += 1
                total_rounds += 1

        labels.append(condition)
        stable_fractions.append(stable_rounds / total_rounds if total_rounds > 0 else 0.0)

    fig, ax = plt.subplots(figsize=(10, 5))
    x = np.arange(len(labels))
    bars = ax.bar(x, stable_fractions, color=[COLORS[c] for c in labels], alpha=0.85)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("Fraction of rounds both metrics > 0.5")
    ax.set_ylim(0, 1.1)
    ax.axhline(1.0, color="green", linestyle="--", linewidth=0.8, alpha=0.5)
    for bar, frac in zip(bars, stable_fractions):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.02,
                f"{frac:.0%}", ha="center", va="bottom", fontsize=9, fontweight="bold")
    ax.set_title(
        "Stability Rate by Condition\n"
        "(Fraction of rounds with Sustainability > 0.5 AND Peace > 0.5)",
        fontweight="bold",
    )
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    _maybe_save(fig, "stability_rates.png", save)


def plot_network_snapshots(save: bool = True, snapshot_rounds: tuple[int, ...] = (10, 30)) -> None:
    """Draw network graph snapshots for condition N at specified rounds."""
    import networkx as nx

    runs = _load_runs("N")
    if not runs:
        print("  [network_snapshots] No N-condition runs found, skipping.")
        return

    for run_idx, run in enumerate(runs):
        specialties = run["session_log"]["specialties"]
        valid_ids = {int(a) for a in specialties}
        rounds_data = run["rounds"]
        n_rounds = len(rounds_data)

        available = [r for r in snapshot_rounds if r <= n_rounds]
        if not available:
            continue

        fig, axes = plt.subplots(1, len(available), figsize=(10 * len(available), 9))
        if len(available) == 1:
            axes = [axes]

        # Fixed circular layout — all 18 nodes evenly spaced
        pos = nx.circular_layout(nx.path_graph(len(valid_ids)))
        pos = {i: pos[i] for i in range(len(valid_ids))}

        for ax, rnd in zip(axes, available):
            rnd_data = rounds_data[rnd - 1]
            net = rnd_data.get("network")
            if net is None:
                ax.set_visible(False)
                continue

            G = nx.Graph()
            G.add_nodes_from(sorted(valid_ids))
            for aid_str, neighbors in net.items():
                for nb in neighbors:
                    if int(aid_str) in valid_ids and nb in valid_ids:
                        G.add_edge(int(aid_str), nb)

            node_list = sorted(G.nodes())
            degrees = [G.degree(n) for n in node_list]

            # Node size = reputation (scaled for visibility)
            rep_scores = rnd_data.get("reputation", {})
            rep_vals = [float(rep_scores.get(str(n), 0.5)) for n in node_list]
            node_sizes = [max(200, r * 1200) for r in rep_vals]

            # Color: blue gradient by reputation (darker = higher rep)
            node_colors = [plt.cm.Blues(0.3 + 0.7 * r) for r in rep_vals]

            # Isolated nodes
            isolated = [n for n in node_list if G.degree(n) == 0]

            # Draw
            nx.draw_networkx_edges(G, pos, ax=ax, alpha=0.25, width=0.8, edge_color="grey")
            nx.draw_networkx_nodes(G, pos, nodelist=node_list, ax=ax,
                                   node_color=node_colors, node_size=node_sizes,
                                   edgecolors="black", linewidths=1.0, alpha=0.9)
            nx.draw_networkx_labels(G, pos, ax=ax, font_size=8, font_weight="bold")

            if isolated:
                nx.draw_networkx_nodes(G, pos, nodelist=isolated, ax=ax,
                                       node_color="white", node_size=350,
                                       edgecolors="red", linewidths=2.5)

            events = rnd_data.get("network_events_this_round", [])
            severs = sum(1 for e in events if e["type"] == "sever" and e["outcome"] == "applied")
            requests = sum(1 for e in events if e["type"] == "request" and e["outcome"] == "applied")
            avg_degree = np.mean(degrees) if degrees else 0

            ax.set_title(
                f"Round {rnd}\n"
                f"Avg degree: {avg_degree:.1f}  |  Isolated: {len(isolated)}  |  "
                f"Severs: {severs}  |  New links: {requests}",
                fontsize=11, fontweight="bold",
            )
            ax.axis("off")

        # Legend
        for sz, label in [(200, "Rep ~ 0.2"), (600, "Rep ~ 0.5"), (1200, "Rep ~ 1.0")]:
            axes[0].scatter([], [], c="#4a90d9", s=sz, label=label, edgecolors="black", linewidths=1.0)
        axes[0].scatter([], [], c="white", s=200, label="Isolated", edgecolors="red", linewidths=2.5)
        axes[0].legend(loc="upper left", fontsize=9, framealpha=0.9, title="Node size = reputation")

        fig.suptitle(f"Condition N — Network Topology (Run {run_idx})", fontsize=14, fontweight="bold")
        plt.tight_layout()
        _maybe_save(fig, f"network_snapshot_run{run_idx:02d}.png", save)


def plot_all(save: bool = True) -> None:
    plot_metric_trajectories(save)
    plot_final_metrics_heatmap(save)
    plot_defection_rates(save)
    plot_intermediate_variables(save)
    plot_marketplace_cooperation_rates(save)
    plot_stability_rates(save)
    plot_defection_trajectory(save)
    plot_trade_volume(save)
    plot_contract_utilisation(save)
    plot_mediation_utilisation(save)
    plot_reputation_trajectories(save)
    plot_utility_distribution(save)
    plot_signal_timelines(save)
    plot_lead_lag_heatmap(save)
    plot_network_snapshots(save)
    print(f"Plots saved to {OUT_DIR}")


def _maybe_save(fig: plt.Figure, filename: str, save: bool) -> None:
    if save:
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        fig.savefig(OUT_DIR / filename, dpi=150, bbox_inches="tight")
        plt.close(fig)
    else:
        plt.show()
