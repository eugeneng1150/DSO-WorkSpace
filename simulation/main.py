"""Entry point for the marketplace simulation.

Usage:
    python -m simulation.main --condition B          # run one condition
    python -m simulation.main --all                  # run all 8 conditions
    python -m simulation.main --analyse              # run analyst agent on existing logs
    python -m simulation.main --plot                 # generate plots from existing logs
    python -m simulation.main --all --plot --analyse # full pipeline
"""
import argparse
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path=os.path.join(os.path.dirname(__file__), "..", ".env"))

from .engine.runner import run_condition, run_all
from .config import CONDITIONS


def main():
    parser = argparse.ArgumentParser(description="Marketplace simulation runner")
    parser.add_argument("--condition", type=str, choices=CONDITIONS, help="Run a single condition")
    parser.add_argument("--all", action="store_true", help="Run all conditions")
    parser.add_argument("--runs", type=int, default=None, help="Override number of runs per condition")
    parser.add_argument("--plot", action="store_true", help="Generate plots after simulation")
    parser.add_argument("--analyse", action="store_true", help="Run analyst agent after simulation")
    parser.add_argument("--reason-analyse", action="store_true", help="Run reasoning analyst on CoT traces")
    parser.add_argument("--extract-signals", action="store_true", help="Extract social signals from agent messages/CoT")
    parser.add_argument("--all-runs", action="store_true", help="Process all runs (not just run 0)")
    parser.add_argument("--run-idx", type=int, default=0, help="Run index to analyse (default 0)")
    parser.add_argument("--model", type=str, default=None,
                        choices=["gpt-5.4-mini", "oss-120b"],
                        help="Agent LLM backend: gpt-5.4-mini (Azure, default) or oss-120b (local Docker)")
    args = parser.parse_args()

    model_tag = args.model or "gpt-5.4-mini"
    from .config import set_model_tag
    set_model_tag(model_tag)

    if args.model == "oss-120b":
        from .config import DOCKER_ENDPOINT, DOCKER_MODEL, DOCKER_API_KEY
        from .engine.agent import configure_llm
        configure_llm(base_url=DOCKER_ENDPOINT, api_key=DOCKER_API_KEY, model=DOCKER_MODEL)
        print(f"Using local Docker model: {DOCKER_MODEL}")
    else:
        if not os.environ.get("AZURE_OPENAI_API_KEY"):
            print("ERROR: AZURE_OPENAI_API_KEY not set. Add it to .env or export it.")
            return

    from . import config as _cfg
    print(f"Data directory: {_cfg.DATA_DIR}")

    if args.condition:
        kwargs = {"runs": args.runs} if args.runs else {}
        run_condition(args.condition, **kwargs)

    elif args.all:
        run_all(runs=args.runs if args.runs else None)

    if args.plot:
        from .analysis.plots import plot_all
        plot_all()

    if args.analyse:
        from .analysis.analyst import run_analyst
        report = run_analyst()
        print("\n" + "=" * 60)
        print(report)

    if args.extract_signals:
        from .analysis.reasoning_analyst import extract_all_signals
        cond = args.condition if args.condition else None
        extract_all_signals(condition=cond, all_runs=args.all_runs)

    if args.reason_analyse:
        from .analysis.reasoning_analyst import run_reasoning_analyst
        cond = args.condition if args.condition else None
        report = run_reasoning_analyst(condition=cond, run_idx=args.run_idx)
        print("\n" + "=" * 60)
        print(report)


if __name__ == "__main__":
    main()
