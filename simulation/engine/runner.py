"""Orchestrates multiple runs per condition and saves JSON logs."""
from __future__ import annotations
import json
from pathlib import Path
from datetime import datetime
from tqdm import tqdm

from .agent import make_agents
from .game import Game
from .. import config
from ..config import CONDITIONS, CONDITION_MECHANISMS, RUNS_PER_CONDITION


def _make_mechanisms(mechanism_names: list[str]):
    from ..mechanisms.reputation import ReputationMechanism
    from ..mechanisms.contracting import ContractingMechanism
    from ..mechanisms.mediation import MediationMechanism
    from ..mechanisms.governance import GovernanceMechanism
    from ..mechanisms.network_rewiring import NetworkRewiringMechanism
    from ..mechanisms.sanction import SanctionMechanism
    from ..mechanisms.local_reputation import LocalReputationMechanism
    from ..mechanisms.judicial import JudicialMechanism
    from ..mechanisms.escrow import EscrowMechanism

    lookup = {
        "reputation": ReputationMechanism,
        "contracting": ContractingMechanism,
        "mediation": MediationMechanism,
        "governance": GovernanceMechanism,
        "network_rewiring": NetworkRewiringMechanism,
        "sanction": SanctionMechanism,
        "local_reputation": LocalReputationMechanism,
        "judicial": JudicialMechanism,
        "escrow": EscrowMechanism,
    }
    return [lookup[name]() for name in mechanism_names]


def run_condition(
    condition: str,
    runs: int = RUNS_PER_CONDITION,
    n_trolls: int = 0,
    total_rounds: int | None = None,
    troll_schedule: list[tuple[int, int]] | None = None,
    smart_trolls: bool = False,
    revote_interval: int = 0,
    adv_version: str = "",
) -> list[dict]:
    """Run all repetitions for one condition. Returns list of run summaries."""
    from ..config import ROUNDS
    effective_rounds = total_rounds if total_rounds is not None else ROUNDS

    mechanism_names = CONDITION_MECHANISMS[condition]
    summaries = []

    for run_idx in tqdm(range(runs), desc=f"Condition {condition}", unit="run", leave=True):
        agents = make_agents(n_trolls=n_trolls)
        mechanisms = _make_mechanisms(mechanism_names)
        game = Game(
            agents=agents,
            mechanisms=mechanisms,
            condition_label=condition,
            run_idx=run_idx,
            total_rounds=effective_rounds,
            troll_schedule=troll_schedule,
            smart_trolls=smart_trolls,
            revote_interval=revote_interval,
        )
        round_logs = game.run()

        summary = {
            "condition": condition,
            "run": run_idx,
            "n_trolls": n_trolls,
            "troll_schedule": troll_schedule,
            "smart_trolls": smart_trolls,
            "adv_version": adv_version,
            "total_rounds": effective_rounds,
            "timestamp": datetime.utcnow().isoformat(),
            "session_log": game.session_log,
            "rounds": round_logs,
            "final_metrics": round_logs[-1]["metrics"] if round_logs else {},
            "agent_types": {
                a.agent_id: type(a).__name__ for a in game.agents
            },
        }
        summaries.append(summary)
        _save_run(condition, run_idx, summary, n_trolls=n_trolls,
                  troll_schedule=troll_schedule, smart_trolls=smart_trolls,
                  adv_version=adv_version)
        _save_traces(condition, run_idx, game.trace_log, n_trolls=n_trolls,
                     troll_schedule=troll_schedule, smart_trolls=smart_trolls,
                     adv_version=adv_version)

    return summaries


def run_all(
    conditions: list[str] = CONDITIONS,
    runs: int | None = None,
    n_trolls: int = 0,
    total_rounds: int | None = None,
    troll_schedule: list[tuple[int, int]] | None = None,
    smart_trolls: bool = False,
    revote_interval: int = 0,
    adv_version: str = "",
) -> dict[str, list[dict]]:
    """Run all conditions sequentially."""
    results = {}
    kwargs: dict = {}
    if runs is not None:
        kwargs["runs"] = runs
    if n_trolls:
        kwargs["n_trolls"] = n_trolls
    if total_rounds is not None:
        kwargs["total_rounds"] = total_rounds
    if troll_schedule is not None:
        kwargs["troll_schedule"] = troll_schedule
    if smart_trolls:
        kwargs["smart_trolls"] = smart_trolls
    if revote_interval:
        kwargs["revote_interval"] = revote_interval
    if adv_version:
        kwargs["adv_version"] = adv_version
    for condition in conditions:
        results[condition] = run_condition(condition, **kwargs)
    return results


def _make_tag(n_trolls: int = 0, troll_schedule: list | None = None,
              smart_trolls: bool = False, adv_version: str = "") -> str:
    if troll_schedule and smart_trolls and adv_version:
        return f"_tprog_adv_{adv_version}"
    elif troll_schedule and smart_trolls:
        return "_tprog_smart"
    elif troll_schedule:
        return "_tprog"
    elif n_trolls > 0:
        return f"_t{n_trolls}"
    return ""


def _save_run(condition: str, run_idx: int, data: dict, n_trolls: int = 0,
              troll_schedule: list | None = None, smart_trolls: bool = False,
              adv_version: str = "") -> None:
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)
    tag = _make_tag(n_trolls, troll_schedule, smart_trolls, adv_version)
    filename = config.DATA_DIR / f"{condition}{tag}_run_{run_idx:02d}.json"
    with open(filename, "w") as f:
        json.dump(data, f, indent=2)
    print(f"  Saved → {filename}")


def _save_traces(condition: str, run_idx: int, traces: list[dict], n_trolls: int = 0,
                 troll_schedule: list | None = None, smart_trolls: bool = False,
                 adv_version: str = "") -> None:
    config.DATA_DIR.mkdir(parents=True, exist_ok=True)
    tag = _make_tag(n_trolls, troll_schedule, smart_trolls, adv_version)
    filename = config.DATA_DIR / f"{condition}{tag}_run_{run_idx:02d}_traces.jsonl"
    with open(filename, "w") as f:
        for entry in traces:
            f.write(json.dumps(entry) + "\n")
    print(f"  Saved traces → {filename} ({len(traces)} entries)")
