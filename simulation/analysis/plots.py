"""Generate charts from JSON run logs."""
from __future__ import annotations
import json
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import matplotlib.colors as mcolors
import numpy as np

from .. import config
from ..config import CONDITIONS, CONDITION_MECHANISMS

def _get_out_dir(n_trolls: int = 0, progressive: bool = False) -> Path:
    """Plots output directory: plots/<model>/ or plots/<model>/troll_<N>/."""
    model_tag = config.DATA_DIR.name
    base = Path(__file__).parent.parent / "data" / "plots" / model_tag
    if progressive:
        return base / "troll_progressive"
    if n_trolls > 0:
        return base / f"troll_{n_trolls}"
    return base

OUT_DIR = Path(__file__).parent.parent / "data" / "plots"  # updated dynamically in plot_all
_N_TROLLS = 0  # set by plot_all(), controls which log files to load
_PROGRESSIVE = False  # set by plot_all(), controls progressive troll mode

METRICS = ["gini"]


def _get_metric(rnd_metrics: dict, key: str, default=0):
    """Get metric with backward compat: old logs use 'peace', new use 'cooperation_rate'."""
    if key == "cooperation_rate":
        return rnd_metrics.get("cooperation_rate", rnd_metrics.get("peace", default))
    return rnd_metrics.get(key, default)
INTERMEDIATE = ["whistleblowing_rate", "false_accusation_rate", "warning_accuracy"]
COLORS = dict(zip(CONDITIONS, cm.tab20(np.linspace(0, 1, max(len(CONDITIONS), 1)))))

def _load_runs(condition: str) -> list[dict]:
    if _PROGRESSIVE:
        files = sorted(config.DATA_DIR.glob(f"{condition}_tprog_run_*.json"))
    elif _N_TROLLS > 0:
        files = sorted(config.DATA_DIR.glob(f"{condition}_t{_N_TROLLS}_run_*.json"))
    else:
        files = sorted(config.DATA_DIR.glob(f"{condition}_run_*.json"))
    runs = []
    for f in files:
        with open(f) as fp:
            runs.append(json.load(fp))
    return runs


def _get_troll_schedule(runs: list[dict]) -> list[tuple[int, int]]:
    """Extract troll injection schedule from run data. Returns [(round, n_new), ...]."""
    if not runs:
        return []
    schedule = runs[0].get("troll_schedule") or runs[0].get("session_log", {}).get("troll_schedule")
    if not schedule:
        return []
    return [(int(r), int(n)) for r, n in schedule]


def _draw_injection_lines(ax, schedule: list[tuple[int, int]]) -> None:
    """Draw vertical red dashed lines at troll injection rounds."""
    cumulative = 0
    for inject_round, n_new in schedule:
        cumulative += n_new
        ax.axvline(inject_round, color="red", linestyle="--", linewidth=1.0, alpha=0.6)
        ax.text(inject_round + 1, 0.95, f"+{n_new}T", transform=ax.get_xaxis_transform(),
                fontsize=7, color="red", alpha=0.8, va="top")


def _mean_metric_over_rounds(runs: list[dict], metric: str) -> list[float]:
    if not runs:
        return []
    n_rounds = len(runs[0]["rounds"])
    values = []
    for r in range(n_rounds):
        round_vals = [_get_metric(run["rounds"][r]["metrics"], metric) for run in runs if r < len(run["rounds"])]
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


def _non_troll_trade_stats(runs: list[dict]) -> tuple[list[float], list[float]]:
    """Compute per-round non-troll trade count and defection count (excludes all troll trades).

    Returns (trade_counts, defection_counts) as lists of per-round averages.
    """
    if not runs:
        return [], []
    n_rounds = len(runs[0]["rounds"])
    trade_counts = []
    defection_counts = []
    for r in range(n_rounds):
        round_trades = []
        round_defections = []
        for run in runs:
            if r >= len(run["rounds"]):
                continue
            troll_ids = _get_troll_ids(run)
            trades = run["rounds"][r].get("trades", [])
            nt_trades = [t for t in trades
                         if str(t["proposer"]) not in troll_ids
                         and str(t["target"]) not in troll_ids]
            round_trades.append(len(nt_trades))
            round_defections.append(sum(1 for t in nt_trades if t.get("defected_by") is not None))
        trade_counts.append(np.mean(round_trades) if round_trades else 0.0)
        defection_counts.append(np.mean(round_defections) if round_defections else 0.0)
    return trade_counts, defection_counts


def _troll_defection_stats(runs: list[dict]) -> list[float]:
    """Compute per-round count of trades where a troll defected on a non-troll (damaging trades).

    Returns defection_counts as list of per-round averages.
    """
    if not runs:
        return []
    n_rounds = len(runs[0]["rounds"])
    defection_counts = []
    for r in range(n_rounds):
        round_defections = []
        for run in runs:
            if r >= len(run["rounds"]):
                continue
            troll_ids = _get_troll_ids(run)
            if not troll_ids:
                round_defections.append(0)
                continue
            trades = run["rounds"][r].get("trades", [])
            count = sum(1 for t in trades
                        if str(t.get("defected_by")) in troll_ids)
            round_defections.append(count)
        defection_counts.append(np.mean(round_defections) if round_defections else 0.0)
    return defection_counts


# ── Plots ─────────────────────────────────────────────────────────────────────

def _grid_shape(n: int) -> tuple[int, int]:
    """Return (n_rows, n_cols) for a grid that fits n panels, preferring 4 columns."""
    n_cols = min(4, n)
    n_rows = max(1, (n + n_cols - 1) // n_cols)
    return n_rows, n_cols


def plot_metric_trajectories(save: bool = True) -> None:
    """Grid — one panel per condition, showing Gini coefficient over rounds."""
    n_rows, n_cols = _grid_shape(len(CONDITIONS))
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(16, 7), sharex=True, sharey=True)
    axes_flat = axes.flatten()

    for ax, condition in zip(axes_flat, CONDITIONS):
        runs = _load_runs(condition)
        if runs:
            trajectory = _mean_metric_over_rounds(runs, "gini")
            rounds = list(range(1, len(trajectory) + 1))
            ax.plot(rounds, trajectory, label="Gini", color="tab:purple", linewidth=1.8)

            schedule = _get_troll_schedule(runs)
            if schedule:
                _draw_injection_lines(ax, schedule)

        ax.set_title(condition, fontweight="bold")
        ax.set_ylim(0, 1.05)
        ax.grid(True, alpha=0.3)

    for ax in axes_flat[len(CONDITIONS):]:
        ax.set_visible(False)

    for ax in axes[-1]:
        ax.set_xlabel("Round")
    for ax in axes[:, 0]:
        ax.set_ylabel("Gini coefficient")

    fig.suptitle("Inequality (Gini Coefficient) Over Rounds by Condition", fontsize=14, fontweight="bold")
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    _maybe_save(fig, "metric_trajectories.png", save)


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

    if all(m == 0.0 for m in means):
        fig.text(0.5, 0.45, "All values are zero — agents did not produce targeted warnings",
                 ha="center", va="center", fontsize=14, color="gray", fontstyle="italic")
    fig.suptitle("Intermediate Variables by Condition", fontsize=13, fontweight="bold")
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    _maybe_save(fig, "intermediate_variables.png", save)


# ── New plots ─────────────────────────────────────────────────────────────────

def plot_defection_trajectory(save: bool = True) -> None:
    """Grid — one panel per condition showing defection count over rounds."""
    n_rows, n_cols = _grid_shape(len(CONDITIONS))
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(16, 7), sharex=True, sharey=True)
    axes_flat = axes.flatten()

    has_trolls = False
    for ax, condition in zip(axes_flat, CONDITIONS):
        runs = _load_runs(condition)
        if runs:
            _, defections = _non_troll_trade_stats(runs)
            rounds = list(range(1, len(defections) + 1))
            ax.plot(rounds, defections, color=COLORS[condition], linewidth=1.8, label="Self-interested")
            ax.fill_between(rounds, defections, alpha=0.15, color=COLORS[condition])

            troll_defections = _troll_defection_stats(runs)
            if troll_defections and any(d > 0 for d in troll_defections):
                has_trolls = True
                ax.plot(rounds, troll_defections, color="red", linewidth=1.5,
                        linestyle="--", alpha=0.8, label="Troll → victim")

            schedule = _get_troll_schedule(runs)
            if schedule:
                _draw_injection_lines(ax, schedule)
        ax.set_title(condition, fontweight="bold")
        ax.grid(True, alpha=0.3)

    for ax in axes_flat[len(CONDITIONS):]:
        ax.set_visible(False)

    for ax in axes[-1]:
        ax.set_xlabel("Round")
    for ax in axes[:, 0]:
        ax.set_ylabel("Defections per round")

    if has_trolls:
        handles, labels = axes_flat[0].get_legend_handles_labels()
        fig.legend(handles, labels, loc="lower center", ncol=2, fontsize=9, bbox_to_anchor=(0.5, -0.02))

    fig.suptitle("Defection Count Over Rounds by Condition", fontsize=14, fontweight="bold")
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    _maybe_save(fig, "defection_trajectory.png", save)


def plot_trade_volume(save: bool = True) -> None:
    """Grid — one panel per condition showing trade volume over rounds."""
    n_rows, n_cols = _grid_shape(len(CONDITIONS))
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(16, 7), sharex=True, sharey=True)
    axes_flat = axes.flatten()

    for ax, condition in zip(axes_flat, CONDITIONS):
        runs = _load_runs(condition)
        if runs:
            trade_counts, _ = _non_troll_trade_stats(runs)
            rounds = list(range(1, len(trade_counts) + 1))
            ax.plot(rounds, trade_counts, color=COLORS[condition], linewidth=1.8)
            ax.fill_between(rounds, trade_counts, alpha=0.15, color=COLORS[condition])

            schedule = _get_troll_schedule(runs)
            if schedule:
                _draw_injection_lines(ax, schedule)
        ax.set_title(condition, fontweight="bold")
        ax.grid(True, alpha=0.3)

    for ax in axes_flat[len(CONDITIONS):]:
        ax.set_visible(False)

    for ax in axes[-1]:
        ax.set_xlabel("Round")
    for ax in axes[:, 0]:
        ax.set_ylabel("Self-interested agent trades per round")

    fig.suptitle("Self-Interested Agent Trade Volume Over Rounds (Excluding Trolls)", fontsize=14, fontweight="bold")
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
        executed  = _count_field(runs, "contracts_executed_this_round")
        breached  = _count_field(runs, "contracts_breached_this_round")

        ax.plot(rounds, proposed, label="Proposed", linewidth=1.5, linestyle="--")
        ax.plot(rounds, executed, label="Executed", linewidth=1.5, color="tab:green")
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
        trade_counts, _ = _non_troll_trade_stats(runs)
        fractions = []
        for r in range(n_rounds):
            mediated = np.mean([run["rounds"][r].get("mediated_trade_count", 0)
                                for run in runs if r < len(run["rounds"])])
            total = trade_counts[r] if r < len(trade_counts) else 0
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


def plot_stability_rates(save: bool = True) -> None:
    """Bar chart: fraction of rounds (across all runs) where BOTH sustainability AND cooperation rate
    exceed the cooperation threshold, per condition.

    Uses the mean metric value over all rounds — not just the final round — so that cooperation rate
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
                coop = _get_metric(rnd["metrics"], "cooperation_rate")
                if sust > COOPERATION_THRESHOLD and coop > COOPERATION_THRESHOLD:
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


def plot_network_snapshots(save: bool = True, snapshot_rounds: tuple[int, ...] | None = None) -> None:
    """Draw network graph snapshots for conditions with network rewiring."""
    import networkx as nx
    import math
    from matplotlib.lines import Line2D
    from matplotlib.colors import LinearSegmentedColormap

    rep_cmap = LinearSegmentedColormap.from_list("rep", ["#d32f2f", "#ff9800", "#2196f3", "#1565c0"])

    if snapshot_rounds is None:
        snapshot_rounds = (1, 50, 100, 150, 200) if _PROGRESSIVE else (10, 30)

    network_conditions = [c for c in CONDITIONS if "network_rewiring" in CONDITION_MECHANISMS.get(c, [])]
    all_runs: list[tuple[str, int, dict]] = []
    for cond in network_conditions:
        runs = _load_troll_runs(cond) if _PROGRESSIVE else _load_runs(cond)
        for idx, run in enumerate(runs):
            all_runs.append((cond, idx, run))
    if not all_runs:
        print("  [network_snapshots] No network-rewiring condition runs found, skipping.")
        return

    for cond, run_idx, run in all_runs:
        rounds_data = run["rounds"]
        n_rounds = len(rounds_data)

        available = [r for r in snapshot_rounds if r <= n_rounds]
        if not available:
            continue

        fig, axes = plt.subplots(1, len(available), figsize=(10 * len(available), 10))
        if len(available) == 1:
            axes = [axes]

        troll_ids = _get_troll_ids(run)

        for ax, rnd in zip(axes, available):
            rnd_data = rounds_data[rnd - 1]
            net = rnd_data.get("network")
            if net is None:
                ax.set_visible(False)
                continue

            all_ids_this_round = set()
            for aid_str, neighbors in net.items():
                all_ids_this_round.add(int(aid_str))
                for nb in neighbors:
                    all_ids_this_round.add(int(nb) if not isinstance(nb, int) else nb)
            all_ids_this_round = sorted(all_ids_this_round)

            n = len(all_ids_this_round)
            pos = {}
            for i, aid in enumerate(all_ids_this_round):
                angle = 2 * math.pi * i / n - math.pi / 2
                pos[aid] = (math.cos(angle), math.sin(angle))

            G = nx.Graph()
            G.add_nodes_from(all_ids_this_round)
            for aid_str, neighbors in net.items():
                for nb in neighbors:
                    nb_int = int(nb) if not isinstance(nb, int) else nb
                    if int(aid_str) in pos and nb_int in pos:
                        G.add_edge(int(aid_str), nb_int)

            node_list = sorted(G.nodes())
            degrees = {nd: G.degree(nd) for nd in node_list}
            non_troll_nodes = [nd for nd in node_list if str(nd) not in troll_ids]
            troll_nodes = [nd for nd in node_list if str(nd) in troll_ids]

            rep_scores = rnd_data.get("reputation", {})
            rep_vals = {nd: float(rep_scores.get(str(nd), 0.5)) for nd in node_list}

            high_rep = [nd for nd in non_troll_nodes if rep_vals[nd] >= 0.7]
            mid_rep = [nd for nd in non_troll_nodes if 0.4 <= rep_vals[nd] < 0.7]
            low_rep = [nd for nd in non_troll_nodes if rep_vals[nd] < 0.4]
            high_deg = np.mean([degrees[nd] for nd in high_rep]) if high_rep else 0
            mid_deg = np.mean([degrees[nd] for nd in mid_rep]) if mid_rep else 0
            low_deg = np.mean([degrees[nd] for nd in low_rep]) if low_rep else 0
            isolated = [nd for nd in non_troll_nodes if degrees[nd] == 0]
            troll_isolated = [nd for nd in troll_nodes if degrees[nd] == 0]

            for u, v in G.edges():
                is_troll_edge = str(u) in troll_ids or str(v) in troll_ids
                edge_color = "#d32f2f" if is_troll_edge else "#aaaaaa"
                edge_alpha = 0.3 if is_troll_edge else 0.5
                x = [pos[u][0], pos[v][0]]
                y = [pos[u][1], pos[v][1]]
                ax.plot(x, y, color=edge_color, linewidth=0.8, alpha=edge_alpha, zorder=1)

            for nd in non_troll_nodes:
                r = rep_vals[nd]
                x, y = pos[nd]
                radius = 0.05 + r * 0.05
                color = rep_cmap(r)
                circle = plt.Circle((x, y), radius, color=color,
                                    ec="black", lw=1.2, alpha=0.9, zorder=2)
                ax.add_patch(circle)
                ax.text(x, y, str(nd), ha="center", va="center",
                        fontsize=7, fontweight="bold", color="white", zorder=3)

            for nd in troll_nodes:
                x, y = pos[nd]
                radius = 0.07
                triangle = plt.Polygon([
                    (x, y + radius * 1.3),
                    (x - radius, y - radius * 0.7),
                    (x + radius, y - radius * 0.7),
                ], closed=True, facecolor="#d32f2f", edgecolor="black", lw=1.5, alpha=0.9, zorder=2)
                ax.add_patch(triangle)
                ax.text(x, y - 0.005, str(nd), ha="center", va="center",
                        fontsize=6, fontweight="bold", color="white", zorder=3)

            for nd in isolated:
                x, y = pos[nd]
                ring = plt.Circle((x, y), 0.08, fill=False, ec="red",
                                  lw=3.0, zorder=4)
                ax.add_patch(ring)

            events = rnd_data.get("network_events_this_round", [])
            severs = sum(1 for e in events if e["type"] == "sever" and e["outcome"] == "applied")
            requests = sum(1 for e in events if e["type"] == "request" and e["outcome"] == "applied")

            troll_deg = np.mean([degrees[nd] for nd in troll_nodes]) if troll_nodes else 0

            ax.set_xlim(-1.5, 1.5)
            ax.set_ylim(-1.5, 1.5)
            ax.set_aspect("equal")
            title_lines = f"Round {rnd}\n"
            title_lines += f"High rep: {len(high_rep)}, avg {high_deg:.1f} links  |  "
            title_lines += f"Mid rep: {len(mid_rep)}, avg {mid_deg:.1f} links  |  "
            title_lines += f"Low rep: {len(low_rep)}, avg {low_deg:.1f} links\n"
            if troll_nodes:
                title_lines += f"Trolls: {len(troll_nodes)} (avg {troll_deg:.1f} links, {len(troll_isolated)} isolated)  |  "
            title_lines += f"Isolated: {len(isolated)}  |  Severs: {severs}  |  New links: {requests}"
            ax.set_title(title_lines, fontsize=9, fontweight="bold")
            ax.axis("off")

        legend_items = [
            Line2D([0], [0], color="#aaaaaa", lw=1.0, alpha=0.5, label="Trade link"),
            Line2D([0], [0], color="#d32f2f", lw=1.0, alpha=0.3, label="Troll link"),
            Line2D([0], [0], marker="o", color="w", markerfacecolor="#d32f2f",
                   markersize=8, label="Low rep (small, red)"),
            Line2D([0], [0], marker="o", color="w", markerfacecolor="#ff9800",
                   markersize=10, label="Mid rep (orange)"),
            Line2D([0], [0], marker="o", color="w", markerfacecolor="#1565c0",
                   markersize=14, label="High rep (large, blue)"),
            Line2D([0], [0], marker="^", color="w", markerfacecolor="#d32f2f",
                   markersize=10, label="Troll (triangle)"),
        ]
        axes[0].legend(handles=legend_items, loc="upper left", fontsize=9,
                       framealpha=0.9, title="Color & size = reputation")

        fig.suptitle(f"Condition {cond} — Network Topology (Run {run_idx})", fontsize=14, fontweight="bold")
        fig.subplots_adjust(top=0.78, wspace=0.1)
        _maybe_save(fig, f"network_snapshot_{cond}_run{run_idx:02d}.png", save)


def plot_utility_trajectories(save: bool = True) -> None:
    """Grid — one panel per condition, average per-round utility with 3-round rolling average."""
    n_rows, n_cols = _grid_shape(len(CONDITIONS))
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(16, 7), sharex=True, sharey=True)
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
            ax.plot(rounds, smoothed, color=COLORS[condition], linewidth=2.0, label="3-round avg")
            ax.axhline(0, color="black", linestyle="--", linewidth=0.8, alpha=0.6)
            ax.fill_between(rounds, smoothed, 0,
                            where=[v >= 0 for v in smoothed], alpha=0.12, color="green")
            ax.fill_between(rounds, smoothed, 0,
                            where=[v < 0 for v in smoothed], alpha=0.12, color="red")

            total_util = sum(raw)
            ax.text(0.97, 0.97, f"Total: {total_util:.0f}", transform=ax.transAxes,
                    ha="right", va="top", fontsize=9, fontweight="bold",
                    bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.8))

            schedule = _get_troll_schedule(runs)
            if schedule:
                _draw_injection_lines(ax, schedule)

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
    """Load troll run files. Uses _PROGRESSIVE or _N_TROLLS if set, otherwise any troll count."""
    if _PROGRESSIVE:
        files = sorted(config.DATA_DIR.glob(f"{condition}_tprog_run_*.json"))
    elif _N_TROLLS > 0:
        files = sorted(config.DATA_DIR.glob(f"{condition}_t{_N_TROLLS}_run_*.json"))
    else:
        files = sorted(config.DATA_DIR.glob(f"{condition}_t*_run_*.json"))
    runs = []
    for f in files:
        with open(f) as fp:
            runs.append(json.load(fp))
    return runs


def plot_troll_trade_volume(save: bool = True) -> None:
    """Line chart: damaging troll trades per round (non-troll proposed → troll defected)."""
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
                    if str(t["proposer"]) not in troll_ids
                    and str(t["target"]) in troll_ids
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
    ax.set_ylabel("Damaging troll trades per round", fontsize=12)
    ax.set_title("Troll Isolation: Self-Interested Agent Proposals to Trolls Over Rounds", fontweight="bold", fontsize=14)
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)
    ax.axhline(0, color="black", linestyle="--", linewidth=0.8, alpha=0.5)
    plt.tight_layout()
    _maybe_save(fig, "troll_trade_volume.png", save)


def plot_troll_resilience_table(save: bool = True) -> None:
    """Table comparing troll containment across conditions.

    For progressive runs: shows per-phase mean utility (0T, 4T, 8T, 16T) plus
    damaging troll trades and non-troll defection rate.
    """
    PHASES = [(0, 49, "0T"), (50, 99, "4T"), (100, 149, "8T"), (150, 199, "16T")]

    rows = []
    for condition in CONDITIONS:
        runs = _load_troll_runs(condition)
        if not runs:
            continue

        troll_ids = _get_troll_ids(runs[0])
        if not troll_ids and not _PROGRESSIVE:
            continue

        n_rounds = len(runs[0]["rounds"])

        damaging_troll_trades = 0
        non_troll_defections = 0
        non_troll_trades_total = 0

        phase_utilities = {label: [] for _, _, label in PHASES}

        for run in runs:
            t_ids = _get_troll_ids(run)
            for r, rnd in enumerate(run["rounds"]):
                trades = rnd.get("trades", [])
                utilities = rnd.get("utilities", {})

                for t in trades:
                    proposer_is_troll = str(t["proposer"]) in t_ids
                    target_is_troll = str(t["target"]) in t_ids
                    if not proposer_is_troll and target_is_troll:
                        damaging_troll_trades += 1
                    elif not proposer_is_troll and not target_is_troll:
                        non_troll_trades_total += 1
                        if t.get("defected_by") is not None:
                            non_troll_defections += 1

                non_troll_utils = [float(v) for k, v in utilities.items() if k not in t_ids]
                if non_troll_utils:
                    avg_util = np.mean(non_troll_utils)
                    for start, end, label in PHASES:
                        if start <= r <= end:
                            phase_utilities[label].append(avg_util)
                            break

        non_troll_def_rate = non_troll_defections / max(non_troll_trades_total, 1)

        row = {
            "condition": condition,
            "damaging_troll_trades": damaging_troll_trades,
            "non_troll_defection_rate": non_troll_def_rate,
        }
        for _, _, label in PHASES:
            vals = phase_utilities[label]
            row[f"util_{label}"] = round(float(np.mean(vals)), 2) if vals else 0.0
        rows.append(row)

    if not rows:
        print("  [troll_resilience_table] No troll runs found, skipping.")
        return

    fig, ax = plt.subplots(figsize=(16, 2 + 0.5 * len(rows)))
    ax.axis("off")

    col_labels = [
        "Condition",
        "Damaging\nTroll Trades",
        "Non-Troll\nDefect Rate",
        "Mean Util\n0T (1-50)",
        "Mean Util\n4T (51-100)",
        "Mean Util\n8T (101-150)",
        "Mean Util\n16T (151-200)",
    ]
    cell_text = []
    for r in rows:
        cell_text.append([
            r["condition"],
            str(r["damaging_troll_trades"]),
            f"{r['non_troll_defection_rate']:.1%}",
            f"{r['util_0T']:.2f}",
            f"{r['util_4T']:.2f}",
            f"{r['util_8T']:.2f}",
            f"{r['util_16T']:.2f}",
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

    for j in range(len(col_labels)):
        table[0, j].set_facecolor("#4472C4")
        table[0, j].set_text_props(color="white", fontweight="bold")

    for i in range(len(rows)):
        color = "#D9E2F3" if i % 2 == 0 else "white"
        for j in range(len(col_labels)):
            table[i + 1, j].set_facecolor(color)

    ax.set_title("Troll Resilience: Per-Phase Mean Utility Under Progressive Injection (Excluding Trolls)",
                 fontweight="bold", fontsize=13, pad=20)
    plt.tight_layout()
    _maybe_save(fig, "troll_resilience_table.png", save)

    print("\n  Troll Resilience Table (per-phase utility):")
    print(f"  {'Cond':<6} {'DmgTroll':>8} {'DefRate':>8} {'0T':>8} {'4T':>8} {'8T':>8} {'16T':>8}")
    print(f"  {'-'*6} {'-'*8} {'-'*8} {'-'*8} {'-'*8} {'-'*8} {'-'*8}")
    for r in rows:
        print(f"  {r['condition']:<6} {r['damaging_troll_trades']:>8} "
              f"{r['non_troll_defection_rate']:>7.1%} "
              f"{r['util_0T']:>8.2f} "
              f"{r['util_4T']:>8.2f} "
              f"{r['util_8T']:>8.2f} "
              f"{r['util_16T']:>8.2f}")
    print()


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

        gini = final_round.get("metrics", {}).get("gini", 0.0)

        colors_bar = ["#4472C4" if u >= 0 else "#C44444" for u in utils]
        ax.bar(range(len(agent_ids)), utils, color=colors_bar, alpha=0.8)
        ax.axhline(mean_util, color="orange", linestyle="--", linewidth=1.5, alpha=0.8, label=f"Mean: {mean_util:.1f}")
        ax.set_xticks(range(len(agent_ids)))
        ax.set_xticklabels([str(a) for a in agent_ids], fontsize=7, rotation=45)
        ax.set_title(f"{condition}  (Gini: {gini:.3f})", fontweight="bold")
        ax.grid(axis="y", alpha=0.3)
        ax.legend(fontsize=7)

    for ax in axes_flat[len(all_conditions):]:
        ax.set_visible(False)

    for ax in axes[-1]:
        ax.set_xlabel("Agent ID")
    for ax in axes[:, 0]:
        ax.set_ylabel("Utility (final round)")

    fig.suptitle("Per-Agent Utility Distribution at Final Round\n(Self-interested agents only, excluding trolls)",
                 fontsize=13, fontweight="bold")
    plt.tight_layout(rect=[0, 0, 1, 0.93])
    _maybe_save(fig, "utility_per_agent.png", save)


def plot_gini_trajectory(save: bool = True) -> None:
    """Grid — Gini coefficient over rounds per condition."""
    n_rows, n_cols = _grid_shape(len(CONDITIONS))
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


# ── Model-comparison summary table & grouped bars ────────────────────────────

_SUMMARY_METRICS = [
    ("gini", "Gini\n(Inequality)", "lower"),
    ("mean_utility", "Mean\nUtility", "higher"),
]


def _discover_models() -> list[str]:
    base = Path(__file__).parent.parent / "data" / "runs"
    return sorted(d.name for d in base.iterdir()
                  if d.is_dir() and any(d.glob("*_run_*.json")))


def _load_run_from_dir(model_dir: Path, condition: str, n_trolls: int) -> dict | None:
    if n_trolls > 0:
        files = sorted(model_dir.glob(f"{condition}_t{n_trolls}_run_*.json"))
    else:
        files = sorted(model_dir.glob(f"{condition}_run_*.json"))
    if not files:
        return None
    with open(files[0]) as fp:
        return json.load(fp)


def _extract_summary_metrics(run: dict) -> dict[str, float]:
    """Compute mean of each metric across ALL rounds (not just the final round)."""
    troll_ids = set(str(t) for t in run.get("session_log", {}).get("troll_ids", []))
    all_rounds = run.get("rounds", [])
    if not all_rounds:
        return {}

    sust_vals = [r["metrics"]["sustainability"] for r in all_rounds]
    coop_vals = [_get_metric(r["metrics"], "cooperation_rate") for r in all_rounds]
    gini_vals = [r["metrics"]["gini"] for r in all_rounds]
    util_vals = []
    for r in all_rounds:
        non_troll = [float(v) for k, v in r.get("utilities", {}).items() if k not in troll_ids]
        util_vals.append(np.mean(non_troll) if non_troll else 0.0)

    return {
        "sustainability": np.mean(sust_vals),
        "cooperation_rate": np.mean(coop_vals),
        "gini": np.mean(gini_vals),
        "whistleblowing_rate": np.mean([r["metrics"].get("whistleblowing_rate", 0) for r in all_rounds]),
        "false_accusation_rate": np.mean([r["metrics"].get("false_accusation_rate", 0) for r in all_rounds]),
        "warning_accuracy": np.mean([r["metrics"].get("warning_accuracy", 0) for r in all_rounds]),
        "mean_utility": np.mean(util_vals),
    }


def _cell_color(value: float, direction: str, vmin: float, vmax: float):
    if vmax == vmin:
        norm = 0.5
    else:
        norm = (value - vmin) / (vmax - vmin)
    if direction == "lower":
        norm = 1.0 - norm
    green = np.array(mcolors.to_rgba("#2e7d32", alpha=0.35))
    red = np.array(mcolors.to_rgba("#c62828", alpha=0.35))
    white = np.array([1.0, 1.0, 1.0, 0.0])
    if norm >= 0.5:
        t = (norm - 0.5) * 2
        c = white * (1 - t) + green * t
    else:
        t = (0.5 - norm) * 2
        c = white * (1 - t) + red * t
    c[3] = max(c[3], 0.15)
    return tuple(c)


def plot_model_summary_table(save: bool = True) -> None:
    """Table: sustainability, cooperation_rate, gini, normalised utility + composite score per model × condition.

    Mean utility is min-max normalised to [0, 1] across all rows. Composite score =
    mean(sustainability, cooperation_rate, 1-gini, norm_utility). Best mechanism per model is highlighted.
    """
    base = Path(__file__).parent.parent / "data" / "runs"
    models = _discover_models()
    if len(models) < 2:
        print("  [model_summary_table] Need ≥2 models. Skipping.")
        return

    # collect raw metrics: {model: {cond: {metric: val}}}
    raw: dict[str, dict[str, dict[str, float]]] = {}
    for model in models:
        raw[model] = {}
        for cond in CONDITIONS:
            run = _load_run_from_dir(base / model, cond, _N_TROLLS)
            if run is None:
                continue
            raw[model][cond] = _extract_summary_metrics(run)

    # min-max normalise mean_utility across ALL model×condition pairs
    all_utils = [m["mean_utility"] for md in raw.values() for m in md.values()]
    if not all_utils:
        print("  [model_summary_table] No data. Skipping.")
        return
    u_min, u_max = min(all_utils), max(all_utils)

    # build table rows: model, cond, sust, coop, gini, norm_util, composite
    col_labels = ["Sustainability", "Cooperation\nRate", "Gini\n(Inequality)",
                  "Mean Utility\n(normalised)", "Composite\nScore"]
    row_labels = []
    cell_values: list[list[float]] = []
    row_model: list[str] = []

    for model in models:
        for cond in CONDITIONS:
            if cond not in raw[model]:
                continue
            m = raw[model][cond]
            sust = m.get("sustainability", 0)
            coop = m.get("cooperation_rate", 0)
            gini = m.get("gini", 0)
            util_raw = m.get("mean_utility", 0)
            norm_util = (util_raw - u_min) / (u_max - u_min) if u_max != u_min else 0.5
            composite = np.mean([sust, coop, 1.0 - gini, norm_util])

            row_labels.append(f"{model}  |  {cond}")
            cell_values.append([sust, coop, gini, norm_util, composite])
            row_model.append(model)

    n_rows = len(row_labels)
    n_cols = len(col_labels)
    col_directions = ["higher", "higher", "lower", "higher", "higher"]

    # find best composite per model
    best_rows: set[int] = set()
    for model in models:
        model_indices = [i for i, m in enumerate(row_model) if m == model]
        if model_indices:
            best_idx = max(model_indices, key=lambda i: cell_values[i][4])
            best_rows.add(best_idx)

    # colour normalisation per column
    col_mins, col_maxs = [], []
    for j in range(n_cols):
        vals = [cell_values[i][j] for i in range(n_rows)]
        col_mins.append(min(vals) if vals else 0)
        col_maxs.append(max(vals) if vals else 1)

    cell_text, cell_colors = [], []
    for i in range(n_rows):
        tr, cr = [], []
        for j in range(n_cols):
            v = cell_values[i][j]
            tr.append(f"{v:.3f}")
            cr.append(_cell_color(v, col_directions[j], col_mins[j], col_maxs[j]))
        cell_text.append(tr)
        cell_colors.append(cr)

    fig_h = 1.5 + 0.45 * n_rows
    fig, ax = plt.subplots(figsize=(14, fig_h))
    ax.axis("off")

    table = ax.table(cellText=cell_text, rowLabels=row_labels, colLabels=col_labels,
                     loc="center", cellLoc="center")
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1.0, 1.8)

    # header style
    for j in range(n_cols):
        table[0, j].set_facecolor("#37474f")
        table[0, j].set_text_props(color="white", fontweight="bold", fontsize=9)

    for i in range(n_rows):
        table[i + 1, -1].set_text_props(fontweight="bold", fontsize=8)
        for j in range(n_cols):
            table[i + 1, j].set_facecolor(cell_colors[i][j])

    # highlight best mechanism per model with gold border
    for i in best_rows:
        for j in range(-1, n_cols):
            table[i + 1, j].set_edgecolor("#FFD700")
            table[i + 1, j].set_linewidth(3.0)
        table[i + 1, -1].set_text_props(fontweight="bold", fontsize=8, color="#B8860B")

    # bold separator between models
    prev_model = None
    for i, label in enumerate(row_labels):
        model_name = label.split("  |  ")[0]
        if prev_model and model_name != prev_model:
            for j in range(-1, n_cols):
                cell = table[i + 1, j]
                if i not in best_rows:
                    cell.set_edgecolor("black")
                    cell.set_linewidth(2.5)
        prev_model = model_name

    troll_tag = f"{_N_TROLLS}-troll" if _N_TROLLS > 0 else "no-troll"
    ax.set_title(
        f"Mean Metrics Across All Rounds — Model Comparison ({troll_tag})\n"
        "Composite = mean(Sustainability, CoopRate, 1−Gini, NormUtility)  ·  "
        "Gold border = best mechanism per model",
        fontweight="bold", fontsize=12, pad=20)
    plt.tight_layout()
    _maybe_save(fig, "model_summary_table.png", save)


def plot_model_comparison_bars(save: bool = True) -> None:
    """Grouped bar chart: sustainability, cooperation rate, gini, normalised utility, composite per condition."""
    base = Path(__file__).parent.parent / "data" / "runs"
    models = _discover_models()
    if len(models) < 2:
        print("  [model_comparison_bars] Need ≥2 models. Skipping.")
        return

    raw_data: dict[str, dict[str, dict[str, float]]] = {}
    for model in models:
        raw_data[model] = {}
        for cond in CONDITIONS:
            run = _load_run_from_dir(base / model, cond, _N_TROLLS)
            if run is None:
                continue
            raw_data[model][cond] = _extract_summary_metrics(run)

    # min-max normalise utility
    all_utils = [m["mean_utility"] for md in raw_data.values() for m in md.values()]
    if not all_utils:
        return
    u_min, u_max = min(all_utils), max(all_utils)

    bar_metrics = [
        ("sustainability", "Sustainability"),
        ("cooperation_rate", "Cooperation Rate"),
        ("gini", "Gini (Inequality)"),
        ("norm_utility", "Mean Utility (norm)"),
        ("composite", "Composite Score"),
    ]

    # pre-compute normalised values
    data: dict[str, dict[str, dict[str, float]]] = {}
    for model in models:
        data[model] = {}
        for cond in CONDITIONS:
            if cond not in raw_data[model]:
                continue
            m = raw_data[model][cond]
            nu = (m["mean_utility"] - u_min) / (u_max - u_min) if u_max != u_min else 0.5
            data[model][cond] = {
                "sustainability": m.get("sustainability", 0),
                "cooperation_rate": m.get("cooperation_rate", 0),
                "gini": m.get("gini", 0),
                "norm_utility": nu,
                "composite": np.mean([m.get("sustainability", 0), m.get("cooperation_rate", 0),
                                      1.0 - m.get("gini", 0), nu]),
            }

    fig, axes = plt.subplots(2, 3, figsize=(18, 10))
    axes_flat = axes.flatten()

    model_cmap = plt.cm.Set2
    model_colors = {m: model_cmap(i / max(len(models) - 1, 1)) for i, m in enumerate(models)}
    bar_w = 0.8 / max(len(models), 1)

    for idx, (key, label) in enumerate(bar_metrics):
        ax = axes_flat[idx]
        x = np.arange(len(CONDITIONS))
        for mi, model in enumerate(models):
            vals = [data.get(model, {}).get(c, {}).get(key, 0) for c in CONDITIONS]
            offset = (mi - len(models) / 2 + 0.5) * bar_w
            bars = ax.bar(x + offset, vals, bar_w * 0.9,
                          label=model, color=model_colors[model], alpha=0.85)
            for bar, v in zip(bars, vals):
                if v != 0:
                    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height(),
                            f"{v:.2f}", ha="center", va="bottom", fontsize=6, rotation=45)
        ax.set_xticks(x)
        ax.set_xticklabels(CONDITIONS, fontsize=9)
        ax.set_title(label, fontweight="bold", fontsize=10)
        ax.grid(axis="y", alpha=0.3)
        if idx == 0:
            ax.legend(fontsize=7, loc="lower left")

    for ax in axes_flat[len(bar_metrics):]:
        ax.set_visible(False)

    troll_tag = f"{_N_TROLLS}-troll" if _N_TROLLS > 0 else "no-troll"
    fig.suptitle(f"Mean Metrics Across All Rounds by Condition & Model ({troll_tag})\n"
                 "Composite = mean(Sustainability, CoopRate, 1−Gini, NormUtility)",
                 fontsize=14, fontweight="bold")
    plt.tight_layout(rect=[0, 0, 1, 0.93])
    _maybe_save(fig, "model_comparison_bars.png", save)


def plot_composite_ranking(save: bool = True) -> None:
    """Heatmap: normalized 4-metric composite score per condition.

    Metrics: mean utility, cooperation rate, equality (1-gini),
    production stability (sustainability). Each is min-max normalized to [0,1]
    across conditions. Shows per-metric normalized scores plus average and min
    (Rawlsian) composite.
    """
    rows = []
    for condition in CONDITIONS:
        runs = _load_runs(condition)
        if not runs:
            continue
        run = runs[0]
        troll_ids = set(str(t) for t in run.get("session_log", {}).get("troll_ids", []))
        all_rounds = run["rounds"]

        gini_vals = [r["metrics"]["gini"] for r in all_rounds]
        util_vals = []
        for r in all_rounds:
            non_troll = [float(v) for k, v in r["utilities"].items() if k not in troll_ids]
            util_vals.append(np.mean(non_troll) if non_troll else 0.0)

        rows.append({
            "condition": condition,
            "utility": np.mean(util_vals),
            "equality": 1.0 - np.mean(gini_vals),
        })

    if not rows:
        print("  [composite_ranking] No data found, skipping.")
        return

    metrics = ["utility", "equality"]
    display_names = ["Mean Utility\n(normalized)", "Equality\n(1−Gini)"]

    raw = {m: np.array([r[m] for r in rows]) for m in metrics}

    normed = {}
    for m in metrics:
        mn, mx = raw[m].min(), raw[m].max()
        if mx - mn < 1e-9:
            normed[m] = np.full_like(raw[m], 0.5)
        else:
            normed[m] = (raw[m] - mn) / (mx - mn)

    n_cond = len(rows)
    avg_scores = np.mean([normed[m] for m in metrics], axis=0)
    min_scores = np.min([normed[m] for m in metrics], axis=0)

    col_labels = display_names + ["Average\n(Composite)", "Min\n(Rawlsian)"]
    data = np.column_stack([normed[m] for m in metrics] + [avg_scores, min_scores])
    row_labels = [r["condition"] for r in rows]

    sort_idx = np.argsort(-avg_scores)
    data = data[sort_idx]
    row_labels = [row_labels[i] for i in sort_idx]

    fig, ax = plt.subplots(figsize=(12, max(4, n_cond * 0.7 + 1)))
    green = np.array(mcolors.to_rgba("#2e7d32", alpha=0.5))
    pale = np.array([1.0, 1.0, 1.0, 0.0])

    cell_text = []
    cell_colors = []
    for i in range(n_cond):
        tr, cr = [], []
        for j in range(data.shape[1]):
            v = data[i, j]
            t = v
            color = tuple(pale * (1 - t) + green * t)
            tr.append(f"{v:.2f}")
            cr.append(color)
        cell_text.append(tr)
        cell_colors.append(cr)

    ax.axis("off")
    table = ax.table(
        cellText=cell_text,
        rowLabels=row_labels,
        colLabels=col_labels,
        cellColours=cell_colors,
        loc="center",
        cellLoc="center",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(11)
    table.scale(1.0, 1.8)

    for (r, c), cell in table.get_celld().items():
        if r == 0:
            cell.set_text_props(fontweight="bold", fontsize=10)
            cell.set_facecolor("#4a7c59")
            cell.set_text_props(color="white", fontweight="bold", fontsize=10)
        if c == -1:
            cell.set_text_props(fontweight="bold", fontsize=11)

    troll_tag = f"{_N_TROLLS} trolls" if _N_TROLLS > 0 else "no trolls"
    ax.set_title(
        f"Composite Mechanism Ranking ({troll_tag})\n"
        "Utility normalized to [0,1]; other metrics are raw [0,1]; sorted by average composite",
        fontsize=13, fontweight="bold", pad=20,
    )
    plt.tight_layout()
    _maybe_save(fig, "composite_ranking.png", save)


def plot_troll_escalation(save: bool = True, troll_counts: tuple[int, ...] = (0, 4, 8, 16)) -> None:
    """Line charts: how each mechanism degrades under escalating troll counts.

    One panel per metric (utility, cooperation rate, sustainability, gini).
    X-axis = troll count, one line per condition. Shows each mechanism's breaking point.
    Averages across all runs per troll count.
    """
    metrics_to_plot = [
        ("mean_utility", "Mean Utility (per round)", "higher"),
        ("gini", "Gini (Inequality)", "lower"),
    ]

    # Collect data: {condition: {troll_count: {metric: value}}}
    data: dict[str, dict[int, dict[str, float]]] = {}
    for cond in CONDITIONS:
        data[cond] = {}
        for tc in troll_counts:
            if tc > 0:
                files = sorted(config.DATA_DIR.glob(f"{cond}_t{tc}_run_*.json"))
            else:
                files = sorted(config.DATA_DIR.glob(f"{cond}_run_*.json"))
            if not files:
                continue
            runs = []
            for f in files:
                with open(f) as fp:
                    runs.append(json.load(fp))
            # Average metrics across all runs
            summaries = [_extract_summary_metrics(run) for run in runs]
            avg = {}
            for key in summaries[0]:
                avg[key] = np.mean([s[key] for s in summaries])
            data[cond][tc] = avg

    # Only plot conditions that have data for at least 2 troll counts
    active_conds = [c for c in CONDITIONS if len(data.get(c, {})) >= 2]
    if not active_conds:
        print("  [troll_escalation] Need data for ≥2 troll counts per condition. Skipping.")
        return

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    for ax, (metric_key, metric_label, direction) in zip(axes, metrics_to_plot):
        for cond in active_conds:
            tcs = sorted(data[cond].keys())
            vals = [data[cond][tc].get(metric_key, 0) for tc in tcs]
            ax.plot(tcs, vals, marker="o", label=cond, color=COLORS.get(cond, "gray"),
                    linewidth=2.0, markersize=6)

        ax.set_xlabel("Number of trolls", fontsize=11)
        ax.set_ylabel(metric_label, fontsize=11)
        ax.set_title(metric_label, fontweight="bold", fontsize=12)
        ax.set_xticks(list(troll_counts))
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=8, loc="best")

    fig.suptitle("Mechanism Resilience Under Escalating Adversarial Pressure\n"
                 "(3 runs × 100 rounds per condition per troll count, averaged)",
                 fontsize=14, fontweight="bold")
    plt.tight_layout(rect=[0, 0, 1, 0.93])
    _maybe_save(fig, "troll_escalation.png", save)


def plot_troll_escalation_table(save: bool = True, troll_counts: tuple[int, ...] = (0, 4, 8, 16)) -> None:
    """Summary table: mean utility per condition × troll phase.

    In progressive mode, splits each run into phases (1-50, 51-100, 101-150, 151-200)
    and computes mean non-troll utility per phase.  Falls back to separate-file mode
    when _PROGRESSIVE is False.
    """
    # Phase boundaries for progressive mode: (start, end, total_trolls)
    PHASES = [(1, 50, 0), (51, 100, 4), (101, 150, 8), (151, 200, 16)]

    data: dict[str, dict[int, float]] = {}

    if _PROGRESSIVE:
        for cond in CONDITIONS:
            runs = _load_runs(cond)
            if not runs:
                continue
            data[cond] = {}
            for phase_start, phase_end, tc in PHASES:
                phase_utils = []
                for run in runs:
                    troll_ids = set(str(t) for t in run.get("session_log", {}).get("troll_ids", []))
                    rounds = run.get("rounds", [])
                    for r in rounds:
                        rn = r.get("round", 0)
                        if rn < phase_start or rn > phase_end:
                            continue
                        non_troll = [float(v) for k, v in r.get("utilities", {}).items() if k not in troll_ids]
                        if non_troll:
                            phase_utils.append(np.mean(non_troll))
                if phase_utils:
                    data[cond][tc] = np.mean(phase_utils)
    else:
        for cond in CONDITIONS:
            data[cond] = {}
            for tc in troll_counts:
                if tc > 0:
                    files = sorted(config.DATA_DIR.glob(f"{cond}_t{tc}_run_*.json"))
                else:
                    files = sorted(config.DATA_DIR.glob(f"{cond}_run_*.json"))
                if not files:
                    continue
                runs = []
                for f in files:
                    with open(f) as fp:
                        runs.append(json.load(fp))
                summaries = [_extract_summary_metrics(run) for run in runs]
                data[cond][tc] = np.mean([s["mean_utility"] for s in summaries])

    active_conds = [c for c in CONDITIONS if data.get(c, {})]
    if not active_conds:
        print("  [troll_escalation_table] No data found. Skipping.")
        return

    if _PROGRESSIVE:
        col_labels = [f"Phase {i+1}\n({p[2]} trolls)" for i, p in enumerate(PHASES)] + ["Δ (0→16)"]
    else:
        col_labels = [f"{tc} trolls" for tc in troll_counts] + ["Δ (0→max)"]
    cell_text = []
    all_vals = [v for cd in data.values() for v in cd.values()]
    v_min, v_max = (min(all_vals), max(all_vals)) if all_vals else (0, 1)

    for cond in active_conds:
        row = []
        for tc in troll_counts:
            val = data[cond].get(tc)
            row.append(f"{val:.2f}" if val is not None else "—")
        v0 = data[cond].get(troll_counts[0])
        vmax = data[cond].get(troll_counts[-1])
        if v0 is not None and vmax is not None:
            delta = vmax - v0
            row.append(f"{delta:+.2f}")
        else:
            row.append("—")
        cell_text.append(row)

    fig, ax = plt.subplots(figsize=(12, 2 + 0.5 * len(active_conds)))
    ax.axis("off")

    table = ax.table(
        cellText=cell_text,
        rowLabels=active_conds,
        colLabels=col_labels,
        loc="center",
        cellLoc="center",
    )
    table.auto_set_font_size(False)
    table.set_fontsize(10)
    table.scale(1.0, 1.8)

    for j in range(len(col_labels)):
        table[0, j].set_facecolor("#37474f")
        table[0, j].set_text_props(color="white", fontweight="bold")

    for i, cond in enumerate(active_conds):
        for j, tc in enumerate(troll_counts):
            val = data[cond].get(tc)
            if val is not None:
                table[i + 1, j].set_facecolor(_cell_color(val, "higher", v_min, v_max))
        v0 = data[cond].get(troll_counts[0])
        vmax_val = data[cond].get(troll_counts[-1])
        if v0 is not None and vmax_val is not None:
            delta = vmax_val - v0
            color = "#c8e6c9" if delta >= 0 else "#ffcdd2"
            table[i + 1, len(troll_counts)].set_facecolor(color)

    title = ("Mean Utility by Condition × Progressive Phase\n"
             "(Green = higher utility, Red = lower; Δ = change from Phase 1 to Phase 4)"
             if _PROGRESSIVE else
             "Mean Utility by Condition × Troll Count\n"
             "(Green = higher utility, Red = lower; Δ = change from 0 to max trolls)")
    ax.set_title(title, fontweight="bold", fontsize=12, pad=20)
    plt.tight_layout()
    _maybe_save(fig, "troll_escalation_table.png", save)


def plot_all(save: bool = True, n_trolls: int = 0, progressive: bool = False) -> None:
    global OUT_DIR, _N_TROLLS, _PROGRESSIVE
    _N_TROLLS = n_trolls
    _PROGRESSIVE = progressive
    OUT_DIR = _get_out_dir(n_trolls, progressive=progressive)
    plot_metric_trajectories(save)
    plot_defection_trajectory(save)
    plot_trade_volume(save)
    plot_contract_utilisation(save)
    plot_mediation_utilisation(save)
    plot_reputation_trajectories(save)
    plot_utility_trajectories(save)
    plot_network_snapshots(save)
    plot_troll_trade_volume(save)
    plot_troll_resilience_table(save)
    plot_utility_per_agent(save)
    plot_composite_ranking(save)
    plot_troll_escalation(save)
    plot_troll_escalation_table(save)
    print(f"Plots saved to {OUT_DIR}")


def _maybe_save(fig: plt.Figure, filename: str, save: bool) -> None:
    if save:
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        fig.savefig(OUT_DIR / filename, dpi=150, bbox_inches="tight")
        plt.close(fig)
    else:
        plt.show()
