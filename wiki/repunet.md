# RepuNet

**Summary**: First operational reputation system for LLM-based multi-agent systems; dual-level architecture (agent reputation dynamics + network evolution via gossip) raises cooperation from ~10% to 85–98%; LLM agents have an unexpected positive gossip bias.

**Sources**: `RepuNet.pdf`, `Reputation as a solution to cooperation collaspe in LLM.pdf` (same paper — arXiv 2505.05029)

**Last updated**: 2026-05-26

---

## Overview

**Authors**: Siyue Ren, Wanli Fu, Xinkun Zou, Chen Shen, Yi Cai, Chen Chu, Zhen Wang, Shuyue Hu. Published AAMAS 2026.

RepuNet is an entirely prompt-driven reputation system — no rule-based or mathematical formulations. Reputation dynamics and network evolution are "autonomously determined by the agents themselves, without any human intervention."

## Reputation Representation

Each reputation is a quintuple: **r = ⟨a, s, o, c, μ⟩**
- **a**: evaluated agent's identity
- **s**: scenario context (reputation is context-dependent)
- **o**: role of the evaluated target
- **c**: natural-language description
- **μ**: numerical score ∈ [-1, 1]

Agents maintain a **RepuNet database (ℛ)** with both self-reputation and peer-reputations, always referencing the most recently updated value.

## Architecture: Two Levels

### Level 1 — Agent-Level Reputation Dynamics

**Direct encounters**: agents form and update peer-reputations (`ShapeRepuPeer`) and self-reputations (`ShapeRepuSelf`) after each interaction.

**Indirect gossip** (modeled after evolutionary human behavior):
- After interactions, agents evaluate satisfaction based on innate values and decide whether to gossip (`GossipWill`)
- Agent selects a listener from its database (`GossipChoice`)
- Listener identifies gossip content (`GossipIdentify`) and evaluates **credibility** on a 5-point Likert scale (`GossipEvaluate`) — based on gossiper's reputation and community's prior credibility ratings
- Listener updates peer-reputation for the target (`ShapeRepuGossip`)

### Level 2 — System-Level Network Evolution

The interaction network G = (V, E) is directed — an edge (i,j) means agent i is willing to interact with agent j.

- After each encounter, agents decide whether to maintain or drop edges (`InteractEdgeShape`)
- Gossip can also trigger edge removal for agents never directly met (`GossipEdgeShape`)
- Result: network self-organizes around reputation — cooperators cluster, defectors get isolated

## Key Results

| Treatment | Prisoner's Dilemma | Voluntary Participation | Trading Investment |
|-----------|-------------------|------------------------|-------------------|
| **with RepuNet** | **0.93** | **0.85** | **0.98** |
| w/o Gossip | 0.90 | 0.81 | 0.96 |
| w/o Reputation | 0.46 | 0.29 | 0.26 |
| **w/o RepuNet** | **0.09** | **0.19** | **0.17** |

Removing gossip causes only a small drop (~3–4%). Removing reputation entirely causes collapse below 30%. Cross-LLM validation (GPT-4o mini, Qwen3 Plus, Gemini 2.5 Flash) shows consistent results across models.

## Emergent Behaviors

**Cooperative clustering**: high-reputation cooperators self-organize into dense, persistent network clusters.

**Defector isolation**: low-reputation agents are systematically excluded through assortative mixing — cooperators preferentially connect with cooperators.

**Positive gossip bias**: approximately 90% of LLM agent gossip is positive — unlike human behavior patterns documented in prior literature. Frequently gossiped-about agents have *higher* average reputations (p < 0.002). LLMs have a pro-social gossip tendency.

**Positive feedback loop**: cooperation → better reputation → more cooperative partners → continued cooperation. All correlations p < 0.001.

## Why This Outperforms CoopEval's Reputation Results

[[coopeval]] found reputation to be the least effective formal mechanism. RepuNet achieves much stronger results because:
1. **Network structure is dynamic and endogenous** — agents choose their interaction partners; defectors are excluded, not just rated poorly
2. **Gossip is explicitly modeled** — reputation propagates to agents who never directly interacted
3. **Credibility filtering** — gossip is evaluated for trustworthiness before updating reputations

CoopEval's Reputation mechanism is static (all agents always interact with all others). RepuNet's is adaptive. The network structure is as important as the reputation scores themselves.

## Connection to Research Question

For a [[marketplace-society]], RepuNet shows that reputation can be far more powerful than previously measured — if the implementation includes dynamic network structure and gossip propagation. The positive gossip bias in LLMs is an unexpected advantage: agents are naturally inclined to share positive reputations, which helps markets build trust without explicit incentives to do so.

This suggests the [[marketplace-spec]] Reputation mechanism should be enhanced to include network-level dynamics (selective trade partner choices based on reputation) rather than just broadcasting scores.

## Related pages

- [[cooperation-mechanisms]]
- [[coopeval]]
- [[social-dilemmas]]
- [[marketplace-society]]
- [[marketplace-spec]]
- [[institutional-governance]]
