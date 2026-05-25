# Prompt Templates

Prompt files for the marketplace simulation engine.

## Structure

| File | Purpose |
|---|---|
| `base_agent.txt` | Core prompt shown to every agent every round in all conditions |
| `baseline.txt` | `{mechanism_block}` for Condition B (no formal mechanism) |
| `reputation.txt` | `{mechanism_block}` for +Reputation conditions (R, NR) |
| `contracting.txt` | All 4 stages for +Contracting conditions (C) |
| `mediation.txt` | All 3 stages for +Mediation conditions (M) |
| `governance.txt` | `{mechanism_block}` for Condition G (automated oracle enforcement) |
| `network_rewiring.txt` | `{mechanism_block}` for +Network Rewiring conditions (N, NR) |
| `sanction.txt` | `{mechanism_block}` for Condition S (agent-initiated costly punishment) |

## How prompts compose

Every agent prompt is built from `base_agent.txt` with `{mechanism_block}` replaced:

```
Condition B   → base_agent.txt + baseline.txt
Condition R   → base_agent.txt + reputation.txt
Condition C   → base_agent.txt + contracting.txt (active contract stage)
Condition M   → base_agent.txt + mediation.txt (delegation stage)
Condition G   → base_agent.txt + governance.txt
Condition N   → base_agent.txt + network_rewiring.txt
Condition NR  → base_agent.txt + network_rewiring.txt + reputation.txt
Condition S   → base_agent.txt + sanction.txt
```

## Contracting stages (per round)

| Stage | When sent | File section |
|---|---|---|
| 1 — Proposal | Communication phase, before trade | `contracting.txt § STAGE 1` |
| 2 — Review & Sign | After proposal received in private inbox | `contracting.txt § STAGE 2` |
| 3 — Play (active) | Trade phase, contract signed | `contracting.txt § STAGE 3` |
| 4 — Play (rejected) | Trade phase, contract rejected | `contracting.txt § STAGE 4` |

## Mediation stages (session + per round)

| Stage | When sent | File section |
|---|---|---|
| 1 — Design | Session start, before Round 1 | `mediation.txt § STAGE 1` |
| 2 — Vote | After all designs submitted | `mediation.txt § STAGE 2` |
| 3 — Delegation | Trade phase, every round | `mediation.txt § STAGE 3` |

## Active conditions

| Condition | Mechanisms | Research question |
|---|---|---|
| B | None (baseline) | How do agents behave without institutional support? |
| R | Reputation | Does public reputation scoring deter defection? |
| C | Contracting | Do binding contracts with breach penalties sustain cooperation? |
| M | Mediation | Does agent-designed mediation improve outcomes? |
| G | Governance | Does automated oracle enforcement (top-down) sustain cooperation? |
| N | Network Rewiring | Can agents restructure trade links to isolate defectors? |
| NR | Network Rewiring + Reputation | Does combining reputation with link rewiring improve cooperation? |
| S | Sanction | Will agents pay personal cost to punish defectors (bottom-up)? |

## Template variables

All `{variable}` placeholders are filled by the simulation engine at runtime.
See `wiki/marketplace-spec.md` for the full agent state definition.
