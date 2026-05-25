"""Orchestrates multiple runs per condition and saves JSON logs."""
from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime
from tqdm import tqdm

from .agent import make_agents
from .game import Game
from ..config import CONDITIONS, CONDITION_MECHANISMS, RUNS_PER_CONDITION, DATA_DIR


def _make_mechanisms(mechanism_names: list[str]):
    from ..mechanisms.reputation import ReputationMechanism
    from ..mechanisms.contracting import ContractingMechanism
    from ..mechanisms.mediation import MediationMechanism
    from ..mechanisms.governance import GovernanceMechanism
    from ..mechanisms.network_rewiring import NetworkRewiringMechanism

    lookup = {
        "reputation": ReputationMechanism,
        "contracting": ContractingMechanism,
        "mediation": MediationMechanism,
        "governance": GovernanceMechanism,
        "network_rewiring": NetworkRewiringMechanism,
    }
    return [lookup[name]() for name in mechanism_names]


def run_condition(condition: str, runs: int = RUNS_PER_CONDITION) -> list[dict]:
    """Run all repetitions for one condition. Returns list of run summaries."""
    mechanism_names = CONDITION_MECHANISMS[condition]
    summaries = []

    for run_idx in tqdm(range(runs), desc=f"Condition {condition}", unit="run", leave=True):
        agents = make_agents()
        mechanisms = _make_mechanisms(mechanism_names)
        game = Game(
            agents=agents,
            mechanisms=mechanisms,
            condition_label=condition,
            run_idx=run_idx,
        )
        round_logs = game.run()

        summary = {
            "condition": condition,
            "run": run_idx,
            "timestamp": datetime.utcnow().isoformat(),
            "session_log": game.session_log,
            "rounds": round_logs,
            "final_metrics": round_logs[-1]["metrics"] if round_logs else {},
            "agent_types": {
                a.agent_id: type(a).__name__ for a in agents
            },
        }
        summaries.append(summary)
        _save_run(condition, run_idx, summary)
        _save_traces(condition, run_idx, game.trace_log)

    return summaries


def run_all(conditions: list[str] = CONDITIONS, runs: int | None = None) -> dict[str, list[dict]]:
    """Run all conditions sequentially."""
    results = {}
    kwargs = {"runs": runs} if runs is not None else {}
    for condition in conditions:
        results[condition] = run_condition(condition, **kwargs)
    return results


def _save_run(condition: str, run_idx: int, data: dict) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    filename = DATA_DIR / f"{condition}_run_{run_idx:02d}.json"
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)
    print(f"  Saved → {filename}")


def _save_traces(condition: str, run_idx: int, traces: list[dict]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    filename = DATA_DIR / f"{condition}_run_{run_idx:02d}_traces.jsonl"
    with open(filename, "w") as f:
        for entry in traces:
            f.write(json.dumps(entry) + "\n")
    print(f"  Saved traces → {filename} ({len(traces)} entries)")
