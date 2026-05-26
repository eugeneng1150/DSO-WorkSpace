# DSO-WorkSpace

> **Work in progress** — this is an ongoing research project. Results, conditions, and implementation details are actively evolving.

Multi-agent marketplace simulation for studying how institutional mechanisms enable cooperation among self-interested LLM agents.

## Research Question

Which formal mechanism (or combination) allows self-interested LLM agents to maintain marketplace cooperation in a repeated trading environment — and how resilient are those mechanisms to adversarial actors?

## Setup

18 LLM agents trade 3 perishable goods (A, B, C) over 30 rounds. Each agent specialises in producing one good and needs the other two. Agents barter goods directly — no currency. All agents use chain-of-thought reasoning.

| Parameter | Value |
|---|---|
| Agents | 18 (6 per good) |
| Rounds | 30 |
| Goods | A, B, C (perishable, 20% spoilage/round) |
| Production cost | 1 utility per unit |
| Consumption gain | +3 utility per needed unit consumed |
| Agent model | gpt-5.4-mini (Azure) or oss-120b (local Docker) |
| Analyst model | claude-opus-4-6 |

## Conditions

| Code | Mechanism | Type |
|---|---|---|
| B | Baseline — no mechanism | — |
| R | Reputation — public system-tracked scores | Agent-visible |
| C | Contracting — binding bilateral contracts with breach penalties | Agent-participatory |
| M | Mediation — agent-designed mediator, voted and elected before round 1 | Agent-designed |
| G | Governance — external Oracle + escalating fines/suspension | Top-down |
| N | Network Rewiring — agents sever/request trade links each round | Structural |
| NR | Network Rewiring + Reputation | Combined |
| S | Sanctions — agents spend utility to anonymously punish others (1:3 ratio) | Bottom-up |

## Metrics

**Primary (marketplace cooperation = both > 0.5 at final round):**
- `sustainability` — avg production this round / avg production round 1
- `peace` — fraction of attempted trades completing without defection (cumulative)

**Intermediate:**
- `whistleblowing_rate` — warnings broadcast / defections suffered
- `false_accusation_rate` — unverified negative mentions / total negative mentions
- `warning_accuracy` — accurate warnings / total warnings

## Usage

```bash
# Run a single condition (3 runs)
python3 -m simulation.main --condition B --runs 3

# Run all 8 conditions
python3 -m simulation.main --all --runs 3

# Run with local oss-120b model (Docker must be running)
python3 -m simulation.main --condition B --runs 3 --model oss-120b

# Generate plots from existing logs
python3 -m simulation.main --plot

# Run LLM analyst report
python3 -m simulation.main --analyse

# Run reasoning analyst on CoT traces
python3 -m simulation.main --reason-analyse --condition B --run-idx 0

# Full pipeline
python3 -m simulation.main --all --runs 3 --plot --analyse
```

Logs are saved to `simulation/data/runs/<model>/` — one folder per model backend.

## Project Structure

```
simulation/
├── main.py                  # CLI entry point
├── config.py                # All parameters and condition definitions
├── engine/
│   ├── agent.py             # IOAgent, CoTAgent, LLM client
│   ├── game.py              # Round loop, phase orchestration
│   ├── market.py            # Market state, trade history, ledgers
│   ├── prompt_builder.py    # Assembles per-agent prompts each round
│   └── runner.py            # Runs N repetitions, saves JSON logs
├── mechanisms/
│   ├── reputation.py        # R — public reputation scores
│   ├── contracting.py       # C — propose/sign/enforce contracts
│   ├── mediation.py         # M — design/vote/delegate mediator
│   ├── governance.py        # G — Oracle + state machine
│   ├── network_rewiring.py  # N — sever/request trade links
│   └── sanction.py          # S — costly anonymous punishment
├── metrics/
│   └── social.py            # sustainability, peace, intermediate vars
├── analysis/
│   ├── analyst.py           # LLM analyst report from run logs
│   ├── reasoning_analyst.py # CoT trace analysis + lead-lag signals
│   ├── plots.py             # All matplotlib visualisations
│   └── stats.py             # Summary statistics
└── data/
    ├── runs/                # JSON logs per condition/run/model
    └── plots/               # Generated figures

prompts/                     # Prompt templates (base + per-mechanism)
wiki/                        # Research knowledge base
idea.md                      # Exploratory ideas and pending decisions
```

## Two-Phase Research Design

**Phase 1 (current):** Which mechanisms achieve cooperation among self-interested agents? Run all 8 conditions, compare Peace/Sustainability/utility trajectories.

**Phase 2 (planned):** Take the top mechanisms from Phase 1 and stress-test with escalating numbers of hardcoded troll agents (0, 2, 4, 6 out of 18). Find each mechanism's breaking point — when does per-round societal utility drop below 0?

## Environment

Requires `AZURE_OPENAI_API_KEY` in `.env` for the default gpt-5.4-mini model. For oss-120b, start Docker model runner (`docker model serve`) — no API key needed.
