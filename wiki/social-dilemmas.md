# Social Dilemmas

**Summary**: Situations where individually rational choices produce collectively suboptimal outcomes — the core problem that any cooperative society must solve.

**Sources**: `CoopEval.pdf`, `Cooperation and Exploitation in LLM.pdf`, `Cooperateive Resilience in AI multiagent systems.pdf`

**Last updated**: 2026-05-16

---

## The Core Problem

A social dilemma exists when:
- Each agent has a dominant strategy that maximizes individual payoff (defect, free-ride, keep)
- But if all agents play their dominant strategy, everyone receives less than if all had cooperated
- The Nash equilibrium is Pareto-inferior to the cooperative outcome

This is the fundamental obstacle to [[marketplace-society|marketplace survival]]: self-interested agents, left to their own devices, will destroy the system they depend on.

## The Four Dilemmas in CoopEval

### Prisoner's Dilemma (2-player)
- Cooperate/Cooperate: both get 2
- Defect/Cooperate: defector gets 3, cooperator gets 0
- Defect/Defect: both get 1 (Nash equilibrium)
- Cooperative surplus is 1 point per player — small but real

### Public Goods Game (3-player)
- Contribute or free-ride; contributions multiplied and shared
- Free-riding is dominant even as all-contribute is best for all
- Models: taxation, commons maintenance, open-source contribution

### Traveler's Dilemma (2-player)
- Each claims a value (2–5); lower claim wins; both get lower claim, higher claimer penalized
- Nash equilibrium: both claim minimum (2)
- Cooperative equilibrium: both claim maximum (5)
- Models: price-setting, negotiation, bidding

### Trust Game (2-player)
- Player 1 can Give (10 each) or Keep (Player 1: 20, Player 2: 0)
- If Player 1 gives, Player 2 can Share back (10/10) or Keep (Player 2: 20, Player 1: 2)
- Nash: Player 1 Keeps; Cooperative: Player 1 Gives, Player 2 Shares
- Models: investment, credit, any relationship requiring vulnerability

### Stag Hunt (2-player)
- Coordinate on stag (5/5) or defect to safe rabbit (3/3)
- Unlike Prisoner's Dilemma, cooperation is rational *if you believe others will cooperate*
- Models: coordination problems, standard-setting, infrastructure investment

## Sequential Social Dilemmas (SSDs)

The Gathering and Cleanup environments from [[cooperation-exploitation-llm]] are *sequential* — agents make decisions over time in a shared environment. This adds:
- **Temporal dynamics**: past behavior influences future opportunities
- **Sustainability**: over-harvesting collapses the resource base
- **Asymmetric impact**: one defector can harm many cooperators

SSDs are a better model for [[marketplace-society]] than one-shot games, because markets operate over time.

## Why LLMs Defect by Default

From [[coopeval]]: all six tested LLMs play Nash equilibrium strategies in one-shot interactions. Reasoning analysis shows they use individual utility maximization and strategic equilibrium focus. They defect not from ignorance but because defection is the correct answer to the isolated game.

The implication: cooperation requires either changing the game (mechanisms) or changing the context (repeated interaction, reputation, contracts).

## Related pages

- [[cooperation-mechanisms]]
- [[evolutionary-dynamics]]
- [[marketplace-society]]
- [[social-metrics]]
- [[coopeval]]
- [[cooperation-exploitation-llm]]
- [[cooperative-resilience-paper]]
