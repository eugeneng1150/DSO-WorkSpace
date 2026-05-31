# DSO-WorkSpace

> **Work in progress** — this is an ongoing research project. Results, conditions, and implementation details are actively evolving.

Multi-agent marketplace simulation for studying how institutional mechanisms enable cooperation among self-interested LLM agents.

## Research Question

Which formal mechanism (or combination) allows self-interested LLM agents to maintain marketplace cooperation in a repeated trading environment — and how resilient are those mechanisms to adversarial actors?

## Setup

18 LLM agents trade 3 perishable goods (A, B, C) in a barter economy. Each agent specialises in producing one good and needs the other two. All agents use chain-of-thought reasoning with 5-step reasoning (situation, self-reflection, gossip evaluation, assessment, strategy).

Agents do NOT know when the game ends — they see only the current round number. They do NOT see aggregate market health metrics. Trust must be formed through direct experience, gossip, and mechanism-specific information.

| Parameter | Value |
|---|---|
| Agents | 18 (6 per good) + trolls added on top |
| Rounds | 30 (Phase 1) or 100 (Phase 2) |
| Goods | A, B, C (perishable, 20% spoilage/round) |
| Production cost | 1 utility per unit |
| Consumption gain | +3 utility per needed unit consumed |
| Agent models | GPT-5.4-mini (Azure), DeepSeek-V3.2 (Azure) |
| Analyst model | Claude Opus 4.6 |

## Conditions

| Code | Mechanism | Description |
|---|---|---|
| B | Baseline | No mechanism. Fixed network. Trades unenforceable. |
| GR | Global Reputation | System-computed reputation score (success/total) visible to all. Fixed network. |
| C | Contracting | Binding bilateral contracts with breach penalties (6 utility). Fixed network. |
| M | Mediation | Agent-designed mediator, voted pre-game. Free delegation guarantees fair execution. Fixed network. |
| G | Governance | External oracle detects defection (D1: rate >40%, D4: predatory targeting). Escalates: Warning → Fined → Suspended. Fixed network. |
| NR | Network Rewiring + Local Reputation | Dynamic network (sever/request links) + 10-round rolling gossip history. No system scores. |
| S | Sanctions | Costly punishment: spend 1 utility → target loses 3. Anonymous, publicly announced. Fixed network. |

### Information Gradient: B → NR → GR

| | B | NR | GR |
|---|---|---|---|
| Lifetime partner summary | Yes | Yes | Yes |
| Current round public messages | Yes | Yes | Yes |
| Historical gossip (last 10 rounds) | No | Yes | No |
| Network reshaping | No | Yes (sever/request) | No |
| System reputation scores | No | No | Yes |

## Troll Agents (Phase 2)

Deterministic adversarial agents added on top of the 18 LLM agents (e.g., 2 trolls = 20 total agents). Trolls:
- Propose trades to ALL neighbors every round, then defect on everything
- Broadcast lies ("I'm committed to fair trading!")
- Do not produce, connected to all agents initially
- Excluded from all metrics

## Metrics

**Primary (marketplace cooperation = both > 0.5):**
- `sustainability` — Production Stability: avg production / round-1 baseline
- `peace` — Cooperation Rate: fraction of non-troll trades without defection
- `gini` — Gini coefficient: utility inequality among non-troll agents (0 = equal, 1 = max inequality)

**Intermediate:**
- `whistleblowing_rate` — targeted warnings / defections suffered (requires naming a specific agent)
- `false_accusation_rate` — false negative mentions / total negative mentions
- `warning_accuracy` — accurate warnings / total warnings

## Usage

```bash
# Run a single condition (3 runs, 30 rounds)
python3 -m simulation.main --condition B --runs 3

# Run all 7 conditions
python3 -m simulation.main --all --runs 3

# Phase 2: trolls + longer games
python3 -m simulation.main --condition NR --trolls 2 --rounds 100 --runs 1

# Switch model
python3 -m simulation.main --condition B --runs 1 --model deepseek-v3

# Generate plots from existing logs
python3 -m simulation.main --plot

# Recompute warning metrics on existing logs (after detection tightening)
python3 -m simulation.scripts.recompute_warnings --model gpt-5.4-mini

# Run LLM analyst report
python3 -m simulation.main --analyse
```

Logs are saved to `simulation/data/runs/<model>/` — one folder per model backend.

## Project Structure

```
simulation/
├── main.py                  # CLI entry point
├── config.py                # All parameters and condition definitions
├── engine/
│   ├── agent.py             # CoTAgent, TrollAgent, LLM client
│   ├── game.py              # Round loop, phase orchestration
│   ├── market.py            # Market state, trade history, gossip buffer
│   ├── prompt_builder.py    # Assembles per-agent prompts each round
│   └── runner.py            # Runs N repetitions, saves JSON logs
├── mechanisms/
│   ├── reputation.py        # GR — system-computed reputation scores
│   ├── contracting.py       # C — propose/sign/enforce contracts
│   ├── mediation.py         # M — design/vote/delegate mediator
│   ├── governance.py        # G — Oracle (D1, D4) + state machine
│   ├── network_rewiring.py  # NR — sever/request trade links
│   ├── local_reputation.py  # NR — gossip channel (10-round history)
│   └── sanction.py          # S — costly anonymous punishment
├── metrics/
│   └── social.py            # sustainability, peace, gini, intermediate vars
├── analysis/
│   ├── analyst.py           # LLM analyst report from run logs
│   ├── reasoning_analyst.py # CoT trace analysis + lead-lag signals
│   └── plots.py             # All matplotlib visualisations
├── scripts/
│   └── recompute_warnings.py # Recompute warning metrics on existing logs
└── data/
    ├── runs/                # JSON logs per condition/run/model
    └── plots/               # Generated figures

prompts/                     # Prompt templates (base + per-mechanism)
wiki/                        # Research knowledge base
idea.md                      # Exploratory ideas and pending decisions
```

## Two-Phase Research Design

**Phase 1:** Which mechanisms achieve cooperation among self-interested agents? Run all 7 conditions (B, GR, C, M, G, NR, S) with no trolls, 30 rounds, 3 runs each.

**Phase 2:** Stress-test with 2 troll agents (20 total), 100 rounds. Compare troll isolation speed, non-troll cooperation rate, and utility across all conditions.

## Environment

Requires `AZURE_OPENAI_API_KEY` environment variable for Azure-hosted models.
