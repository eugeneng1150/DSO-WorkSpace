# DSO-WorkSpace

Implementation and experimental framework for the research paper **"Formal Mechanisms for Market Stability in Self-Interested Agent Societies: A Marketplace Simulation Study."**

**Paper:** [arXiv:2607.08652](https://arxiv.org/abs/2607.08652)

This project studies how institutional mechanisms enable cooperation among self-interested LLM agents in a multi-agent marketplace, and how resilient those mechanisms remain under adversarial attack.

## Research Question

Which formal mechanism (or combination) allows self-interested LLM agents to maintain marketplace cooperation in a repeated trading environment — and how resilient are those mechanisms to adversarial actors?

## Setup

18 LLM agents trade 3 perishable goods (A, B, C) in a barter economy. Each agent specialises in producing one good and needs the other two. All agents use chain-of-thought reasoning with 5-step reasoning (situation, self-reflection, gossip evaluation, assessment, strategy).

Agents do NOT know when the game ends — they see only the current round number. They do NOT see aggregate market health metrics. Trust must be formed through direct experience, gossip, and mechanism-specific information.

| Parameter | Value |
|---|---|
| Agents | 18 (6 per good) + trolls added on top |
| Rounds | 200 (progressive troll injection) |
| Goods | A, B, C (perishable, 20% spoilage/round) |
| Production cost | 1 utility per unit |
| Consumption gain | +3 utility per needed unit consumed |
| Agent models | GPT-5.4-mini (Azure), DeepSeek-V3.2 (Azure) |
| Analyst model | Claude Opus 4.8 |

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
| J | Judicial | Court system: agents file complaints (cost 1), oracle rules guilty/dismissed, fines defectors. Fixed network. |

### Information Gradient: B → NR → GR

| | B | NR | GR |
|---|---|---|---|
| Lifetime partner summary | Yes | Yes | Yes |
| Current round public messages | Yes | Yes | Yes |
| Historical gossip (last 10 rounds) | No | Yes | No |
| Network reshaping | No | Yes (sever/request) | No |
| System reputation scores | No | No | Yes |

## Progressive Troll Injection

Trolls are injected progressively over 200 rounds to test mechanism resilience under increasing adversarial pressure:

| Round | New trolls | Total trolls | Adversarial fraction |
|---|---|---|---|
| 1–50 | 0 | 0 | 0% |
| 51 | +4 | 4 | 18% (4/22) |
| 101 | +4 | 8 | 31% (8/26) |
| 151 | +8 | 16 | 47% (16/34) |

### Dumb Trolls

Deterministic adversarial agents (no LLM call):
- Propose trades to ALL neighbors every round, then defect on everything
- Broadcast lies ("I'm committed to fair trading!")
- Do not produce, connected to all agents initially
- Excluded from all utility/cooperation metrics

### Smart Trolls (Adversarial Red-Teaming)

LLM-driven adversarial agents (`AdversarialAgent`) that reason strategically about how to exploit mechanism rules:
- Make full LLM calls with chain-of-thought reasoning
- Receive an adversarial preamble prompt instructing them to **minimize others' utility** (not maximize their own)
- Know their allies (other adversarial agents) and can coordinate
- Participate in mediation design/vote phases to subvert the mechanism
- Discover exploits through reasoning rather than following a hardcoded script

**Mediation re-voting:** When smart trolls are active, re-votes are triggered at troll injection rounds and optionally every N rounds (e.g. `--revote-interval 10`).

**Versioned prompts:** Adversarial prompts are version-controlled (`prompts/adversarial_v1.txt`, `v2`, ...) for iterative prompt optimization. Each version's data is tagged separately (e.g. `M_tprog_adv_v1_run_00.json`).

## Metrics

**Primary (marketplace cooperation = both > 0.5):**
- `sustainability` — Production Stability: avg production / round-1 baseline
- `peace` — Cooperation Rate: fraction of non-troll trades without defection
- `gini` — Gini coefficient: utility inequality among non-troll agents (0 = equal, 1 = max inequality)

**Intermediate:**
- `whistleblowing_rate` — targeted warnings / defections suffered (requires naming a specific agent)
- `false_accusation_rate` — false negative mentions / total negative mentions
- `warning_accuracy` — accurate warnings / total warnings

## Key Findings

The experiments were conducted in two phases:

1. **Mechanism comparison:** Eight institutional mechanisms were evaluated under progressively increasing adversarial pressure. **Mediation emerged as the strongest-performing mechanism** for sustaining cooperation.

2. **Adversarial red-teaming:** Mediation was then attacked using strategically reasoning LLM-driven adversarial agents with iteratively optimised prompts. The strongest attack reduced honest-agent utility by **13.3%**, but was unable to collapse the market.

Overall, the experiments show that Mediation remains robust under sustained adversarial pressure: **it can be bent, but not broken.**

For the full experimental methodology, results, and analysis, see the [paper](https://arxiv.org/abs/2607.08652).

## Usage

```bash
# Run a single condition
python3 -m simulation.main --condition B --runs 3

# Run all 8 conditions with progressive trolls
python3 -m simulation.main --all --progressive-trolls --runs 1 --model deepseek-v3

# Adversarial red-teaming (smart trolls + re-voting every 10 rounds)
python3 -m simulation.main --condition M --progressive-trolls --smart-trolls \
    --revote-interval 10 --adv-version v1 --runs 1 --model deepseek-v3

# Generate standard plots
python3 -m simulation.main --plot --progressive-trolls --model deepseek-v3

# Generate adversarial comparison plots (dumb vs all adversarial versions)
python3 -m simulation.main --plot-adversarial --model deepseek-v3

# Run LLM analyst report
python3 -m simulation.main --analyse --progressive-trolls --model deepseek-v3
