# Evolutionary Dynamics

**Summary**: Replicator dynamics model how strategies compete and spread in a population over time, providing a framework for understanding which cooperation mechanisms are stable in the long run.

**Sources**: `CoopEval.pdf`

**Last updated**: 2026-05-16

---

## Replicator Dynamics

In replicator dynamics, agent types (here: different LLM models) compete in a population. Types with above-average fitness reproduce (their share of the population grows); types with below-average fitness shrink.

Formally: if type *i* has fitness *f_i* and mean fitness is *f̄*, then the growth rate of type *i* is proportional to (*f_i* - *f̄*).

This models evolutionary or competitive selection: strategies that are more successful crowd out less successful ones. In a market context, this maps to businesses or agents that earn more growing and those that earn less exiting.

## Key Findings from CoopEval

### Without mechanisms: convergence to all-defection
Under NoMechanism in Prisoner's Dilemma, replicator dynamics drive the population toward the model that defects most reliably. Even a model that is more cooperative can be outcompeted if it is exploited by defectors.

**Implication**: A marketplace without institutional mechanisms will, over evolutionary time, select for increasingly exploitative agents. Self-interest is not just a problem at the individual level — it's a systemic pressure.

### With Repetition (Trust Game): cooperative types dominate
When interactions are repeated (same partner, history visible), Claude and Gemini-R achieve near-cooperative payoffs and grow to dominate the population. Defecting types are gradually outcompeted.

**Implication**: Repeated interaction alone can be sufficient for cooperation to be evolutionarily stable in some games — but not all (PD remains difficult).

### With Contracting: cooperation becomes the evolutionary stable strategy
When contracts are in place, the payoff structure changes so that cooperative strategies outcompete defecting ones across games. Population converges to cooperation.

**Implication**: [[cooperation-mechanisms|Contracting]] doesn't just induce cooperation in a single interaction — it creates the conditions for cooperative types to take over the population.

## Evolutionary Pressure as Amplifier

From [[coopeval]]: evolutionary dynamics boost cooperation rates to 90–100% when combined with Contracting or Mediation. The mechanism makes cooperation fitness-positive; selection does the rest.

This is significant because it means well-designed mechanisms are self-reinforcing over time: they not only induce cooperation immediately but also change the composition of the agent population toward more cooperative types.

## Connection to Research Question

"What mechanism allows the *survival* of a society with self-interested agents?" has an evolutionary answer:

- A society survives if cooperative strategies are evolutionarily stable — i.e., they cannot be invaded by defecting mutants
- This requires mechanisms that make defection fitness-negative
- Contracting achieves this most reliably; Repetition achieves it conditionally; NoMechanism fails

The evolutionary lens also explains why resilience ([[cooperative-resilience]]) matters: a society that achieves cooperation but loses it under disruption may not recover if the disruption shifts evolutionary pressures toward defection during the disruption period.

## Evolutionary Stable Strategies (ESS)

A strategy is an ESS if:
1. It performs at least as well as any mutant strategy when common
2. It performs better than the mutant when the mutant is rare

Under NoMechanism, defection is ESS. Under Contracting, cooperation becomes ESS. The design goal for a [[marketplace-society]] is to engineer the game so cooperation is the ESS.

## Related pages

- [[social-dilemmas]]
- [[cooperation-mechanisms]]
- [[coopeval]]
- [[marketplace-society]]
