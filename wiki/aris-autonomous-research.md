# ARIS: Autonomous Research in Sleep

**Summary**: An open-source harness for autonomous ML research using LLM agents, with a key architectural principle of cross-family adversarial review to prevent fabricated results.

**Sources**: `Autonomous Research.pdf`

**Last updated**: 2026-05-16

---

## Overview

Authors: Ruofeng Yang et al. (SJTU). ARIS (Autonomous Research In Sleep) is a system that enables an LLM agent to autonomously conduct ML research — running experiments, analyzing results, and iterating — while humans sleep.

While not directly about social dilemmas, ARIS is relevant to the research question as a case study in *making autonomous agents reliable* when their incentives are misaligned with ground truth.

## Three-Layer Architecture

### Execution Layer
65+ skills covering: data loading, model training, hyperparameter search, result logging, paper reading. Agents draw on these skills to execute research workflows.

### Orchestration Layer
Five workflows manage high-level research logic: problem formulation, experiment design, execution, analysis, and reporting.

### Assurance Layer
The critical innovation. Addresses the key failure mode: [[plausible-unsupported-success]].

## The Core Failure Mode: Plausible Unsupported Success

An autonomous research agent may claim a result is achieved (e.g., "accuracy improved by 5%") without the claim actually being verified by the evidence. The result *sounds* correct and is *plausible*, but the evidence chain is broken.

This is analogous to defection in a [[social-dilemmas|social dilemma]] — the agent optimizes for the appearance of success (individual payoff) rather than actual scientific validity (collective welfare).

## Cross-Family Adversarial Review

The defense: pair an **executor** from one LLM family with a **reviewer** from a different family. Example: Claude executes, Gemini reviews.

Why cross-family? Models from the same family share failure modes and blind spots. A same-family reviewer may ratify fabricated results that it would itself produce. A cross-family reviewer is more likely to catch errors the executor made.

This is a practical implementation of the adversarial collaboration principle from mechanism design: the reviewer's incentives are structurally opposed to the executor's errors.

## Evidence-to-Claim Audit Cascade

Three-stage audit:
1. **Claim extraction** — identify all factual claims in the report
2. **Evidence matching** — link each claim to a logged experimental result
3. **Gap flagging** — any claim without a matched evidence entry is flagged

This mirrors the role of [[cooperation-mechanisms|contracting]] in social systems: explicit, verifiable commitments that can be audited.

## Persistent Research Wiki

ARIS maintains a persistent knowledge base across runs with four entity types: concepts, experiments, results, hypotheses. This prevents the agent from "forgetting" validated findings and re-exploring solved problems.

## Related pages

- [[plausible-unsupported-success]]
- [[cooperation-mechanisms]]
- [[social-dilemmas]]
