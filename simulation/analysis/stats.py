"""Statistical significance tests across simulation conditions.

Usage:
    python -m simulation.analysis.stats
"""
from __future__ import annotations
import json
from pathlib import Path
from itertools import combinations

import numpy as np
from scipy.stats import mannwhitneyu

from .. import config

METRICS = ["sustainability", "peace", "mean_utility"]


def _discover_runs() -> dict[str, list[dict]]:
    """Auto-discover all condition run logs in DATA_DIR."""
    data: dict[str, list[dict]] = {}
    for f in sorted(config.DATA_DIR.glob("*_run_*.json")):
        if "_traces" in f.name:
            continue
        with open(f) as fp:
            run = json.load(fp)
        cond = run["condition"]
        data.setdefault(cond, []).append(run)
    return data


def _extract_metrics(runs: list[dict]) -> dict[str, list[float]]:
    """Extract per-run final-round metrics."""
    out: dict[str, list[float]] = {m: [] for m in METRICS}
    for run in runs:
        final = run["rounds"][-1]
        out["sustainability"].append(final["metrics"]["sustainability"])
        out["peace"].append(final["metrics"]["peace"])
        utilities = [float(v) for v in final["utilities"].values()]
        out["mean_utility"].append(float(np.mean(utilities)))
    return out


def _effect_size(u: float, n1: int, n2: int) -> float:
    """Rank-biserial correlation: r = 1 - 2U/(n1*n2)."""
    denom = n1 * n2
    if denom == 0:
        return 0.0
    return 1.0 - (2.0 * u) / denom


def _sig_marker(p: float) -> str:
    if p < 0.01:
        return "**"
    if p < 0.05:
        return "*"
    if p < 0.10:
        return "+"
    return ""


def run_stats() -> str:
    all_runs = _discover_runs()
    if not all_runs:
        return "No run logs found in " + str(config.DATA_DIR)

    lines: list[str] = []
    lines.append("=" * 70)
    lines.append("STATISTICAL ANALYSIS — Mann-Whitney U Tests")
    lines.append("=" * 70)

    # --- Descriptive stats ---
    condition_metrics: dict[str, dict[str, list[float]]] = {}
    for cond, runs in sorted(all_runs.items()):
        metrics = _extract_metrics(runs)
        condition_metrics[cond] = metrics

        lines.append(f"\n--- Condition {cond} (n={len(runs)} runs) ---")
        for m in METRICS:
            vals = metrics[m]
            lines.append(
                f"  {m:20s}  mean={np.mean(vals):.4f}  std={np.std(vals):.4f}  "
                f"min={np.min(vals):.4f}  max={np.max(vals):.4f}"
            )

    # --- Sample size warning ---
    small = [c for c, r in all_runs.items() if len(r) < 5]
    if small:
        lines.append(f"\n  WARNING: conditions {small} have < 5 runs.")
        lines.append("  Mann-Whitney U has low power at small n. Interpret with caution.")

    # --- Pairwise tests ---
    conds = sorted(condition_metrics.keys())
    if len(conds) < 2:
        lines.append("\nOnly one condition found — no pairwise tests possible.")
        return "\n".join(lines)

    lines.append("\n" + "=" * 70)
    lines.append("PAIRWISE COMPARISONS")
    lines.append("=" * 70)
    lines.append("Significance: ** p<0.01  * p<0.05  + p<0.10")

    for metric in METRICS:
        lines.append(f"\n--- {metric} ---")
        lines.append(f"  {'Comparison':>12s}   {'U':>8s}   {'p-value':>10s}   {'effect r':>9s}   sig")
        lines.append("  " + "-" * 55)

        for c1, c2 in combinations(conds, 2):
            v1 = condition_metrics[c1][metric]
            v2 = condition_metrics[c2][metric]
            n1, n2 = len(v1), len(v2)

            try:
                u_stat, p_val = mannwhitneyu(v1, v2, alternative="two-sided")
                r = _effect_size(u_stat, n1, n2)
                sig = _sig_marker(p_val)
                lines.append(
                    f"  {c1:>5s} vs {c2:<5s}   {u_stat:8.1f}   {p_val:10.4f}   {r:9.3f}   {sig}"
                )
            except ValueError as e:
                lines.append(f"  {c1:>5s} vs {c2:<5s}   — test failed: {e}")

    # --- Summary table ---
    lines.append("\n" + "=" * 70)
    lines.append("CONDITION RANKING (by final-round mean utility)")
    lines.append("=" * 70)
    ranked = sorted(
        condition_metrics.items(),
        key=lambda x: np.mean(x[1]["mean_utility"]),
        reverse=True,
    )
    for i, (cond, metrics) in enumerate(ranked, 1):
        u = np.mean(metrics["mean_utility"])
        s = np.mean(metrics["sustainability"])
        p = np.mean(metrics["peace"])
        n = len(all_runs[cond])
        lines.append(f"  {i}. {cond:>5s}  utility={u:+.3f}  sustainability={s:.3f}  peace={p:.3f}  (n={n})")

    return "\n".join(lines)


if __name__ == "__main__":
    print(run_stats())
