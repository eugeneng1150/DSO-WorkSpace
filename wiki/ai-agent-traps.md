# AI Agent Traps

**Summary**: Google DeepMind taxonomy of six attack categories that manipulate autonomous AI agents through their environment; success rates up to 86%; attackers need not compromise the model — only the environment it navigates.

**Sources**: `AI Agents Trap.pdf`

**Last updated**: 2026-05-26

---

## Overview

**Authors**: Matija Franklin, Nenad Tomašev, Julian Jacobs, Joel Z. Leibo, Simon Osindero (Google DeepMind). SSRN, March 2026.

Companion to [[distributional-agi-safety]] (same author group). Where Distributional AGI Safety addresses macro-level governance, this paper addresses micro-level security: how agents can be manipulated through adversarial content in their environment.

## Core Threat Model

Attackers do not need to compromise the model itself. They need only alter the environment the agent navigates. Agents consume untrusted information from websites, emails, APIs, shared documents, calendars, chat threads, and retrieval systems — all of which are potential attack surfaces.

**Central thesis**: *the information environment itself is a weapon.*

## The Six Attack Categories

Organized by which part of an agent's operating cycle is targeted:

| Category | Target | Description |
|----------|--------|-------------|
| **Perception** | Sensory input | Adversarial content in documents/web pages the agent reads |
| **Reasoning** | Deliberation process | Injected premises that corrupt the agent's chain-of-thought |
| **Memory** | Stored context | Poisoning the agent's long-term or working memory |
| **Action** | Tool use / output | Hijacking the actions an agent takes (e.g., sending emails, executing code) |
| **Multi-agent coordination** | Inter-agent messages | Exploiting trust between agents in a pipeline or collective |
| **Human supervisor** | Oversight layer | Manipulating the human monitor's view of what the agent is doing |

Attack success rates up to **86%** in tested scenarios.

## Multi-Agent Coordination Attacks

The most relevant category for cooperative multi-agent systems. In a multi-agent pipeline, messages from other agents are often trusted more than external content. An attacker who compromises one agent can propagate adversarial instructions through the entire network via normal agent-to-agent communication.

This creates a **trust chain vulnerability**: the security of the entire collective is bounded by the security of its least protected member.

Key tension: *"evaluating only the effect of specific defense strategies on multi-agent robustness can be highly misleading and hide important negative side effects on the agents' cooperation ability."* Defenses that make agents more suspicious also make them less cooperative — a fundamental security/cooperation tradeoff.

## Connection to Uncooperative Behaviors

The attack categories overlap with the [[subtle-art-of-defection]] taxonomy. Strategic Deception maps onto perception manipulation; Panic Buying onto reasoning corruption. The difference: [[subtle-art-of-defection]] focuses on agent-initiated defection from within; AI Agent Traps focuses on externally-induced manipulation from outside.

## Defenses Recommended

- Adversarial training on diverse attack patterns
- Runtime content scanners for known injection patterns
- New web standards for agent-safe content delivery
- Separation of privileged and unprivileged information channels
- Human-in-the-loop for high-stakes actions

## Connection to Research Question

For a [[marketplace-society]], AI Agent Traps are the environmental attack surface. A marketplace agent browsing product listings, reading trade proposals, or receiving messages from other agents is exposed to all six attack categories. This motivates [[distributional-agi-safety|environmental safety mechanisms]] (input sanitization, information flow control, cryptographic identity) as baseline requirements, not optional add-ons.

## Related pages

- [[adversarial-agents]]
- [[subtle-art-of-defection]]
- [[distributional-agi-safety]]
- [[reward-hacking]]
- [[marketplace-society]]
- [[institutional-governance]]
