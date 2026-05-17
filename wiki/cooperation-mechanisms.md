# Cooperation Mechanisms

**Summary**: Institutional and structural mechanisms that enable cooperative outcomes among self-interested agents, ranked by effectiveness from the empirical literature.

**Sources**: `CoopEval.pdf`, `Cooperation and Exploitation in LLM.pdf`, `AgentSociety.pdf`

**Last updated**: 2026-05-16

---

## Why Mechanisms Are Necessary

Without mechanisms, all modern LLMs defect in [[social-dilemmas]] (source: [[coopeval]]). Cooperation is not a natural property of self-interested agents — it must be *structurally induced*.

A mechanism is anything that changes the information, payoffs, or structure of an interaction so that cooperation becomes rational (or at least compatible with self-interest).

## The Four Formal Mechanisms (CoopEval)

### 1. Contracting
Agents propose a payment contract (additional payoffs conditional on actions), vote on it, and sign if all agree. The contract modifies the base payoff matrix.

**Effectiveness**: Highest. Achieves near-perfect cooperation in Prisoner's Dilemma and Traveler's Dilemma. Makes cooperation a dominant strategy by changing payoffs directly.

**Real-world analogues**: Trade contracts, service agreements, payment terms, escrow, smart contracts.

**Why it works**: Converts a social dilemma into a non-dilemma. If the contract is well-designed, defection becomes irrational.

**Failure mode**: Requires all parties to sign (unanimous consent). One defecting party can block the contract.

### 2. Mediation
Agents propose a mediator (a decision function mapping number of delegators → action), vote on mediators, then choose to delegate or act independently. The mediator plays a coordinating action for all delegators simultaneously.

**Effectiveness**: Near-equal to Contracting. Achieves perfect cooperation when all agents delegate.

**Real-world analogues**: Arbitrators, escrow agents, clearinghouses, regulatory bodies.

**Why it works**: Removes the prisoner's dilemma structure by replacing individual choices with a coordinated action. All delegators receive the cooperative outcome regardless of what non-delegators do.

**Failure mode**: Requires trust in the mediator. Mediator quality matters — poorly designed mediators produce poor outcomes.

### 3. Repetition
Agents play the same game repeatedly with the same partner. Past actions are visible and influence future interactions.

**Effectiveness**: Significant improvement over no mechanism, but not perfect. Most effective in Trust Game (near-cooperative payoffs). Less effective in Prisoner's Dilemma without additional mechanisms.

**Real-world analogues**: Ongoing trade relationships, supplier contracts, long-term business partnerships.

**Why it works**: Makes future interactions contingent on current behavior. Defection today risks losing cooperative surplus tomorrow (shadow of the future).

**Failure mode**: Requires sufficient continuation probability. Agents defect near the end of a known-length game. Also fails with short memory or high discount rates.

### 4. Reputation
Agents' past actions are visible to future interaction partners (not just current ones). Two variants:
- **Reputation−**: Only positive reputation visible
- **Reputation+**: Both positive and negative visible

**Effectiveness**: Moderate. Reputation+ sometimes backfires (punishment triggers counter-punishment). Less effective than Contracting or Mediation.

**Real-world analogues**: Credit scores, seller ratings (eBay/Amazon), professional reputation, social proof.

**Why it works**: Extends the shadow of the future across the entire population. Defection in one interaction damages prospects in all future interactions.

**Failure mode**: Reputation systems can be gamed (fake reviews, sybil attacks). Punishment information can trigger conflict rather than reform.

## The Fifth Mechanism: Dense Social-Metric Feedback

From [[cooperation-exploitation-llm]], a different approach: rather than changing the game structure, change the *feedback signal*. Providing four [[social-metrics]] (Efficiency, Equality, Sustainability, Peace) alongside scalar reward produces more cooperative LLM policies.

This is a mechanism that operates at the agent design level rather than the game level — it shapes what the agent optimizes for.

**Real-world analogue**: ESG reporting, stakeholder capitalism, triple-bottom-line accounting.

## Evolutionary Pressure as Mechanism Amplifier

From [[coopeval]]: [[evolutionary-dynamics|replicator dynamics]] can boost cooperation to 90–100% when combined with Contracting or Repetition. The mechanism makes cooperation fitness-positive; evolution selects for it.

## Mechanism Design for Marketplace

For a [[marketplace-society]] with self-interested agents, the evidence suggests a layered approach:

| Layer | Mechanism | Purpose |
|-------|-----------|---------|
| 1 (foundation) | Contracts | Make cooperation rational by changing payoffs |
| 2 (coordination) | Mediation/Arbitration | Handle disputes and coordinate when contracts fail |
| 3 (network) | Reputation | Extend accountability across the whole market |
| 4 (incentives) | Social metrics in feedback | Align agent optimization with collective welfare |
| 5 (selection) | Evolutionary pressure | Over time, select for cooperative agent types |

No single mechanism is sufficient. The papers show that Contracting alone fails with one non-signer; Reputation alone is insufficient; Repetition requires long time horizons.

## Related pages

- [[social-dilemmas]]
- [[evolutionary-dynamics]]
- [[social-metrics]]
- [[marketplace-society]]
- [[coopeval]]
- [[cooperation-exploitation-llm]]
- [[cooperative-resilience]]
