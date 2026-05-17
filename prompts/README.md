# Prompt Templates

Prompt files for the marketplace simulation engine.

## Structure

| File | Purpose |
|---|---|
| `base_agent.txt` | Core prompt shown to every agent every round in all conditions |
| `baseline.txt` | `{mechanism_block}` for Condition B (no formal mechanism) |
| `reputation.txt` | `{mechanism_block}` for +Reputation conditions (R, RC, RCM) |
| `contracting.txt` | All 4 stages for +Contracting conditions (C, RC, CM, RCM) |
| `mediation.txt` | All 3 stages for +Mediation conditions (M, CM, RCM) |

## How prompts compose

Every agent prompt is built from `base_agent.txt` with `{mechanism_block}` replaced:

```
Condition B   → base_agent.txt + baseline.txt
Condition R   → base_agent.txt + reputation.txt
Condition C   → base_agent.txt + contracting.txt (active contract stage)
Condition M   → base_agent.txt + mediation.txt (delegation stage)
Condition RC  → base_agent.txt + reputation.txt + contracting.txt
Condition CM  → base_agent.txt + contracting.txt + mediation.txt
Condition RCM → base_agent.txt + reputation.txt + contracting.txt + mediation.txt
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

## Template variables

All `{variable}` placeholders are filled by the simulation engine at runtime.
See `wiki/marketplace-spec.md` for the full agent state definition.
