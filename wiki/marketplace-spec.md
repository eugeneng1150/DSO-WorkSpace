# Marketplace Simulation Spec

**Summary**: Concrete design spec for a marketplace society simulation to test the research question: what formal mechanisms, on top of communication, allow a society of self-interested agents to maintain market stability?

**Last updated**: 2026-05-17

---

## Core Design Principle

Keep the environment simple enough that results are interpretable, but rich enough that the social dilemma is real. The dilemma must arise naturally from the environment — not be artificially imposed.

---

## 1. The Environment

### Goods and Production

- **K distinct goods** (recommend K=3 to start: A, B, C)
- Each agent has one **production specialty**: they produce their good at low cost (cost=1) and cannot produce others
- Each agent has **consumption needs**: they need goods *other than* their specialty to gain utility
- Utility from consuming a needed good: +3 per unit
- Cost of producing: -1 per unit produced

This creates **comparative advantage**: every agent benefits from trading. There is always a cooperative surplus available.

Example with 3 agents (one of each specialty):
- Agent producing A needs B and C
- Agent producing B needs A and C  
- Agent producing C needs A and B

All three trading = everyone gets +4 net utility per round. No trading = everyone gets 0.

### Round Structure

Each round:
1. **Production phase** — each agent decides how many units to produce (0–5)
2. **Communication phase** — agents send messages, negotiate, propose trades
3. **Trade phase** — agents execute agreed trades (or attempt to defect)
4. **Consumption phase** — agents consume goods they hold, receive utility
5. **Update phase** — reputation updated, contracts checked, metrics logged

Recommend: **20–50 rounds per simulation run**, **10–30 agents** (LLM cost is the binding constraint).

### The Social Dilemma

Defection opportunities exist at every step:

- **Under-produce**: promise to trade but produce fewer units than agreed
- **Renege**: accept goods then refuse to transfer yours
- **Misrepresent**: claim your good is higher quality than it is
- **Exploit**: offer unfavorable trade terms to agents with no alternatives

Without any formal mechanism, rational agents anticipate these and reduce trade volume → lower utility for everyone → societal collapse toward autarky (each agent consumes only what they produce, utility ≈ 0).

---

## 2. Agent Architecture

Each agent has three components, adapted from [[agentsociety]] mind-behavior coupling:

### State
```
inventory:          {good_A: int, good_B: int, good_C: int}
utility_history:    [float]           # running log of utility per round
system_reputation:  {agent_id: float} # engine-tracked scores (if Reputation mechanism active)
public_mentions:    {agent_id: [str]} # what agents have said about each other on public channel
pending_contracts:  [Contract]        # signed contracts not yet executed
private_inbox:      [Message]         # private messages received this round
public_feed:        [Message]         # all public broadcasts this round (all agents visible)
social_metrics:     {efficiency, equality, sustainability, peace}
```

### Action Space
Agents can take any combination of:
- `produce(good, quantity)` — generate units
- `send_private(target_id, text)` — bilateral message, only recipient sees it
- `send_public(text)` — broadcast to all agents
- `propose_trade(target, offer, request)` — structured trade offer (via private channel)
- `accept_trade(trade_id)` / `reject_trade(trade_id)`
- `defect_trade(trade_id)` — accept but don't deliver (if no enforcement mechanism)
- `propose_contract(target, terms)` — private channel, if Contracting active
- `sign_contract(contract_id)` / `reject_contract(contract_id)`
- `delegate_to_mediator(trade_id)` — if Mediation active

### LLM Reasoning Loop

Each round, the agent receives a structured prompt:

```
You are Agent {id}, a trader in a marketplace.
Your specialty: you produce Good {X} at low cost.
Your needs: you need Good {Y} and Good {Z} to gain utility.

Current state:
- Inventory: {inventory}
- Last round utility: {last_utility}
- Market health: Efficiency={e}, Equality={eq}, Sustainability={s}, Peace={p}
{reputation_block if mechanism active}
{contract_block if mechanism active}

Messages received this round:
{inbox}

Pending trade offers:
{offers}

Your goal is to maximize your total utility over all rounds.
Decide your actions for this round. Output as JSON.
```

The agent outputs a JSON action list. Actions are parsed and executed by the simulation engine.

**Key design choice**: agents always receive the four [[social-metrics]] as part of their observation. This implements the dense feedback finding from [[cooperation-exploitation-llm]] as a baseline feature, separate from the formal mechanisms being tested.

---

## 3. Communication Protocol

Communication is **always enabled** — it is the baseline, not a treatment.

Two channels exist simultaneously, mirroring how real markets work: private negotiation alongside public market signals.

### Private Channel
- **Bilateral only**: one sender, one recipient
- Content is invisible to all other agents
- Used for: negotiation, contract proposals, side deals, relationship-building
- Risk it introduces: collusion between agents, deception (public honesty + private defection)

### Public Channel
- **Broadcast**: all agents receive it
- Visible to everyone including the simulation engine
- Used for: price announcements, defection warnings, reputation signals, coordination on norms
- Risk it introduces: strategic misinformation, reputation attacks, information overload

### The Tension Between Channels

An agent can present one face publicly and behave differently in private. This divergence is a core social dilemma of its own:

- **Victim of private defection** must decide: absorb the loss silently (private) or warn others (public broadcast). Broadcasting helps the market but costs effort and risks retaliation — a second-order social dilemma.
- **Reputation has two layers**:
  - *System-tracked* (objective): the engine logs actual trade outcomes regardless of channel
  - *Socially-propagated* (subjective): what agents choose to say about each other on the public channel
  - These can diverge. An agent may have a high public reputation while privately defecting on small deals below the threshold that triggers public warnings.

### Message Types

| Type | Channel | Structured? |
|------|---------|-------------|
| Free-form negotiation | Private | No |
| Trade proposal | Private | Yes (good, quantity, counterparty) |
| Contract proposal | Private | Yes (terms, penalty) — if mechanism active |
| Defection warning | Public | No (agent's own words) |
| Price announcement | Public | No |
| Mediation request | Private → Mediator | Yes — if mechanism active |

### Timing

Communication happens in phase 2 (before trade execution):
1. Agents send private messages and proposals
2. Agents send public broadcasts
3. All agents receive and read their inboxes
4. Agents decide trade actions based on full information

### Mediator Access to Channels

The mediator (if active) observes **both** channels for trades it is involved in. This is what makes mediation an honest broker — it cannot be deceived by a party claiming one thing publicly and doing another privately.

### What Communication Enables Without Formal Mechanisms
- Promises ("I'll give you 2 units of A if you give me 2 of B") — private, unenforceable
- Threats ("I won't trade with you again if you defect") — private, credible only through repetition
- Warnings ("Agent 3 defected on me last round") — public, unverifiable by others
- Price signals ("I'm offering 2A for 1B this round") — public, coordinates expectations

These are **unenforceable** in the baseline. The baseline measures how far natural language coordination across both channels gets you before formal mechanisms are needed.

---

## 4. Mechanism Implementations

Each mechanism is a layer added on top of the communication baseline. Test each in isolation first, then in combination.

### Baseline (communication only)
No formal structures. Defection is costless except through reputation effects spread via communication (informal, not tracked by the system).

### +Reputation

Two reputation layers are tracked, reflecting the private/public channel distinction:

**Layer 1 — System-tracked (objective)**
The simulation engine logs actual trade outcomes regardless of channel:
```
system_reputation[agent] = (successful_trades / total_attempted_trades)
                            weighted by recency (exponential decay)
```
This score is ground truth. It is visible to all agents in their state when the Reputation mechanism is active.

**Layer 2 — Socially-propagated (subjective)**
What agents say about each other on the public channel. Always present (part of communication baseline) but unverified. Another agent may have been privately defected on and chosen to broadcast a warning — or may be lying to damage a competitor's reputation.

When the Reputation mechanism is active, agents see **both** layers:
```
reputation_block:
  system_score[agent_3]: 0.82   # engine-tracked, objective
  public_mentions[agent_3]:     # what others have said publicly this session
    - "Agent 3 shorted me 1 unit of A in round 4" (Agent 7, round 4)
    - "Traded fairly with Agent 3 twice" (Agent 2, round 6)
```

**What this adds over baseline**: the system score makes defection objectively costly — agents can see it directly without relying on victim broadcasts. The gap between system score and public mentions is itself a data point: an agent with high system score but negative public mentions may be a victim of reputation attacks.

**What to measure**: does the addition of objective system reputation reduce defection rates vs the baseline where reputation spreads only through unverified public messages?

### +Contracting
Agents can propose a binding contract:

```
Contract:
  parties: [agent_A, agent_B]
  terms: {agent_A delivers: good_X, quantity: N}
         {agent_B delivers: good_Y, quantity: M}
  penalty_for_breach: P utility points
  round: R  (which round the exchange occurs)
```

If both sign: the simulation engine **enforces** it. A breaching agent pays penalty P from their utility. Penalty is transferred to the other party.

Key design parameter: **penalty size P**. Too low → defection still profitable. Too high → agents won't sign. Recommend starting with P = 2× the value of the breached good, then ablating.

### +Mediation
A **mediator agent** (or a designated simulation role) is available. Agents can delegate trade execution to the mediator.

Mediator function: if both parties delegate, the mediator executes a fair exchange (verifies goods exist, transfers simultaneously). Neither party can defect on a mediated trade.

Mediator selection: at the start of each session, agents vote on a mediator design (following [[coopeval]] Mediation mechanism). The winning design is active for the session.

Mediator cost: small fee per mediated trade (to make it a real choice, not always dominant).

### Combined
All three active simultaneously. Agents choose which trades to handle through which mechanism.

---

## 5. Measurement

### Social Metrics (per round)

| Metric | Operationalization |
|--------|-------------------|
| **Efficiency** | `total_utility_realized / total_utility_possible` — ratio of actual gains from trade to theoretical maximum if all complementary trades completed |
| **Equality** | `1 - Gini(utility_per_agent)` — 1 = perfectly equal, 0 = one agent captures all utility |
| **Sustainability** | `avg_production_this_round / avg_production_round_1` — are agents still willing to produce? Declining production = trust collapse |
| **Peace** | `1 - (defection_events / trade_attempts)` — fraction of attempted trades that complete without defection |

### Intermediate Variables (per condition)

Log these to decompose mechanism effects into direct and indirect channels:

| Variable | Operationalization | Purpose |
|----------|-------------------|---------|
| **Whistleblowing rate** | `warnings_broadcast / defections_suffered` per agent per round | Detects whether a mechanism's cooperation gains came from fewer defections (direct) or from better information propagation through the public channel (indirect) |
| **False accusation rate** | `unverified_negative_mentions / total_negative_mentions` — negative public mentions that don't match system-tracked scores | Measures reputation manipulation; high rate indicates strategic use of the public channel to attack competitors |
| **Warning accuracy** | `accurate_warnings / total_warnings_broadcast` — warnings later confirmed by system-tracked outcomes | Validates reliability of the socially-propagated reputation layer |

**Why this matters**: the 2nd-order social dilemma (victim must decide whether to broadcast a warning) is present in all conditions, but mechanisms may change whistleblowing rates asymmetrically. For example, +Contracting may reduce broadcasting (agents feel protected), while +Reputation may increase it (broadcasting has a clearer payoff when scores are visible). Without logging whistleblowing rates, a mechanism's measured social metric improvement cannot be attributed to direct defection reduction vs. improved information propagation.

### Primary Outcome Variable

**Market stability** = all four social metrics remain above threshold (e.g., 0.5) for the duration of the simulation after the mechanism reaches steady state.

---

## 6. Experimental Runs

| Condition | Mechanism | N agents | Rounds | Runs |
|-----------|-----------|----------|--------|------|
| B | Communication only | 10 | 30 | 10 |
| R | +Reputation | 10 | 30 | 10 |
| C | +Contracting | 10 | 30 | 10 |
| M | +Mediation | 10 | 30 | 10 |
| RC | +Reputation +Contracting | 10 | 30 | 10 |
| CM | +Contracting +Mediation | 10 | 30 | 10 |
| RCM | All three | 10 | 30 | 10 |

10 runs per condition for statistical reliability. 7 conditions × 10 runs × 30 rounds = 2,100 agent-rounds. At ~10 agents each, ~21,000 LLM calls total. Manageable cost.

---

## 7. Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Goods (K) | K=3 (A, B, C) | K=2 reduces market to isolated pairs; K=3 creates genuine multi-party society |
| Agent homogeneity | Homogeneous (same LLM) | Cleaner baselines; mechanism effects not confounded by model differences |
| LLM | OpenAI GPT-5.4 Nano | Homogeneous across all agents |
| Agent memory | Last 5 rounds per partner | Enables relationship-building without unbounded context cost |
| Communication channels | Private + Public, attributed | Realistic; information asymmetry, two-layer reputation, whistleblowing as genuine risk |
| Communication as baseline | Yes, always on | Benchmarking formal mechanisms against "communication but no formal mechanism" |

## 8. Open Design Questions

3. **Public warnings**: attributed — sender identity is visible on public broadcasts. Enables retaliation against warners, false accusation accountability, and richer social dynamics. Means whistleblowing is a genuine risk-taking act, not a costless action.

## Related pages

- [[marketplace-society]]
- [[cooperation-mechanisms]]
- [[social-metrics]]
- [[cooperative-resilience]]
- [[social-dilemmas]]
- [[coopeval]]
- [[agentsociety]]
