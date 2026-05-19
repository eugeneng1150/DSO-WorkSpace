# Dynamic Pricing Strategies for Perishable Product in a Competitive Multi-Agent Retailers Market

**Summary**: Chen, Liu, and Xu (2018) build a multi-agent simulation of competing retailers selling perishable goods (grapes), comparing Q-learning dynamic pricing against three fixed strategies. The Q-learning agent outperforms all others in most market conditions, and the spoilage mechanic fundamentally alters agent pricing behavior.

**Sources**: `dynaimic pricing.pdf` (Chen, Liu, Xu — Tianjin University, JASSS Vol. 21(2), 2018)

**Last updated**: 2026-05-19

---

## Setup

The marketplace is modeled as a bipartite graph G = <V1, V2, E> in NetLogo 5.1.0, with two types of agents:

- **4 retailer agents**, each using a different pricing strategy
- **78–240 customer agents**, divided into three preference categories (distance-sensitive, price-sensitive, balanced)

Retailers compete for the same pool of customers selling a single perishable good (grapes). The competitive cycle each period: retailers set prices -> customers choose a retailer based on preference weights -> demand is fulfilled (subject to inventory) -> profits calculated -> inventory updated.

## Pricing Strategies

| Retailer | Strategy | How it works |
|----------|----------|-------------|
| v11 | Cost-plus | Fixed markup: price = (costs) x (1 + margin) |
| v12 | Value-based | Price declines exponentially with freshness: p(t) = m*e^(-beta*t) + theta |
| v13 | Inventory-sensitive | Price adjusts based on deviation from a standard inventory trajectory |
| v14 | **Q-learning** | Learns optimal pricing through trial-and-error (3 actions: raise/lower/hold) |

The Q-learning agent uses a Boltzmann soft-max action selection with exploration tendency e_u = 0.8. Reward signal is the change in profit from the previous period. Converges after approximately 1200-1400 steps.

## Perishability Model

Two simultaneous decay mechanisms:

1. **Quantity deterioration**: inventory shrinks by psi = 0.005 (0.5%) per period — goods physically disappear
2. **Value deterioration**: freshness decays exponentially as r(t) = e^(-alpha*t) where alpha = 0.01 — older goods are worth less

When freshness drops below a customer-acceptable threshold xi, goods become unsellable and the retailer must restock regardless of remaining quantity. This creates dual pressure: goods are both disappearing and losing value over time.

## Demand Model

- Individual customer demand follows N(mu=3, sigma^2=1) kg, independent of pricing
- Customers select retailers via multi-attribute preference evaluation (distance and price, weighted by customer type)
- Shortage is allowed but backlog is not — unsatisfied customers lose their purchase opportunity

## Key Findings

1. **Q-learning outperforms all three fixed strategies** in most competitive conditions — it learns to adapt pricing to the current competitive environment
2. **"A high pricing strategy does not always bring benefits"** — overpricing backfires because goods spoil, a finding directly driven by the perishability mechanic
3. Higher discount rate (eta) reduces competition intensity and increases total market profits
4. Higher learning rate (epsilon) intensifies competition
5. Q-learning maintains advantage across varying customer demand levels and preference distributions
6. The strategy is **not always optimal** — when competitors adjust fundamental parameters, the competitive landscape shifts

## Key Parameters

| Parameter | Value |
|-----------|-------|
| Retailers | 4 |
| Customers | 78-240 |
| Restock quantity | 800 kg |
| Price bounds | [6, 12] Yuan |
| Quantity decay (psi) | 0.005/period |
| Value decay (alpha) | 0.01 |
| Learning rate (epsilon) | 0.5 |
| Discount rate (eta) | 0.4 |

## Relevance to Our Project

The paper's main contribution to our simulation is the **spoilage mechanic**: the empirical finding that perishability fundamentally changes agent pricing behavior by punishing hoarding and overpricing. We adapt this as a flat 30% inventory decay per round — simpler than their dual-decay model but sufficient to create the temporal urgency that drives more realistic trading dynamics.

The paper's setup is otherwise quite different from ours:
- **Their agents compete** (retailers vs customers) rather than **cooperate** (bilateral trade with defection risk)
- Their pricing is RL-based (Q-learning), ours is LLM-based (natural language reasoning)
- They study a single perishable good; we have three complementary goods
- No [[social-dilemmas]] or [[cooperation-mechanisms]] in their framework

See also: [[marketplace-spec]] for how spoilage is implemented in our simulation.

## Related pages

- [[marketplace-society]] — our research question: what mechanisms sustain cooperation
- [[cooperation-mechanisms]] — the formal mechanisms we test (Reputation, Contracting, Mediation)
- [[marketplace-spec]] — simulation design including spoilage implementation
- [[social-metrics]] — Sustainability and Peace, the metrics spoilage pressure amplifies
