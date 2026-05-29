"""Animated network graph using Plotly — RepuNet-style troll isolation visualization.

Inspired by Figure 3 of "Reputation as a Solution to Cooperation Collapse in LLM-based MASs".
- Force-directed layout (computed once, stable across frames)
- Node color = reputation score (blue = low → red = high); trolls always dark red with diamond marker
- Node size = degree (number of active trade connections)
- Edge thickness to trolls = trade volume (thick = active trading, fading = boycott)
- Play button + slider to scrub through rounds
- Outputs one HTML file per condition
"""
from __future__ import annotations
import json
import math
from pathlib import Path
from collections import defaultdict

import numpy as np
import plotly.graph_objects as go

from .. import config
from ..config import CONDITIONS

OUT_DIR = Path(__file__).parent.parent / "data" / "plots"


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


def _force_directed_layout(
    agent_ids: list[int],
    network: dict[int, list[int]],
    troll_ids: set[int],
    iterations: int = 200,
    k: float = 1.0,
) -> dict[int, tuple[float, float]]:
    """Spring-electric force-directed layout. Trolls start at periphery."""
    n = len(agent_ids)
    id_to_idx = {aid: i for i, aid in enumerate(agent_ids)}

    # Initialize: normals in a circle, trolls slightly outside
    pos = np.zeros((n, 2))
    normal_ids = [a for a in agent_ids if a not in troll_ids]
    troll_list = [a for a in agent_ids if a in troll_ids]

    for i, aid in enumerate(normal_ids):
        angle = 2 * math.pi * i / len(normal_ids) - math.pi / 2
        pos[id_to_idx[aid]] = [math.cos(angle) * 0.8, math.sin(angle) * 0.8]

    for i, aid in enumerate(troll_list):
        angle = 2 * math.pi * i / max(len(troll_list), 1)
        pos[id_to_idx[aid]] = [math.cos(angle) * 1.3, math.sin(angle) * 1.3]

    optimal_dist = k * math.sqrt(4.0 / max(n, 1))

    for iteration in range(iterations):
        temp = 0.5 * (1 - iteration / iterations)
        disp = np.zeros((n, 2))

        # Repulsive forces (all pairs)
        for i in range(n):
            for j in range(i + 1, n):
                delta = pos[i] - pos[j]
                dist = max(np.linalg.norm(delta), 0.01)
                force = optimal_dist ** 2 / dist
                direction = delta / dist
                disp[i] += direction * force
                disp[j] -= direction * force

        # Attractive forces (edges)
        for aid, neighbors in network.items():
            if aid not in id_to_idx:
                continue
            i = id_to_idx[aid]
            for nb in neighbors:
                if nb not in id_to_idx:
                    continue
                j = id_to_idx[nb]
                if i >= j:
                    continue
                delta = pos[i] - pos[j]
                dist = max(np.linalg.norm(delta), 0.01)
                force = dist ** 2 / optimal_dist
                direction = delta / dist
                disp[i] -= direction * force
                disp[j] += direction * force

        # Apply displacement with temperature
        for i in range(n):
            mag = max(np.linalg.norm(disp[i]), 0.01)
            pos[i] += (disp[i] / mag) * min(mag, temp)

    # Center and normalize
    pos -= pos.mean(axis=0)
    max_extent = np.abs(pos).max()
    if max_extent > 0:
        pos /= max_extent

    return {aid: (float(pos[id_to_idx[aid]][0]), float(pos[id_to_idx[aid]][1]))
            for aid in agent_ids}


def _get_network(run: dict, round_idx: int) -> dict[int, list[int]]:
    rnd = run["rounds"][round_idx]
    net = rnd.get("network")
    if net is not None:
        return {int(k): v for k, v in net.items()}
    return {int(k): v for k, v in run["session_log"]["network"].items()}


def _count_troll_trades(run: dict, round_idx: int, troll_ids: set[int],
                        window: int = 3) -> dict[tuple[int, int], int]:
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


def _count_all_trades(run: dict, round_idx: int, troll_ids: set[int],
                      window: int = 3) -> dict[tuple[int, int], int]:
    """Count trades between all non-troll pairs over a rolling window."""
    counts: dict[tuple[int, int], int] = defaultdict(int)
    start = max(0, round_idx - window + 1)
    for r in range(start, round_idx + 1):
        for trade in run["rounds"][r].get("trades", []):
            p, t = trade["proposer"], trade["target"]
            if p in troll_ids or t in troll_ids:
                continue
            key = (min(p, t), max(p, t))
            counts[key] += 1
    return dict(counts)


def _reputation_to_color(rep: float) -> str:
    """Map reputation [0, 1] to a blue→yellow→red color string."""
    # Blue (low) → Orange (mid) → Red (high cooperation)
    if rep < 0.5:
        # Blue to orange
        t = rep / 0.5
        r = int(30 + t * 225)
        g = int(100 + t * 50)
        b = int(200 * (1 - t))
    else:
        # Orange to red
        t = (rep - 0.5) / 0.5
        r = int(220 + t * 35)
        g = int(150 * (1 - t) + 50 * (1 - t))
        b = int(20 * (1 - t))
    return f"rgb({min(r,255)},{max(g,0)},{max(b,0)})"


def build_network_animation(condition: str, troll_suffix: str = "_t2") -> go.Figure | None:
    run = _load_run(condition, troll_suffix)
    if run is None:
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
    n_rounds = len(run["rounds"])

    # Compute force-directed layout from initial network (stable positions)
    initial_net = {int(k): v for k, v in run["session_log"]["network"].items()}
    pos = _force_directed_layout(agent_ids, initial_net, troll_ids)

    # Pre-compute max troll trade count for consistent scaling
    max_trade_count = 1
    for r in range(n_rounds):
        counts = _count_troll_trades(run, r, troll_ids)
        if counts:
            max_trade_count = max(max_trade_count, max(counts.values()))

    # Build all frames
    frames = []
    for r in range(n_rounds):
        net = _get_network(run, r)
        troll_trades = _count_troll_trades(run, r, troll_ids)
        normal_trades = _count_all_trades(run, r, troll_ids)

        # Get reputation scores for this round
        rep_scores = run["rounds"][r].get("reputation", {})

        traces = []

        # --- Normal-to-normal edges (thin, grey) ---
        edge_x, edge_y = [], []
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
                edge_x.extend([x0, x1, None])
                edge_y.extend([y0, y1, None])

        traces.append(go.Scatter(
            x=edge_x, y=edge_y, mode="lines",
            line=dict(width=0.4, color="rgba(180,180,180,0.25)"),
            hoverinfo="none", showlegend=False,
        ))

        # --- Troll edges (thickness + opacity = trade volume) ---
        seen_troll = set()
        for aid in agent_ids:
            if aid in troll_ids:
                continue
            for troll in troll_ids:
                edge_key = (min(aid, troll), max(aid, troll))
                if edge_key in seen_troll:
                    continue
                seen_troll.add(edge_key)

                # Only draw if they're neighbors
                if troll not in net.get(aid, []):
                    continue

                count = troll_trades.get((aid, troll), 0)
                frac = count / max_trade_count if max_trade_count > 0 else 0

                width = 0.5 + frac * 10
                alpha = 0.08 + frac * 0.85

                x0, y0 = pos[aid]
                x1, y1 = pos[troll]
                traces.append(go.Scatter(
                    x=[x0, x1, None], y=[y0, y1, None],
                    mode="lines",
                    line=dict(width=width, color=f"rgba(214,39,40,{alpha:.2f})"),
                    hoverinfo="text",
                    hovertext=f"Agent {aid} <-> Troll {troll}: {count} trades",
                    showlegend=False,
                ))

        # --- Normal agent nodes ---
        normal_list = [a for a in agent_ids if a not in troll_ids]
        normal_x = [pos[a][0] for a in normal_list]
        normal_y = [pos[a][1] for a in normal_list]

        # Degree = number of active neighbors (from current network)
        degrees = [len(net.get(a, [])) for a in normal_list]
        max_deg = max(degrees) if degrees else 1
        node_sizes = [12 + (d / max(max_deg, 1)) * 22 for d in degrees]

        # Reputation → color
        node_colors = []
        hover_texts = []
        for a in normal_list:
            rep = float(rep_scores.get(str(a), 1.0))
            node_colors.append(_reputation_to_color(rep))
            hover_texts.append(
                f"Agent {a} (Good {specialties[a]})<br>"
                f"Reputation: {rep:.2f}<br>"
                f"Connections: {len(net.get(a, []))}"
            )

        traces.append(go.Scatter(
            x=normal_x, y=normal_y, mode="markers+text",
            marker=dict(
                size=node_sizes,
                color=node_colors,
                line=dict(width=1.5, color="white"),
            ),
            text=[str(a) for a in normal_list],
            textposition="middle center",
            textfont=dict(size=7, color="white", family="Arial Black"),
            hovertext=hover_texts,
            hoverinfo="text",
            showlegend=False,
        ))

        # --- Troll nodes (always dark red, diamond) ---
        troll_list = sorted(troll_ids)
        troll_x = [pos[a][0] for a in troll_list]
        troll_y = [pos[a][1] for a in troll_list]
        troll_degrees = [len(net.get(a, [])) for a in troll_list]
        troll_sizes = [18 + (d / max(max_deg, 1)) * 18 for d in troll_degrees]

        troll_trade_total = sum(
            troll_trades.get((normal, troll), 0)
            for normal in normal_list for troll in troll_list
        )

        troll_hover = [
            f"TROLL Agent {a} (Good {specialties[a]})<br>"
            f"Connections: {len(net.get(a, []))}<br>"
            f"Trades this window: {sum(troll_trades.get((n, a), 0) for n in normal_list)}"
            for a in troll_list
        ]

        traces.append(go.Scatter(
            x=troll_x, y=troll_y, mode="markers+text",
            marker=dict(
                size=troll_sizes,
                color="rgb(180,20,20)",
                symbol="diamond",
                line=dict(width=2.5, color="black"),
            ),
            text=[f"T{a}" for a in troll_list],
            textposition="middle center",
            textfont=dict(size=7, color="white", family="Arial Black"),
            hovertext=troll_hover,
            hoverinfo="text",
            showlegend=False,
        ))

        frames.append(go.Frame(
            data=traces,
            name=str(r + 1),
            layout=go.Layout(
                annotations=[dict(
                    x=0.5, y=1.05, xref="paper", yref="paper",
                    text=(f"<b>Round {r+1}</b> | "
                          f"Trades with trolls (3-round window): <b>{troll_trade_total}</b>"),
                    showarrow=False, font=dict(size=14),
                )]
            ),
        ))

    # --- Build figure ---
    fig = go.Figure(data=frames[0].data, frames=frames)

    # Slider + play/pause
    sliders = [dict(
        active=0,
        yanchor="top", xanchor="left",
        currentvalue=dict(prefix="Round: ", font=dict(size=14)),
        pad=dict(b=10, t=60),
        len=0.9, x=0.05, y=0,
        steps=[
            dict(
                args=[[str(r + 1)],
                      dict(frame=dict(duration=300, redraw=True), mode="immediate")],
                method="animate", label=str(r + 1),
            )
            for r in range(n_rounds)
        ],
    )]

    fig.update_layout(
        title=dict(
            text=(
                f"<b>Condition {condition} — Troll Isolation Over Time</b><br>"
                f"<sub>Node color = reputation (blue=low, red=high) | "
                f"Node size = connections | "
                f"Red edge thickness = trade volume with trolls<br>"
                f"Trolls (diamonds): {sorted(troll_ids)}</sub>"
            ),
            font=dict(size=16),
        ),
        showlegend=False,
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False,
                   range=[-1.3, 1.3]),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False,
                   range=[-1.3, 1.3], scaleanchor="x", scaleratio=1),
        plot_bgcolor="rgb(250,250,252)",
        width=900, height=900,
        sliders=sliders,
        updatemenus=[dict(
            type="buttons", showactive=False,
            y=0, x=0.0, xanchor="left", yanchor="top",
            pad=dict(t=70, r=10),
            buttons=[
                dict(label="Play",
                     method="animate",
                     args=[None, dict(
                         frame=dict(duration=500, redraw=True),
                         fromcurrent=True,
                         transition=dict(duration=200),
                     )]),
                dict(label="Pause",
                     method="animate",
                     args=[[None], dict(
                         frame=dict(duration=0, redraw=True),
                         mode="immediate",
                         transition=dict(duration=0),
                     )]),
            ],
        )],
    )

    return fig


def plot_interactive_networks(conditions: list[str] | None = None,
                               troll_suffix: str = "_t2",
                               save: bool = True) -> None:
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
