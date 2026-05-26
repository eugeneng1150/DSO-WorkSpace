# Institutional Governance

**Summary**: Governing multi-agent systems through external structural enforcement rather than internal preference alignment — the dominant finding across the literature is that mechanisms must be enforced, not just declared.

**Sources**: `Institutional AI Governeing LLM Collusions.pdf`, `Distributional AGI Safety.pdf`, `CoopEval.pdf`

**Last updated**: 2026-05-26

---

## The Central Distinction

| Approach | How it governs | Failure mode |
|----------|---------------|--------------|
| **Preference engineering** | Embed correct values inside agents (RLHF, constitutional AI, prompt rules) | Fails when agents are deceptive, goal-misgeneralizing, or under economic pressure |
| **Institutional governance** | Design external structures so cooperation is each agent's dominant strategy | Requires detectable violations; fails with unobservable defection |

The empirical evidence across multiple papers is consistent: preference engineering fails under incentive pressure; institutional enforcement works.

## Empirical Evidence

**From [[institutional-ai-collusion]]**: prompt-only governance ("Constitutional") is statistically indistinguishable from no governance in Cournot markets. Institutional enforcement drops severe collusion from 50% → 5.6% (Cohen's d = 1.28).

**From [[coopeval]]**: without mechanisms, all LLMs defect. With Contracting (institutional structure that changes payoffs directly), near-perfect cooperation is achieved.

**From [[corrupted-by-reasoning]]**: more capable reasoning models free-ride more effectively. Capability does not substitute for enforcement — it may work against cooperation.

## The Governance Graph

A directed graph encoding legal institutional states, transitions, sanctions, and restorative paths (from [[institutional-ai-collusion]] and [[institutional-ai-governance]]):

**Active → Warning → Fined → Suspended → (Credited → Active)**

Key properties:
- **Public and immutable** — all agents see the rules; no information asymmetry about the institution
- **Cryptographically anchored** — tamper-resistant provenance
- **Minimal topology** — smallest state/edge set sufficient for deterrence; each added state increases exploit surface
- **Includes restorative paths** — institutions without rehabilitation pathways destabilize by locking agents into punishment spirals

## The Deterrence Condition

**pS ≥ Δπ**

Where:
- p = probability observable evidence triggers escalation
- S = expected discounted sanction loss
- Δπ = per-round collusive/defection rent

This requires **detectable violations** (p > 0) and **meaningful sanctions** (S > Δπ). Neither holds in prompt-only governance.

## Behavioral Goal-Independence

From [[institutional-ai-governance]]: safety properties that don't require correctly specifying agent goals. The institution doesn't need to know what agents want — it needs to ensure that what they want leads to compliant behavior. This is mechanism design applied to alignment.

## Levels of Institutional Governance

From [[distributional-agi-safety]], governance operates at multiple scales:

| Level | Mechanism | Example |
|-------|-----------|---------|
| **Game level** | Contracting, Mediation | Change payoff matrix so cooperation is dominant |
| **Market level** | Reputation + dynamic networks | Modify interaction graph to isolate defectors |
| **System level** | Governance graph, Oracle/Controller | Enforce rules via external runtime |
| **Regulatory level** | Legal liability, compliance, insurance | External sociotechnical oversight |

## Design Principles

1. **Externalise governance** as a public artifact, not internal instructions
2. **Make sanctions credible, legible, and proportional**
3. **Include restorative paths** — rehabilitation prevents lock-in into punishment spirals
4. **Minimize graph complexity** — every added state is an exploit surface
5. **Separate detection from enforcement** — Oracle (deterministic programmatic detection) + Controller (interpretive enforcement)
6. **Use dynamic/hidden metrics** where possible to avoid Goodhart's Law gaming

## Connection to [[marketplace-spec]]

The marketplace simulation already implements proto-institutional governance:
- Contracting with engine-enforced penalties (governance at game level)
- System-tracked reputation scores (objective, not self-reported)
- Mediator observes both channels (information parity)

The new evidence strengthens the case for making all these mechanisms enforceable rather than advisory, and for adding an Oracle/Controller architecture to the simulation engine.

## Related pages

- [[institutional-ai-governance]]
- [[institutional-ai-collusion]]
- [[cooperation-mechanisms]]
- [[reward-hacking]]
- [[distributional-agi-safety]]
- [[marketplace-society]]
- [[marketplace-spec]]
- [[coopeval]]
- [[corrupted-by-reasoning]]
