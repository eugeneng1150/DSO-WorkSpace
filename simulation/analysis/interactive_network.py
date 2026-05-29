"""Animated network graph using Plotly — shows troll isolation over rounds.

Edge thickness to troll agents = trade volume (thick = many trades, invisible = boycott).
Play button + slider to scrub through rounds. Outputs one HTML file per condition.
"""
from __future__ import annotations
import json
import math
from pathlib import Path
from collections import defaultdict

import plotly.graph_objects as go

from .. import config
from ..config import CONDITIONS, CONDITION_MECHANISMS

OUT_DIR = Path(__file__).parent.parent / "data" / "plots"

GOOD_COLORS = {"A": "#1f77b4", "B": "#2ca02c", "C": "#ff7f0e"}
TROLL_COLOR = "#d62728"
EDGE_NORMAL_COLOR = "rgba(180,180,180,0.3)"
EDGE_TROLL_COLOR = "rgba(214,39,40,{alpha})"


def _load_run(condition: str, troll_suffix: str = "") -> dict | None:
    pattern = f"{condition}{troll_suffix}_run_00.json"
    f = config.DATA_DIR / pattern
    if f.exists():
        with open(f) as fp:
            return json.load(fp)
    files = sorted(config.DATA_DIR.glob(f"{condition}{troll_suffix}_run_*.json"))
    if files:
        with open(files[0]) as fp:
            return json.load(fp)
    return None


def _circular_layout(agent_ids: list[int]) -> dict[int, tuple[float, float]]:
    n = len(agent_ids)
    pos = {}
    for i, aid in enumerate(sorted(agent_ids)):
        angle = 2 * math.pi * i / n - math.pi / 2
        pos[aid] = (math.cos(angle), math.sin(angle))
    return pos


def _get_network(run: dict, round_idx: int) -> dict[int, list[int]]:
    """Get network at a given round. Falls back to session_log for non-NR conditions."""
    rnd = run["rounds"][round_idx]
    net = rnd.get("network")
    if net is not None:
        return {int(k): v for k, v in net.items()}
    return {int(k): v for k, v in run["session_log"]["network"].items()}


def _count_troll_trades(run: dict, round_idx: int, troll_ids: set[int], window: int = 3) -> dict[tuple[int, int], int]:
    """Count trades involving each (normal, troll) pair over a rolling window."""
    counts: dict[tuple[int, int], int] = defaultdict(int)
    start = max(0, round_idx - window + 1)
    for r in range(start, round_idx + 1):
        for trade in run["rounds"][r].get("trades", []):
            p, t = trade["proposer"], trade["target"]
            if p in troll_ids and t not in troll_ids:
                counts[(t, p)] += 1
            elif t in troll_ids and p not in troll_ids:
                counts[(p, t)] += 1
    return dict(counts)


def build_network_animation(condition: str, troll_suffix: str = "_t2") -> go.Figure | None:
    """Build an animated Plotly network graph for a single condition+run."""
    run = _load_run(condition, troll_suffix)
    if run is None:
        # try without suffix
        run = _load_run(condition)
    if run is None:
        print(f"  [interactive_network] No run data for {condition}{troll_suffix}, skipping.")
        return None

    troll_ids = set(run.get("session_log", {}).get("troll_ids", []))
    if not troll_ids:
        print(f"  [interactive_network] No trolls in {condition}, skipping.")
        return None

    specialties = {int(k): v for k, v in run["session_log"]["specialties"].items()}
    agent_ids = sorted(specialties.keys())
    pos = _circular_layout(agent_ids)
    n_rounds = len(run["rounds"])

    # Pre-compute max troll trade count for consistent scaling
    max_trade_count = 1
    for r in range(n_rounds):
        counts = _count_troll_trades(run, r, troll_ids)
        if counts:
            max_trade_count = max(max_trade_count, max(counts.values()))

    frames = []
    for r in range(n_rounds):
        net = _get_network(run, r)
        troll_trades = _count_troll_trades(run, r, troll_ids)

        edge_traces = []

        # Normal-to-normal edges
        seen = set()
        for aid, neighbors in net.items():
            if aid in troll_ids:
                continue
            for nb in neighbors:
                if nb in troll_ids:
                    continue
                edge_key = (min(aid, nb), max(aid, nb))
                if edge_key in seen:
                    continue
                seen.add(edge_key)
                x0, y0 = pos[aid]
                x1, y1 = pos[nb]
                edge_traces.append(go.Scatter(
                    x=[x0, x1, None], y=[y0, y1, None],
                    mode="lines",
                    line=dict(width=0.5, color=EDGE_NORMAL_COLOR),
                    hoverinfo="none",
                    showlegend=False,
                ))

        # Troll edges (thickness = trade volume)
        seen_troll = set()
        for aid, neighbors in net.items():
            for nb in neighbors:
                if aid not in troll_ids and nb not in troll_ids:
                    continue
                normal = aid if aid not in troll_ids else nb
                troll = nb if nb not in troll_ids else aid
                if normal in troll_ids:
                    continue
                edge_key = (min(normal, troll), max(normal, troll))
                if edge_key in seen_troll:
                    continue
                seen_troll.add(edge_key)

                count = troll_trades.get((normal, troll), 0)
                width = max(0.3, (count / max_trade_count) * 8)
                alpha = max(0.05, min(0.9, count / max_trade_count))

                x0, y0 = pos[normal]
                x1, y1 = pos[troll]
                edge_traces.append(go.Scatter(
                    x=[x0, x1, None], y=[y0, y1, None],
                    mode="lines",
                    line=dict(width=width, color=EDGE_TROLL_COLOR.format(alpha=alpha)),
                    hoverinfo="text",
                    text=f"Agent {normal} ↔ Troll {troll}: {count} trades (last 3 rounds)",
                    showlegend=False,
                ))

        # Normal nodes
        normal_x = [pos[a][0] for a in agent_ids if a not in troll_ids]
        normal_y = [pos[a][1] for a in agent_ids if a not in troll_ids]
        normal_colors = [GOOD_COLORS.get(specialties[a], "#999") for a in agent_ids if a not in troll_ids]
        normal_text = [f"Agent {a} (Good {specialties[a]})" for a in agent_ids if a not in troll_ids]

        node_normal = go.Scatter(
            x=normal_x, y=normal_y, mode="markers+text",
            marker=dict(size=18, color=normal_colors, line=dict(width=1.5, color="white")),
            text=[str(a) for a in agent_ids if a not in troll_ids],
            textposition="middle center",
            textfont=dict(size=8, color="white"),
            hovertext=normal_text,
            hoverinfo="text",
            showlegend=False,
        )

        # Troll nodes
        troll_list = sorted(troll_ids)
        troll_x = [pos[a][0] for a in troll_list]
        troll_y = [pos[a][1] for a in troll_list]
        troll_text_hover = [f"TROLL Agent {a} (Good {specialties[a]})" for a in troll_list]

        node_troll = go.Scatter(
            x=troll_x, y=troll_y, mode="markers+text",
            marker=dict(size=24, color=TROLL_COLOR, symbol="diamond",
                        line=dict(width=2, color="black")),
            text=[str(a) for a in troll_list],
            textposition="middle center",
            textfont=dict(size=8, color="white"),
            hovertext=troll_text_hover,
            hoverinfo="text",
            showlegend=False,
        )

        # Total trades with trolls this round for annotation
        total_troll_trades = sum(troll_trades.values())

        frame_data = edge_traces + [node_normal, node_troll]
        frames.append(go.Frame(
            data=frame_data,
            name=str(r + 1),
            layout=go.Layout(
                annotations=[dict(
                    x=0.5, y=1.08, xref="paper", yref="paper",
                    text=f"Round {r+1} — Trades with trolls (3-round window): {total_troll_trades}",
                    showarrow=False, font=dict(size=14),
                )]
            ),
        ))

    # Initial frame
    fig = go.Figure(data=frames[0].data, frames=frames)

    # Slider + play button
    sliders = [dict(
        active=0,
        yanchor="top", xanchor="left",
        currentvalue=dict(prefix="Round: ", font=dict(size=14)),
        pad=dict(b=10, t=50),
        len=0.9, x=0.05, y=0,
        steps=[dict(args=[[str(r + 1)], dict(frame=dict(duration=300, redraw=True), mode="immediate")],
                    method="animate", label=str(r + 1))
               for r in range(n_rounds)],
    )]

    fig.update_layout(
        title=dict(
            text=f"Condition {condition} — Troll Isolation Over Time<br>"
                 f"<sub>Edge thickness to trolls = trade volume (3-round window). "
                 f"Trolls: {sorted(troll_ids)}</sub>",
            font=dict(size=16),
        ),
        showlegend=False,
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-1.4, 1.4]),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-1.4, 1.4],
                   scaleanchor="x", scaleratio=1),
        plot_bgcolor="white",
        width=800, height=800,
        sliders=sliders,
        updatemenus=[dict(
            type="buttons",
            showactive=False,
            y=0,
            x=0.0,
            xanchor="left",
            yanchor="top",
            pad=dict(t=60, r=10),
            buttons=[
                dict(label="▶ Play", method="animate",
                     args=[None, dict(frame=dict(duration=400, redraw=True),
                                      fromcurrent=True, transition=dict(duration=200))]),
                dict(label="⏸ Pause", method="animate",
                     args=[[None], dict(frame=dict(duration=0, redraw=True),
                                        mode="immediate", transition=dict(duration=0))]),
            ],
        )],
    )

    return fig


def plot_interactive_networks(conditions: list[str] | None = None,
                               troll_suffix: str = "_t2",
                               save: bool = True) -> None:
    """Generate animated network HTML for specified conditions (or all with troll data)."""
    if conditions is None:
        conditions = CONDITIONS

    OUT_DIR.mkdir(parents=True, exist_ok=True)

    for cond in conditions:
        fig = build_network_animation(cond, troll_suffix)
        if fig is None:
            continue
        if save:
            out_path = OUT_DIR / f"network_animation_{cond}{troll_suffix}.html"
            fig.write_html(str(out_path), auto_open=False)
            print(f"  Saved: {out_path}")
        else:
            fig.show()
