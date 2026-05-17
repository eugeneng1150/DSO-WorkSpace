# Social Metrics

**Summary**: Four measurable properties — Efficiency, Equality, Sustainability, Peace — that define whether a society is functioning well, and that serve as a dense feedback signal for shaping LLM agent behavior.

**Sources**: `Cooperation and Exploitation in LLM.pdf`

**Last updated**: 2026-05-16

---

## The Four Metrics

Introduced in [[cooperation-exploitation-llm]] as components of the dense feedback signal that outperforms scalar reward alone.

### Efficiency
How much total value is produced relative to the theoretical maximum? Captures whether the collective is exploiting available cooperative surplus.

In a [[marketplace-society]]: total trade volume, GDP, resource utilization rate.

### Equality
How evenly is value distributed across agents? Captures whether the cooperative surplus is shared or captured by a subset.

A highly efficient but unequal society may be unstable — inequality can generate defection incentives for those excluded from the surplus. Measured by something like Gini coefficient or ratio of top/bottom quintile outcomes.

In a marketplace: income distribution, whether trade relationships are exploitative or mutually beneficial.

### Sustainability
Is the resource base being maintained for future interactions? Captures whether current behavior can continue indefinitely.

This is the key metric for [[cooperative-resilience]] — a society may be efficient and equal today while depleting what it needs to survive tomorrow.

In a marketplace: resource depletion rates, whether contracts are honored over time, whether trust is accumulated or eroded.

### Peace
How much conflict, sanctioning, or destructive behavior is occurring? Captures whether agents are investing energy in harming each other rather than producing.

High peace = agents resolve disputes through [[cooperation-mechanisms|mediation and contracts]] rather than retaliatory defection. Low peace = escalating punishment loops.

In a marketplace: litigation rates, contract dispute frequency, agent-to-agent conflict.

## Why These Four?

These metrics together operationalize the difference between a "surviving" society and one that:
- Is efficient but destroys its resource base (low Sustainability)
- Is sustainable but captures gains for a few (low Equality)
- Is equal but unproductive (low Efficiency)
- Is productive but consumes itself in conflict (low Peace)

A society that scores well on all four is genuinely robust.

## As a Feedback Signal

The dense feedback finding from [[cooperation-exploitation-llm]]: giving LLM agents these four metrics *in addition to* their personal reward causes them to synthesize more cooperative policies.

This works because the metrics make the social consequences of individual actions legible to the agent's reasoning. An agent that only sees its own reward cannot reason about sustainability or equality. An agent that also sees these metrics can — and does.

**Design implication for [[marketplace-society]]**: agents should receive not just their trade profit but also market-level health indicators. This is a form of [[cooperation-mechanisms|mechanism design]] at the information level.

## Connection to Cooperative Resilience

The 4-stage resilience measurement from [[cooperative-resilience-paper]] can be mapped onto these metrics:
- Pre-disruption baseline: high on all four
- Disruption impact: drop in Efficiency and/or Peace
- Adaptation: adjustments that restore Sustainability and Equality
- Recovery: all four return to baseline

## Related pages

- [[cooperation-exploitation-llm]]
- [[cooperation-mechanisms]]
- [[cooperative-resilience]]
- [[marketplace-society]]
- [[social-dilemmas]]
