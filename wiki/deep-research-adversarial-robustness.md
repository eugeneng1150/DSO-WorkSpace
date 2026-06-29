# Deep Research: Adversarial Robustness of Multi-Agent LLM Cooperation

**Summary**: Fact-checked survey of 2025–2026 academic work on adversarial robustness, mechanism design, and disinformation defenses in multi-agent LLM systems. 25 claims verified, 8 confirmed, 17 killed.

**Sources**: arXiv:2605.09076, arXiv:2502.14847 (ACL 2025), arXiv:2507.14928v1, arXiv:2601.11369v2, arXiv:2605.08426, arXiv:2505.19212, arXiv:2507.04105

**Last updated**: 2026-06-28

---

## Research Context

Generated to inform next steps for a multi-agent marketplace simulation comparing 8 institutional cooperation mechanisms under progressive adversarial stress from LLM-driven troll agents. [[mediation]] was found to be the best-performing mechanism; a RAPOA-inspired prompt optimizer (v1–v6) red-teamed it.

**Stats**: 6 search angles · 28 sources fetched · 132 claims extracted · 25 verified · 8 confirmed · 17 killed

---

## Confirmed Findings

### Finding 1 — Static governance constraints backfire (HIGH confidence)
Sources: arXiv:2601.11369v2, arXiv:2605.08426

Prompt-level constitutional anti-collusion constraints yield no reliable improvement over ungoverned baselines (mean tier 3.02 ± 1.05 vs 3.10 ± 1.06, N=90 runs). Enforced Code Contracts in GovSimContract reduce total gain vs. no-contract baseline by −27.7 ± 21.5 (p=0.019) due to over-prudent caps — even though prosocial agents otherwise outperform selfish agents by +119.6.

**Failure mode**: Rigid constraints hurt cooperative agents more than defectors.

**Implication**: Do not layer more prompt-level or contract-level constraints on top of [[cooperation-mechanisms|Mediation]]. Consistent with the M+GR result where GR's peacetime cost dragged down overall performance.

See also: [[institutional-governance]], [[institutional-ai-collusion]]

---

### Finding 2 — One Byzantine agent collapses consensus; SAC fixes it (HIGH confidence)
Source: arXiv:2605.09076

A single Byzantine agent broadcasting falsified confidence scores of 1.0 collapses CP-WBFT across all topologies (BFTI −10.4% to −54.7% on MATH500) even when honest agents are 6-of-7. Receiver-side scoring (SAC) recovers positive fault tolerance: BFTI +3.8% to +7.6%.

**SAC mechanism**: Credibility is computed by the *receiver* from the message content, not self-reported by the sender. "Sender-agnostic" because it does not depend on anything the sender claims about itself.

**Difference from GR**:
- [[adversarial-agents|Global Reputation (GR)]] answers: "Is this agent trustworthy overall?" (identity-level, gameable by behaving well early)
- SAC answers: "Is this specific factual claim in this message true?" (claim-level, grounded in verifiable content)

**Implication**: If Mediation uses any self-reported trust signals, replacing them with receiver-computed credibility is an empirically validated high-priority defense. For the marketplace simulation: mediator cross-checks cited trades against the public ledger before passing messages to recipients. A troll claiming "Agent 5 defected in Round 54" is flagged if Round 54 shows no such defection.

---

### Finding 3 — Agent-in-the-Middle achieves 70–97% attack success (HIGH confidence)
Source: arXiv:2502.14847 (ACL 2025, peer-reviewed)

Exact ASRs from Table 1: AutoGen chain 95.2%/96.9% (HumanEval/MBPP), complete 96.3%/92.4%, Camel chain 97.6%/98.5%. Minimum across all conditions: ~40.7%.

The adversary does not compromise any agent's reasoning — it intercepts and modifies message passing between agents. This is orthogonal to agent-level defenses.

**Implication**: A troll injected into Mediation's message-passing layer could achieve near-total information control independent of how robust the mediation protocol is. Mediator ledger verification (Finding 2 defense) directly addresses the content-manipulation variant. Full channel interception would require cryptographic message authentication.

See also: [[adversarial-agents]]

---

### Finding 4 — BRB + Geometric Median tolerates up to ⌊(n-1)/2⌋ Byzantine agents (MEDIUM confidence)
Source: arXiv:2507.14928v1 (preprint)

Byzantine Reliable Broadcast + Geometric Median aggregation fault tolerance is strictly more permissive than Krum (⌊(n-2)/2⌋) or Bulyan (⌊(n-3)/4⌋) when adversaries collude to assign max scores to Byzantine workers and zero to honest ones.

At 47% trolls in Phase 4 of the progressive injection schedule, this directly applies to mediator revote aggregation. Simple majority breaks at ~33% adversarial agents; BRB+GM tolerates up to 49%.

**Confidence caveat**: Preprint, unreviewed. Empirical performance claims (71% MMLU-Pro) did not survive adversarial verification (1-2 vote). The fault-tolerance bounds themselves are mathematically grounded.

**Implication**: Supermajority voting in mediator revotes (GM aggregation) gives theoretically grounded resilience beyond Phase 3 troll levels.

---

### Finding 5 — LLM morality scores vary 10× across models (HIGH confidence)
Source: arXiv:2505.19212

GPT-4o-mini: 76.3%. Qwen-3-235B-A22B: 7.9%. Across 9 models in morally framed social dilemmas. DeepSeek-v3 is in the lower half of the morality-score range.

**Implication**: Mediation's observed superiority may be partially a DeepSeek-v3 artifact. Results should be reported disaggregated by model class. Testing across at least 3 models spanning the morality-score range is required for external validity claims.

---

### Finding 6 — Randomized smoothing provides formal certification radius per agent decision (MEDIUM confidence)
Source: arXiv:2507.04105

Certification radius: r = σ/2·(Ψ⁻¹(p_A) − Ψ⁻¹(p_B)) per agent decision.
Multi-hop attenuation: ‖δ_out,k‖ ≈ ‖δ₁‖ · ∏(1−Ψ(rᵢ/σ)).

**Confidence caveat**: Empirical 90.24% deviation reduction claim failed verification (1-2 vote). Formal apparatus is mathematically sound.

**Implication**: Certified radii can be computed for each of the 8 mechanisms under RAPOA-generated adversarial prompts, producing a rigorous comparison metric beyond empirical win-rates.

---

## Key Kills (Notable Refuted Claims)

| Claim | Vote | Why it matters |
|-------|------|----------------|
| ALIGN gossip framework consistently improves cooperation and resists malicious entrants | 0-3 | Conceptually sound for the reputation arm — failed on specifics |
| Structural governance (5-state graph + sanctions) reduces collusion 50%→5.6% | 1-2 | Insufficient evidence for exact numbers |
| Communication topology determines robustness (chain most vulnerable) | 0-3 | Plausible, not confirmed by data |
| SAC prevents Byzantine agents from inflating perceived reliability (mechanism claim) | 0-3 | The BFTI performance claim survived; the mechanistic explanation was too strong |
| Survival pressure systematically reduces moral behavior across all models | 0-3 | Not generalizable across model families as stated |

---

## Open Questions

1. Can SAC be operationalized within a natural-language Mediation protocol, or does it require structured numeric outputs?
2. Do BRB+GM aggregation and channel authentication compose additively, or does one defense create a new attack surface?
3. Is there a model-agnostic metric for institutional robustness, or must every mechanism be re-evaluated per model?
4. Can per-decision certification radius be lifted to a system-level certified cooperation floor?

---

## Actionable Next Steps

1. **SAC-style mediator ledger verification** — mediator cross-checks cited trade claims against public ledger before relaying messages (addresses Findings 2+3, kills v6's primary weapon)
2. **Supermajority revote** — replace simple majority in mediator revotes with GM aggregation (addresses Finding 4)
3. **Cross-model validation** — run 8-mechanism comparison on at least 2 more backbone models (addresses Finding 5, essential for write-up credibility)

---

## Related pages

- [[cooperation-mechanisms]]
- [[adversarial-agents]]
- [[institutional-governance]]
- [[reward-hacking]]
- [[marketplace-spec]]
