"""Generate charts from JSON run logs."""
from __future__ import annotations
import json
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np

from .. import config
from ..config import COOPERATION_THRESHOLD, CONDITIONS, CONDITION_MECHANISMS

def _get_out_dir(n_trolls: int = 0) -> Path:
    """Plots output directory: plots/<model>/ or plots/<model>/troll_<N>/."""
    model_tag = config.DATA_DIR.name
    base = Path(__file__).parent.parent / "data" / "plots" / model_tag
    if n_trolls > 0:
        return base / f"troll_{n_trolls}"
    return base

OUT_DIR = Path(__file__).parent.parent / "data" / "plots"  # updated dynamically in plot_all
_N_TROLLS = 0  # set by plot_all(), controls which log files to load

METRICS = ["sustainability", "peace"]
INTERMEDIATE = ["whistleblowing_rate", "false_accusation_rate", "warning_accuracy"]
COLORS = dict(zip(CONDITIONS, cm.tab20(np.linspace(0, 1, len(CONDITIONS)))))

def _load_runs(condition: str) -> list[dict]:
    if _N_TROLLS > 0:
        files = sorted(config.DATA_DIR.glob(f"{condition}_t{_N_TROLLS}_run_*.json"))
    else:
        files = sorted(config.DATA_DIR.glob(f"{condition}_run_*.json"))
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


def _get_troll_ids(run: dict) -> set[str]:
    """Extract troll agent IDs from a run's session log (as strings for utilities dict keys)."""
    return set(str(tid) for tid in run.get("session_log", {}).get("troll_ids", []))


# ── Plots ─────────────────────────────────────────────────────────────────────

def plot_metric_trajectories(save: bool = True) -> None:
    """2×4 grid — one panel per condition, each showing Production Stability and Cooperation Rate over rounds."""
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
                ["Production Stability", "Cooperation Rate"],
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
    fig.suptitle("Production Stability and Cooperation Rate Over Rounds by Condition", fontsize=14, fontweight="bold")
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
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
    metric_labels = {"sustainability": "Production Stability", "peace": "Cooperation Rate"}
    ax.set_xticklabels([metric_labels.get(m, m.capitalize()) for m in METRICS])
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

    if not labels:
        print("  [defection_rates] No data found, skipping.")
        return

    fig, ax = plt.subplots(figsize=(10, 5))
    x = np.arange(len(labels))
    ax.bar(x, means, yerr=stds, capsize=5, color=[COLORS[c] for c in labels], alpha=0.85)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("Defection rate (1 - Cooperation Rate)")
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
        ax.set_ylim(0, max(max(means) * 1.2, 0.1) if means else 1)
        ax.grid(axis="y", alpha=0.3)

    fig.suptitle("Intermediate Variables by Condition", fontsize=13, fontweight="bold")
    plt.tight_layout(rect=[0, 0, 1, 0.95])
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

    if not labels:
        print("  [marketplace_cooperation_rates] No data found, skipping.")
        return

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
    ax.set_title("Marketplace Cooperation Rate by Condition\n(Production Stability and Cooperation Rate > 0.5 at final round)", fontweight="bold")
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
    plt.tight_layout(rect=[0, 0, 1, 0.95])
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
    plt.tight_layout(rect=[0, 0, 1, 0.95])
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
    plt.tight_layout(rect=[0, 0, 1, 0.95])
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
    if all(f == 0.0 for f in fractions):
        ax.text(0.5, 0.5, "No agents delegated to the mediator",
                ha="center", va="center", transform=ax.transAxes,
                fontsize=14, color="gray", fontstyle="italic")
    plt.tight_layout()
    _maybe_save(fig, "mediation_utilisation.png", save)


def plot_reputation_trajectories(save: bool = True) -> None:
    """For reputation conditions: mean and min reputation score over rounds."""
    reputation_conditions = [c for c in CONDITIONS if "reputation" in CONDITION_MECHANISMS.get(c, [])]
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
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    _maybe_save(fig, "reputation_trajectories.png", save)


def plot_utility_distribution(save: bool = True) -> None:
    """Boxplot: final round utility distribution across agents per condition (trolls excluded)."""
    labels, all_utils = [], []
    for condition in CONDITIONS:
        runs = _load_runs(condition)
        if not runs:
            continue
        utils = []
        for run in runs:
            troll_ids = _get_troll_ids(run)
            final_round = run["rounds"][-1]
            utilities = final_round.get("utilities", {})
            utils.extend(float(v) for k, v in utilities.items() if k not in troll_ids)
        if utils:
            labels.append(condition)
            all_utils.append(utils)

    if not all_utils:
        print("  [utility_distribution] No utility data found, skipping.")
        return

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
    """For each condition: signals over time (bottom) vs Cooperation Rate/Production Stability (top)."""
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
        ax_metric.plot(rounds, peace, label="Cooperation Rate", linewidth=2, color="tab:blue")
        ax_metric.plot(rounds, sust, label="Production Stability", linewidth=2, color="tab:green")
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
    plt.tight_layout(rect=[0, 0, 1, 0.97])
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

    if not labels:
        print("  [stability_rates] No data found, skipping.")
        return

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
        "(Fraction of rounds with Production Stability > 0.5 AND Cooperation Rate > 0.5)",
        fontweight="bold",
    )
    ax.grid(axis="y", alpha=0.3)
    plt.tight_layout()
    _maybe_save(fig, "stability_rates.png", save)


def plot_network_snapshots(save: bool = True, snapshot_rounds: tuple[int, ...] = (10, 30)) -> None:
    """Draw network graph snapshots for conditions with network rewiring."""
    import networkx as nx
    import math
    from matplotlib.lines import Line2D
    from matplotlib.colors import LinearSegmentedColormap

    rep_cmap = LinearSegmentedColormap.from_list("rep", ["#d32f2f", "#ff9800", "#2196f3", "#1565c0"])

    network_conditions = [c for c in CONDITIONS if "network_rewiring" in CONDITION_MECHANISMS.get(c, [])]
    all_runs: list[tuple[str, int, dict]] = []
    for cond in network_conditions:
        for idx, run in enumerate(_load_runs(cond)):
            all_runs.append((cond, idx, run))
    if not all_runs:
        print("  [network_snapshots] No network-rewiring condition runs found, skipping.")
        return

    for cond, run_idx, run in all_runs:
        specialties = run["session_log"]["specialties"]
        valid_ids = sorted(int(a) for a in specialties)
        rounds_data = run["rounds"]
        n_rounds = len(rounds_data)

        available = [r for r in snapshot_rounds if r <= n_rounds]
        if not available:
            continue

        fig, axes = plt.subplots(1, len(available), figsize=(10 * len(available), 10))
        if len(available) == 1:
            axes = [axes]

        n = len(valid_ids)
        pos = {}
        for i, aid in enumerate(valid_ids):
            angle = 2 * math.pi * i / n - math.pi / 2
            pos[aid] = (math.cos(angle), math.sin(angle))

        for ax, rnd in zip(axes, available):
            rnd_data = rounds_data[rnd - 1]
            net = rnd_data.get("network")
            if net is None:
                ax.set_visible(False)
                continue

            G = nx.Graph()
            G.add_nodes_from(valid_ids)
            for aid_str, neighbors in net.items():
                for nb in neighbors:
                    if int(aid_str) in pos and nb in pos:
                        G.add_edge(int(aid_str), nb)

            node_list = sorted(G.nodes())
            degrees = {n_: G.degree(n_) for n_ in node_list}

            rep_scores = rnd_data.get("reputation", {})
            rep_vals = {n_: float(rep_scores.get(str(n_), 0.5)) for n_ in node_list}

            # Split agents by reputation tier (hardcoded thresholds)
            high_rep = [n_ for n_ in node_list if rep_vals[n_] >= 0.7]
            mid_rep = [n_ for n_ in node_list if 0.4 <= rep_vals[n_] < 0.7]
            low_rep = [n_ for n_ in node_list if rep_vals[n_] < 0.4]
            high_deg = np.mean([degrees[n_] for n_ in high_rep]) if high_rep else 0
            mid_deg = np.mean([degrees[n_] for n_ in mid_rep]) if mid_rep else 0
            low_deg = np.mean([degrees[n_] for n_ in low_rep]) if low_rep else 0
            isolated = [n_ for n_ in node_list if degrees[n_] == 0]

            # Draw edges
            for u, v in G.edges():
                x = [pos[u][0], pos[v][0]]
                y = [pos[u][1], pos[v][1]]
                ax.plot(x, y, color="#aaaaaa", linewidth=0.8, alpha=0.5, zorder=1)

            # Draw nodes: red (low rep) → blue (high rep), size = rep
            for n_ in node_list:
                r = rep_vals[n_]
                x, y = pos[n_]
                radius = 0.05 + r * 0.05
                color = rep_cmap(r)
                circle = plt.Circle((x, y), radius, color=color,
                                    ec="black", lw=1.2, alpha=0.9, zorder=2)
                ax.add_patch(circle)
                ax.text(x, y, str(n_), ha="center", va="center",
                        fontsize=7, fontweight="bold", color="white", zorder=3)

            # Highlight isolated with red ring
            for n_ in isolated:
                x, y = pos[n_]
                ring = plt.Circle((x, y), 0.08, fill=False, ec="red",
                                  lw=3.0, zorder=4)
                ax.add_patch(ring)

            events = rnd_data.get("network_events_this_round", [])
            severs = sum(1 for e in events if e["type"] == "sever" and e["outcome"] == "applied")
            requests = sum(1 for e in events if e["type"] == "request" and e["outcome"] == "applied")

            ax.set_xlim(-1.5, 1.5)
            ax.set_ylim(-1.5, 1.5)
            ax.set_aspect("equal")
            ax.set_title(
                f"Round {rnd}\n"
                f"High rep (≥0.7): {len(high_rep)} agents, avg {high_deg:.1f} links\n"
                f"Mid rep (0.4–0.7): {len(mid_rep)} agents, avg {mid_deg:.1f} links\n"
                f"Low rep (<0.4): {len(low_rep)} agents, avg {low_deg:.1f} links\n"
                f"Isolated: {len(isolated)}  |  Severs: {severs}  |  New links: {requests}",
                fontsize=9, fontweight="bold",
            )
            ax.axis("off")

        # Legend
        legend_items = [
            Line2D([0], [0], color="#aaaaaa", lw=1.0, alpha=0.5, label="Trade link"),
            Line2D([0], [0], marker="o", color="w", markerfacecolor="#d32f2f",
                   markersize=8, label="Low rep (small, red)"),
            Line2D([0], [0], marker="o", color="w", markerfacecolor="#ff9800",
                   markersize=10, label="Mid rep (orange)"),
            Line2D([0], [0], marker="o", color="w", markerfacecolor="#1565c0",
                   markersize=14, label="High rep (large, blue)"),
        ]
        axes[0].legend(handles=legend_items, loc="upper left", fontsize=9,
                       framealpha=0.9, title="Color & size = reputation")

        fig.suptitle(f"Condition {cond} — Network Topology (Run {run_idx})", fontsize=14, fontweight="bold")
        fig.subplots_adjust(top=0.78, wspace=0.1)
        _maybe_save(fig, f"network_snapshot_{cond}_run{run_idx:02d}.png", save)


def plot_utility_trajectories(save: bool = True) -> None:
    """2×4 grid — one panel per condition, average per-round utility with 3-round rolling average."""
    n_cols = 4
    n_rows = 2
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(16, 7), sharex=True)
    axes_flat = axes.flatten()

    for ax, condition in zip(axes_flat, CONDITIONS):
        runs = _load_runs(condition)
        if runs:
            n_rounds = max(len(run["rounds"]) for run in runs)
            raw = []
            for r in range(n_rounds):
                round_vals = []
                for run in runs:
                    if r < len(run["rounds"]):
                        troll_ids = _get_troll_ids(run)
                        utilities = run["rounds"][r].get("utilities", {})
                        non_troll = {k: v for k, v in utilities.items() if k not in troll_ids}
                        if non_troll:
                            round_vals.append(np.mean([float(v) for v in non_troll.values()]))
                raw.append(np.mean(round_vals) if round_vals else 0.0)

            # 3-round rolling average
            smoothed = np.convolve(raw, np.ones(3) / 3, mode="same")
            # fix edges: use raw values for first and last point
            smoothed[0] = raw[0]
            smoothed[-1] = raw[-1]

            rounds = list(range(1, n_rounds + 1))
            ax.plot(rounds, raw, color=COLORS[condition], linewidth=0.8, alpha=0.3)
            ax.plot(rounds, smoothed, color=COLORS[condition], linewidth=2.0, label="3-round avg")
            ax.axhline(0, color="black", linestyle="--", linewidth=0.8, alpha=0.6)
            ax.fill_between(rounds, smoothed, 0,
                            where=[v >= 0 for v in smoothed], alpha=0.12, color="green")
            ax.fill_between(rounds, smoothed, 0,
                            where=[v < 0 for v in smoothed], alpha=0.12, color="red")

        ax.set_title(condition, fontweight="bold")
        ax.grid(True, alpha=0.3)

    for ax in axes_flat[len(CONDITIONS):]:
        ax.set_visible(False)

    for ax in axes[-1]:
        ax.set_xlabel("Round")
    for ax in axes[:, 0]:
        ax.set_ylabel("Avg utility per agent")

    fig.suptitle("Average Per-Round Utility by Condition (3-round rolling average)\nGreen = net positive, Red = net negative",
                 fontsize=13, fontweight="bold")
    plt.tight_layout(rect=[0, 0, 1, 0.93])
    _maybe_save(fig, "utility_trajectories.png", save)


def _load_runs_from(data_dir: Path, condition: str) -> list[dict]:
    """Load runs from a specific data directory (not config.DATA_DIR)."""
    files = sorted(data_dir.glob(f"{condition}_run_*.json"))
    runs = []
    for f in files:
        with open(f) as fp:
            runs.append(json.load(fp))
    return runs


def plot_model_comparison(save: bool = True) -> None:
    """Side-by-side comparison of per-round utility trajectories across models.

    Top row: gpt-5.4-mini, bottom row: deepseek-v3 (or whichever models have data).
    One column per condition. Allows visual comparison of whether mechanisms are
    robust to model choice.
    """
    base_dir = Path(__file__).parent.parent / "data" / "runs"
    model_dirs = sorted([d for d in base_dir.iterdir() if d.is_dir() and any(d.glob("*_run_*.json"))])

    if len(model_dirs) < 2:
        print("  [model_comparison] Need data from at least 2 models. Skipping.")
        return

    model_names = [d.name for d in model_dirs]
    conditions_with_data = []
    for cond in CONDITIONS:
        if all(any(d.glob(f"{cond}_run_*.json")) for d in model_dirs):
            conditions_with_data.append(cond)

    if not conditions_with_data:
        print("  [model_comparison] No conditions have data across all models. Skipping.")
        return

    n_models = len(model_dirs)
    n_conds = len(conditions_with_data)
    fig, axes = plt.subplots(n_models, n_conds, figsize=(4 * n_conds, 4 * n_models),
                              sharex=True, sharey=True, squeeze=False)

    for row, (model_dir, model_name) in enumerate(zip(model_dirs, model_names)):
        for col, condition in enumerate(conditions_with_data):
            ax = axes[row][col]
            runs = _load_runs_from(model_dir, condition)

            if runs:
                n_rounds = max(len(run["rounds"]) for run in runs)
                raw = []
                for r in range(n_rounds):
                    round_vals = []
                    for run in runs:
                        if r < len(run["rounds"]):
                            troll_ids = _get_troll_ids(run)
                            utilities = run["rounds"][r].get("utilities", {})
                            non_troll = {k: v for k, v in utilities.items() if k not in troll_ids}
                            if non_troll:
                                round_vals.append(np.mean([float(v) for v in non_troll.values()]))
                    raw.append(np.mean(round_vals) if round_vals else 0.0)

                smoothed = np.convolve(raw, np.ones(3) / 3, mode="same")
                smoothed[0] = raw[0]
                smoothed[-1] = raw[-1]

                rounds = list(range(1, n_rounds + 1))
                ax.plot(rounds, raw, color=COLORS[condition], linewidth=0.8, alpha=0.3)
                ax.plot(rounds, smoothed, color=COLORS[condition], linewidth=2.0)
                ax.axhline(0, color="black", linestyle="--", linewidth=0.8, alpha=0.6)
                ax.fill_between(rounds, smoothed, 0,
                                where=[v >= 0 for v in smoothed], alpha=0.12, color="green")
                ax.fill_between(rounds, smoothed, 0,
                                where=[v < 0 for v in smoothed], alpha=0.12, color="red")

            ax.grid(True, alpha=0.3)
            if row == 0:
                ax.set_title(condition, fontweight="bold")
            if col == 0:
                ax.set_ylabel(model_name, fontsize=10, fontweight="bold")
            if row == n_models - 1:
                ax.set_xlabel("Round")

    fig.suptitle("Per-Round Utility by Condition — Model Comparison\n(3-round rolling average; green = positive, red = negative)",
                 fontsize=14, fontweight="bold")
    plt.tight_layout(rect=[0, 0, 1, 0.93])
    _maybe_save(fig, "model_comparison.png", save)


def _load_troll_runs(condition: str) -> list[dict]:
    """Load troll run files. Uses _N_TROLLS if set, otherwise any troll count."""
    if _N_TROLLS > 0:
        files = sorted(config.DATA_DIR.glob(f"{condition}_t{_N_TROLLS}_run_*.json"))
    else:
        files = sorted(config.DATA_DIR.glob(f"{condition}_t*_run_*.json"))
    runs = []
    for f in files:
        with open(f) as fp:
            runs.append(json.load(fp))
    return runs


def plot_troll_trade_volume(save: bool = True) -> None:
    """Line chart: trades with trolls per round, one line per condition."""
    fig, ax = plt.subplots(figsize=(12, 6))
    found_any = False

    for condition in CONDITIONS:
        runs = _load_troll_runs(condition)
        if not runs:
            continue
        troll_ids = _get_troll_ids(runs[0])
        if not troll_ids:
            continue

        n_rounds = len(runs[0]["rounds"])
        troll_trades_per_round = []
        for r in range(n_rounds):
            counts = []
            for run in runs:
                if r >= len(run["rounds"]):
                    continue
                trades = run["rounds"][r].get("trades", [])
                count = sum(
                    1 for t in trades
                    if str(t["proposer"]) in troll_ids or str(t["target"]) in troll_ids
                )
                counts.append(count)
            troll_trades_per_round.append(np.mean(counts) if counts else 0.0)

        rounds = list(range(1, n_rounds + 1))
        ax.plot(rounds, troll_trades_per_round, label=condition,
                color=COLORS[condition], linewidth=2.0)
        found_any = True

    if not found_any:
        plt.close(fig)
        print("  [troll_trade_volume] No troll runs found, skipping.")
        return

    ax.set_xlabel("Round", fontsize=12)
    ax.set_ylabel("Trades with trolls per round", fontsize=12)
    ax.set_title("Troll Isolation: Trade Volume with Trolls Over Rounds", fontweight="bold", fontsize=14)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.axhline(0, color="black", linestyle="--", linewidth=0.8, alpha=0.5)
    plt.tight_layout()
    _maybe_save(fig, "troll_trade_volume.png", save)


def plot_troll_resilience_table(save: bool = True) -> None:
    """Table comparing troll containment across conditions.

    Columns: total troll defections, avg troll trades/round (last half),
    non-troll defection rate, mean non-troll utility.
    """
    rows = []
    for condition in CONDITIONS:
        runs = _load_troll_runs(condition)
        if not runs:
            continue

        troll_ids = _get_troll_ids(runs[0])
        if not troll_ids:
            continue

        n_rounds = len(runs[0]["rounds"])
        half = n_rounds // 2

        total_troll_defections = 0
        troll_trades_last_half = []
        non_troll_defections = 0
        non_troll_trades_total = 0
        non_troll_utilities = []

        for run in runs:
            for r, rnd in enumerate(run["rounds"]):
                trades = rnd.get("trades", [])
                utilities = rnd.get("utilities", {})

                for t in trades:
                    involves_troll = str(t["proposer"]) in troll_ids or str(t["target"]) in troll_ids
                    if involves_troll:
                        if t.get("defected_by") is not None:
                            total_troll_defections += 1
                        if r >= half:
                            troll_trades_last_half.append(1)
                    else:
                        non_troll_trades_total += 1
                        if t.get("defected_by") is not None:
                            non_troll_defections += 1

                for aid, util in utilities.items():
                    if aid not in troll_ids:
                        non_troll_utilities.append(float(util))

            # Count rounds in last half for averaging
            if not troll_trades_last_half:
                troll_trades_last_half = [0]

        n_runs = len(runs)
        last_half_rounds = (n_rounds - half) * n_runs
        avg_troll_last_half = sum(troll_trades_last_half) / max(last_half_rounds, 1)
        non_troll_def_rate = non_troll_defections / max(non_troll_trades_total, 1)
        mean_utility = np.mean(non_troll_utilities) if non_troll_utilities else 0.0

        rows.append({
            "condition": condition,
            "total_troll_defections": total_troll_defections,
            "avg_troll_trades_last_half": avg_troll_last_half,
            "non_troll_defection_rate": non_troll_def_rate,
            "mean_utility": mean_utility,
        })

    if not rows:
        print("  [troll_resilience_table] No troll runs found, skipping.")
        return

    # Render as a matplotlib table figure
    fig, ax = plt.subplots(figsize=(14, 2 + 0.5 * len(rows)))
    ax.axis("off")

    col_labels = [
        "Condition",
        "Total Troll\nDefections",
        "Avg Troll Trades/Round\n(last half)",
        "Non-Troll\nDefection Rate",
        "Mean Non-Troll\nUtility",
    ]
    cell_text = []
    for r in rows:
        cell_text.append([
            r["condition"],
            str(r["total_troll_defections"]),
            f"{r['avg_troll_trades_last_half']:.2f}",
            f"{r['non_troll_defection_rate']:.1%}",
            f"{r['mean_utility']:.2f}",
        ])

    table = ax.table(
        cellText=cell_text,
        colLabels=col_labels,
        loc="center",
        cellLoc="center",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1, 1.6)

    # Style header
    for j in range(len(col_labels)):
        table[0, j].set_facecolor("#4472C4")
        table[0, j].set_text_props(color="white", fontweight="bold")

    # Alternate row colors
    for i in range(len(rows)):
        color = "#D9E2F3" if i % 2 == 0 else "white"
        for j in range(len(col_labels)):
            table[i + 1, j].set_facecolor(color)

    ax.set_title("Troll Resilience Comparison Across Mechanisms",
                 fontweight="bold", fontsize=13, pad=20)
    plt.tight_layout()
    _maybe_save(fig, "troll_resilience_table.png", save)

    # Also print to console
    print("\n  Troll Resilience Table:")
    print(f"  {'Condition':<10} {'Troll Def':>10} {'Avg Troll/Rnd':>14} {'NonTroll Def%':>14} {'Mean Util':>10}")
    print(f"  {'-'*10} {'-'*10} {'-'*14} {'-'*14} {'-'*10}")
    for r in rows:
        print(f"  {r['condition']:<10} {r['total_troll_defections']:>10} "
              f"{r['avg_troll_trades_last_half']:>14.2f} "
              f"{r['non_troll_defection_rate']:>13.1%} "
              f"{r['mean_utility']:>10.2f}")
    print()


def plot_troll_metric_trajectories(save: bool = True) -> None:
    """2×4 grid — peace and sustainability over rounds for troll runs."""
    troll_conditions = [c for c in CONDITIONS if _load_troll_runs(c)]
    if not troll_conditions:
        print("  [troll_metric_trajectories] No troll runs found, skipping.")
        return

    n_cols = 4
    n_rows = max(1, (len(troll_conditions) + n_cols - 1) // n_cols)
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(16, 4 * n_rows), sharex=True, sharey=True)
    if n_rows == 1:
        axes = axes.reshape(1, -1)
    axes_flat = axes.flatten()

    for ax, condition in zip(axes_flat, troll_conditions):
        runs = _load_troll_runs(condition)
        for metric, color, label in zip(
            METRICS,
            ["tab:green", "tab:blue"],
            ["Production Stability", "Cooperation Rate"],
        ):
            trajectory = _mean_metric_over_rounds(runs, metric)
            rounds = list(range(1, len(trajectory) + 1))
            ax.plot(rounds, trajectory, label=label, color=color, linewidth=1.8)

        ax.axhline(COOPERATION_THRESHOLD, color="black", linestyle="--", linewidth=0.8, alpha=0.5)
        ax.set_title(condition, fontweight="bold")
        ax.set_ylim(0, 1.05)
        ax.grid(True, alpha=0.3)

    for ax in axes_flat[len(troll_conditions):]:
        ax.set_visible(False)

    for ax in axes[-1]:
        ax.set_xlabel("Round")
    for ax in axes[:, 0]:
        ax.set_ylabel("Metric value")

    handles, labels = axes_flat[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=2, fontsize=9, bbox_to_anchor=(0.5, -0.02))
    fig.suptitle("Production Stability and Cooperation Rate Over Rounds (Troll Runs)", fontsize=14, fontweight="bold")
    plt.tight_layout(rect=[0, 0.03, 1, 0.95])
    _maybe_save(fig, "troll_metric_trajectories.png", save)


def plot_utility_per_agent(save: bool = True) -> None:
    """Bar chart: final-round utility per agent, one panel per condition (trolls excluded).

    Shows how equally utility is distributed across agents.
    """
    troll_conditions = [c for c in CONDITIONS if _load_troll_runs(c)]
    non_troll_conditions = [c for c in CONDITIONS if _load_runs(c) and c not in troll_conditions]
    all_conditions = non_troll_conditions + troll_conditions

    if not all_conditions:
        print("  [utility_per_agent] No runs found, skipping.")
        return

    n_cols = 4
    n_rows = max(1, (len(all_conditions) + n_cols - 1) // n_cols)
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(16, 4 * n_rows), sharey=True)
    if n_rows == 1:
        axes = axes.reshape(1, -1)
    axes_flat = axes.flatten()

    for ax, condition in zip(axes_flat, all_conditions):
        runs = _load_troll_runs(condition) or _load_runs(condition)
        if not runs:
            continue

        run = runs[0]
        troll_ids = _get_troll_ids(run)
        final_round = run["rounds"][-1]
        utilities = final_round.get("utilities", {})

        agents = sorted(
            [(int(k), float(v)) for k, v in utilities.items() if k not in troll_ids],
            key=lambda x: x[0],
        )
        if not agents:
            continue

        agent_ids = [a[0] for a in agents]
        utils = [a[1] for a in agents]
        mean_util = np.mean(utils)

        colors_bar = ["#4472C4" if u >= 0 else "#C44444" for u in utils]
        ax.bar(range(len(agent_ids)), utils, color=colors_bar, alpha=0.8)
        ax.axhline(mean_util, color="orange", linestyle="--", linewidth=1.5, alpha=0.8, label=f"Mean: {mean_util:.1f}")
        ax.set_xticks(range(len(agent_ids)))
        ax.set_xticklabels([str(a) for a in agent_ids], fontsize=7, rotation=45)
        ax.set_title(condition, fontweight="bold")
        ax.grid(axis="y", alpha=0.3)
        ax.legend(fontsize=7)

    for ax in axes_flat[len(all_conditions):]:
        ax.set_visible(False)

    for ax in axes[-1]:
        ax.set_xlabel("Agent ID")
    for ax in axes[:, 0]:
        ax.set_ylabel("Utility (final round)")

    fig.suptitle("Per-Agent Utility Distribution at Final Round\n(Blue = positive, Red = negative)",
                 fontsize=13, fontweight="bold")
    plt.tight_layout(rect=[0, 0, 1, 0.93])
    _maybe_save(fig, "utility_per_agent.png", save)


def plot_cumulative_utility(save: bool = True) -> None:
    """2×4 grid — cumulative mean utility over rounds per condition (trolls excluded)."""
    n_cols = 4
    n_rows = 2
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(16, 7), sharex=True)
    axes_flat = axes.flatten()

    for ax, condition in zip(axes_flat, CONDITIONS):
        runs = _load_troll_runs(condition) or _load_runs(condition)
        if not runs:
            ax.set_title(condition, fontweight="bold")
            ax.grid(True, alpha=0.3)
            continue

        n_rounds = max(len(run["rounds"]) for run in runs)
        cumulative = []
        running_sum = 0.0
        for r in range(n_rounds):
            round_vals = []
            for run in runs:
                if r < len(run["rounds"]):
                    troll_ids = _get_troll_ids(run)
                    utilities = run["rounds"][r].get("utilities", {})
                    non_troll = [float(v) for k, v in utilities.items() if k not in troll_ids]
                    if non_troll:
                        round_vals.append(np.mean(non_troll))
            running_sum += np.mean(round_vals) if round_vals else 0.0
            cumulative.append(running_sum)

        rounds = list(range(1, n_rounds + 1))
        ax.plot(rounds, cumulative, color=COLORS[condition], linewidth=2.0)
        ax.axhline(0, color="black", linestyle="--", linewidth=0.8, alpha=0.6)
        ax.fill_between(rounds, cumulative, 0,
                        where=[v >= 0 for v in cumulative], alpha=0.12, color="green")
        ax.fill_between(rounds, cumulative, 0,
                        where=[v < 0 for v in cumulative], alpha=0.12, color="red")
        ax.set_title(condition, fontweight="bold")
        ax.grid(True, alpha=0.3)

    for ax in axes_flat[len(CONDITIONS):]:
        ax.set_visible(False)
    for ax in axes[-1]:
        ax.set_xlabel("Round")
    for ax in axes[:, 0]:
        ax.set_ylabel("Cumulative avg utility")

    fig.suptitle("Cumulative Average Utility Over Rounds by Condition",
                 fontsize=13, fontweight="bold")
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    _maybe_save(fig, "cumulative_utility.png", save)


def plot_gini_trajectory(save: bool = True) -> None:
    """2×4 grid — Gini coefficient over rounds per condition."""
    n_cols = 4
    n_rows = 2
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(16, 7), sharex=True, sharey=True)
    axes_flat = axes.flatten()

    for ax, condition in zip(axes_flat, CONDITIONS):
        runs = _load_troll_runs(condition) or _load_runs(condition)
        if not runs:
            ax.set_title(condition, fontweight="bold")
            ax.grid(True, alpha=0.3)
            continue

        trajectory = _mean_metric_over_rounds(runs, "gini")
        if trajectory:
            rounds = list(range(1, len(trajectory) + 1))
            ax.plot(rounds, trajectory, color=COLORS[condition], linewidth=2.0)
            ax.fill_between(rounds, trajectory, alpha=0.15, color=COLORS[condition])

        ax.set_title(condition, fontweight="bold")
        ax.set_ylim(0, 1.05)
        ax.grid(True, alpha=0.3)

    for ax in axes_flat[len(CONDITIONS):]:
        ax.set_visible(False)
    for ax in axes[-1]:
        ax.set_xlabel("Round")
    for ax in axes[:, 0]:
        ax.set_ylabel("Gini coefficient")

    fig.suptitle("Inequality (Gini Coefficient) Over Rounds by Condition\n(0 = perfect equality, 1 = maximum inequality)",
                 fontsize=13, fontweight="bold")
    plt.tight_layout(rect=[0, 0, 1, 0.93])
    _maybe_save(fig, "gini_trajectory.png", save)


def plot_all(save: bool = True, n_trolls: int = 0) -> None:
    global OUT_DIR, _N_TROLLS
    _N_TROLLS = n_trolls
    OUT_DIR = _get_out_dir(n_trolls)
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
    plot_utility_trajectories(save)
    plot_signal_timelines(save)
    plot_lead_lag_heatmap(save)
    plot_network_snapshots(save)
    plot_troll_trade_volume(save)
    plot_troll_resilience_table(save)
    plot_troll_metric_trajectories(save)
    plot_utility_per_agent(save)
    plot_cumulative_utility(save)
    plot_gini_trajectory(save)
    plot_model_comparison(save)
    print(f"Plots saved to {OUT_DIR}")


def _maybe_save(fig: plt.Figure, filename: str, save: bool) -> None:
    if save:
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        fig.savefig(OUT_DIR / filename, dpi=150, bbox_inches="tight")
        plt.close(fig)
    else:
        plt.show()
