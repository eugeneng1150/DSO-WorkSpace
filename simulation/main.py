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
    parser.add_argument("--interactive", action="store_true",
                        help="Generate interactive Plotly network animations (requires troll runs)")
    parser.add_argument("--analyse", action="store_true", help="Run analyst agent after simulation")
    parser.add_argument("--trolls", type=int, default=0,
                        help="Number of troll agents — deterministic defectors (default 0)")
    parser.add_argument("--progressive-trolls", action="store_true",
                        help="Progressive injection: 0→4→8→16 trolls at rounds 1/51/101/151 (200 rounds)")
    parser.add_argument("--smart-trolls", action="store_true",
                        help="Use LLM-driven adversarial agents instead of deterministic trolls (requires --progressive-trolls)")
    parser.add_argument("--revote-interval", type=int, default=0,
                        help="Re-vote on mediator design every N rounds (0 = only at injection rounds)")
    parser.add_argument("--adv-version", type=str, default="",
                        help="Adversarial prompt version tag (e.g. v1, v2). Tags output files and loads prompts/adversarial_vN.txt")
    parser.add_argument("--plot-adversarial", action="store_true",
                        help="Generate adversarial comparison plots (dumb trolls vs all adversarial versions)")
    parser.add_argument("--rounds", type=int, default=None,
                        help="Override number of rounds (default 30)")
    parser.add_argument("--model", type=str, default=None,
                        choices=["gpt-5.4-mini", "gpt-5.4-nano", "oss-120b", "oss-20b", "deepseek-v3"],
                        help="Agent LLM backend: gpt-5.4-mini (Azure, default), gpt-5.4-nano (Azure), oss-120b (local Docker), oss-20b (local Docker), or deepseek-v3 (Azure)")
    args = parser.parse_args()

    model_tag = args.model or "gpt-5.4-mini"
    from .config import set_model_tag
    set_model_tag(model_tag)

    if args.model == "oss-120b":
        from .config import DOCKER_ENDPOINT, DOCKER_MODEL, DOCKER_API_KEY
        from .engine.agent import configure_llm
        configure_llm(base_url=DOCKER_ENDPOINT, api_key=DOCKER_API_KEY, model=DOCKER_MODEL)
        print(f"Using local Docker model: {DOCKER_MODEL}")
    elif args.model == "oss-20b":
        from .config import OSS20B_ENDPOINT, OSS20B_MODEL, OSS20B_API_KEY
        from .engine.agent import configure_llm
        configure_llm(base_url=OSS20B_ENDPOINT, api_key=OSS20B_API_KEY, model=OSS20B_MODEL)
        print(f"Using local Docker model: {OSS20B_MODEL}")
    elif args.model == "gpt-5.4-nano":
        if not os.environ.get("AZURE_OPENAI_API_KEY"):
            print("ERROR: AZURE_OPENAI_API_KEY not set. Add it to .env or export it.")
            return
        from .config import AZURE_ENDPOINT, NANO_MODEL
        from .engine.agent import configure_llm
        configure_llm(base_url=AZURE_ENDPOINT, api_key=os.environ.get("AZURE_OPENAI_API_KEY"), model=NANO_MODEL)
        print(f"Using GPT-5.4-nano: {NANO_MODEL}")
    elif args.model == "deepseek-v3":
        if not os.environ.get("AZURE_OPENAI_API_KEY"):
            print("ERROR: AZURE_OPENAI_API_KEY not set. Add it to .env or export it.")
            return
        from .config import DEEPSEEK_ENDPOINT, DEEPSEEK_MODEL
        from .engine.agent import configure_llm
        configure_llm(base_url=DEEPSEEK_ENDPOINT, api_key=os.environ.get("AZURE_OPENAI_API_KEY"), model=DEEPSEEK_MODEL)
        print(f"Using DeepSeek: {DEEPSEEK_MODEL}")
    else:
        if not os.environ.get("AZURE_OPENAI_API_KEY"):
            print("ERROR: AZURE_OPENAI_API_KEY not set. Add it to .env or export it.")
            return

    from . import config as _cfg
    print(f"Data directory: {_cfg.DATA_DIR}")

    troll_schedule = None
    if args.progressive_trolls:
        troll_schedule = [(51, 4), (101, 4), (151, 8)]
        if not args.rounds:
            args.rounds = 200
        smart_label = " (SMART — LLM-driven adversarial)" if args.smart_trolls else ""
        print(f"Progressive troll injection{smart_label}: 0→4→8→16 at rounds 1/51/101/151 ({args.rounds} rounds)")
    elif args.trolls:
        print(f"Troll agents: {args.trolls}")
    if args.rounds:
        print(f"Rounds: {args.rounds}")

    if args.smart_trolls and not args.progressive_trolls:
        print("ERROR: --smart-trolls requires --progressive-trolls")
        return

    if args.adv_version:
        from .engine.prompt_builder import set_adversarial_version
        set_adversarial_version(args.adv_version)
        print(f"Adversarial prompt: adversarial_{args.adv_version}.txt")

    run_kwargs: dict = {}
    if args.runs:
        run_kwargs["runs"] = args.runs
    if args.trolls and not args.progressive_trolls:
        run_kwargs["n_trolls"] = args.trolls
    if args.rounds:
        run_kwargs["total_rounds"] = args.rounds
    if troll_schedule:
        run_kwargs["troll_schedule"] = troll_schedule
    if args.smart_trolls:
        run_kwargs["smart_trolls"] = True
    if args.revote_interval:
        run_kwargs["revote_interval"] = args.revote_interval
    if args.adv_version:
        run_kwargs["adv_version"] = args.adv_version

    if args.condition:
        run_condition(args.condition, **run_kwargs)

    elif args.all:
        run_all(**run_kwargs)

    if args.plot_adversarial:
        from .analysis.adversarial_plots import plot_adversarial_comparison
        plot_adversarial_comparison()

    if args.plot:
        from .analysis.plots import plot_all
        plot_all(n_trolls=args.trolls, progressive=args.progressive_trolls)

    if args.interactive:
        from .analysis.interactive_network import plot_interactive_networks
        troll_suffix = f"_t{args.trolls}" if args.trolls else "_t2"
        cond_list = [args.condition] if args.condition else None
        plot_interactive_networks(conditions=cond_list, troll_suffix=troll_suffix)

    if args.analyse:
        from .analysis.analyst import run_analyst
        filter_models = [args.model] if args.model else None
        report = run_analyst(filter_models=filter_models, progressive_only=args.progressive_trolls)
        print("\n" + "=" * 60)
        print(report)



if __name__ == "__main__":
    main()
