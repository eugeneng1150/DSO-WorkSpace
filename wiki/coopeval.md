# CoopEval

**Summary**: Benchmarks four cooperation mechanisms (Repetition, Reputation, Mediation, Contracting) across four social dilemmas and six LLMs, finding that all LLMs defect without mechanisms and that Contracting and Mediation are most effective.

**Sources**: `CoopEval.pdf`

**Last updated**: 2026-05-16

---

## Overview

Authors: Tewolde, Zhang et al. (CMU, University of Toronto, ETH Zürich). CoopEval is the most directly relevant paper to the research question: it systematically tests which institutional mechanisms can induce cooperation among self-interested LLM agents.

Code: https://github.com/Xiao215/CoopEval

## Experimental Design

- **4 mechanisms**: NoMechanism, Repetition, Reputation (±), Mediation, Contracting
- **4–5 social dilemmas**: Prisoner's Dilemma, Public Goods, Traveler's Dilemma, Trust Game, Stag Hunt
- **6 LLMs**: Claude (Sonnet), Gemini-R, Gemini-B, GPT-5.2, GPT-4o, Qwen-30b
- **Evolutionary dynamics**: Replicator dynamics applied to measure which LLM strategies survive

Prompting was carefully designed to prevent strategy-name leakage: actions are anonymized (A0, A1) and common strategy labels (e.g., "defect") are avoided. Actions are sampled from a probability distribution each round.

## The Baseline Problem: All LLMs Defect

Without any mechanism, all six LLMs consistently play the Nash equilibrium strategy (defect/free-ride/keep) across all social dilemmas. No modern LLM is natively cooperative in a one-shot interaction.

This establishes the central problem: **self-interest is the default**. Mechanisms are not optional enhancements — they are necessary conditions for any cooperative outcome.

## Mechanism Effectiveness Rankings

From most to least effective at inducing cooperation:

1. **Contracting** — agents propose, vote on, and sign a payment contract. If all sign, payoffs are modified to make cooperation dominant. Achieves near-perfect cooperation (Fitness ≈ 2.0 in PD, 5.0 in Traveler's).
2. **Mediation** — agents propose and vote on a mediator that plays on behalf of delegating agents. Achieves perfect cooperation when all delegate.
3. **Repetition** — repeated interaction with the same partner. Significant improvement, but not perfect; some defection remains.
4. **Reputation+** (visible, positive only) — moderate improvement.
5. **Reputation−** (visible, positive and negative) — less effective than Reputation+; punishment information sometimes triggers counter-punishment.
6. **NoMechanism** — Nash equilibrium defection.

## Model-Level Results

| Model | Overall performance | Notes |
|-------|--------------------|-|
| Gemini-R | Best | Most cooperative across mechanisms |
| Gemini-B | Strong | Good with Contracting/Mediation |
| Claude | Consistent | Conservative; rarely exploited |
| GPT-5.2 | Moderate | — |
| GPT-4o | Weakest | Most exploitable; frequently defects even with mechanisms |
| Qwen-30b | Mixed | — |

## Reasoning Analysis (LLM-as-Judge)

15 justification categories were coded. Key findings:
- **Individual utility maximization** and **Strategic equilibrium focus** dominate across all mechanisms (>70% frequency)
- Mediation and Contracting shift reasoning toward **Social welfare maximization** and **Trust evaluation**
- Repetition increases **Reciprocity** and **Strategic influence**
- **Social norm conformity** is almost never invoked — LLMs don't cooperate because they feel socially obligated

## Evolutionary Dynamics

Replicator dynamics applied: models compete in a population, and those with higher fitness grow. Key findings:
- Under Repetition with Trust Game: Claude and Gemini-R achieve near-cooperative payoffs and dominate population
- Under NoMechanism in Prisoner's Dilemma: population converges to all-defection
- Contracting prevents competitive dominance by defectors by making cooperation the rational choice

**Implication**: Evolutionary pressure alone does not produce cooperation — it must be combined with mechanisms that make cooperation fitness-positive.

## Connection to Research Question

This paper is the most direct answer to the research question:

- **The answer is: Contracting and Mediation** — formal institutional mechanisms that change payoff structures
- For a [[marketplace-society]]: contracts (trade agreements, payment terms) and mediators (arbitrators, escrow services) are exactly the real-world analogues
- Reputation systems are helpful but insufficient alone
- Evolutionary dynamics show that without mechanisms, competitive pressure drives societies to all-defection equilibrium — collapse

## Related pages

- [[cooperation-mechanisms]]
- [[social-dilemmas]]
- [[evolutionary-dynamics]]
- [[marketplace-society]]
- [[cooperation-exploitation-llm]]
- [[social-metrics]]
