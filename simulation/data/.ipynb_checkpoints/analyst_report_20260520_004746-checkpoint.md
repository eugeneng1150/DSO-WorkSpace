# Analyst Report

Generated: 2026-05-20T00:47:46.591254

# Findings Report: Multi-Agent Marketplace Simulation

---

## 1. Which Conditions Achieved Marketplace Cooperation?

**No condition achieved marketplace cooperation.** All eight conditions report a `marketplace_cooperation_rate` of 0.0, meaning that across all 40 sessions (8 conditions × 5 runs), not a single session ended with both final-round Sustainability > 0.5 and final-round Peace > 0.5.

Examining the final-round values reveals why:

| Condition | Final Sustainability | Final Peace | Sustainability > 0.5? | Peace > 0.5? |
|-----------|---------------------|-------------|------------------------|--------------|
| B         | 0.5232              | 0.3416      | ✓ (barely)             | ✗            |
| R         | 0.7182              | 0.2615      | ✓                      | ✗            |
| C         | 0.6237              | 0.2552      | ✓                      | ✗            |
| M         | 0.5541              | 0.1281      | ✓                      | ✗            |
| RC        | 0.7324              | 0.2782      | ✓                      | ✗            |
| RM        | 0.7605              | 0.2083      | ✓                      | ✗            |
| CM        | 0.6292              | 0.2366      | ✓                      | ✗            |
| RCM       | 0.7590              | 0.1618      | ✓                      | ✗            |

**The binding constraint is universally Peace, not Sustainability.** Every condition clears the Sustainability threshold (most comfortably), but no condition comes close to the Peace threshold of 0.5 in the final round. The best final Peace is the baseline (0.3416), and the worst is Mediation alone (0.1281). This is a striking and counterintuitive result: every mechanism and combination *worsens* final-round Peace relative to baseline.

---

## 2. Which Single Mechanism Was Most Effective?

Comparing R, C, and M against baseline B across key metrics:

### Sustainability (mean / final)
| Condition | Mean  | Final  | Δ vs B (final) |
|-----------|-------|--------|-----------------|
| B         | 0.638 | 0.523  | —               |
| R         | 0.765 | 0.718  | +0.195          |
| C         | 0.756 | 0.624  | +0.101          |
| M         | 0.741 | 0.554  | +0.031          |

**Reputation (R) is the most effective single mechanism for Sustainability**, lifting the final value by ~19.5 percentage points over baseline.

### Peace (mean / final)
| Condition | Mean  | Final  | Δ vs B (final) |
|-----------|-------|--------|-----------------|
| B         | 0.641 | 0.342  | —               |
| R         | 0.535 | 0.262  | −0.080          |
| C         | 0.300 | 0.255  | −0.087          |
| M         | 0.233 | 0.128  | −0.214          |

**No single mechanism improves Peace.** All three worsen it relative to baseline, both on average and in the final round. Mediation is the worst performer, with final Peace dropping to 0.128 — a 21.4 pp decline from baseline.

### Total Defections
| Condition | Total Defections | Δ vs B |
|-----------|-----------------|--------|
| B         | 715             | —      |
| R         | 915             | +200   |
| C         | 1,838           | +1,123 |
| M         | 2,065           | +1,350 |

This is deeply counterintuitive: **all three mechanisms increase total defections relative to baseline.** Contracting and Mediation roughly triple defection counts. Reputation increases defections by ~28%.

### Verdict
**Reputation (R) is the best single mechanism**, but only on the Sustainability dimension. It maintains production levels effectively (final 0.718 vs. baseline 0.523) while being the least harmful to Peace among the three mechanisms. However, it still fails the cooperation threshold and actually increases total defections.

---

## 3. Do Mechanism Combinations Outperform Single Mechanisms?

### Sustainability (final round)

| Combination | Final Sust. | Best Component | Component Final | Improvement? |
|-------------|-------------|----------------|-----------------|--------------|
| RC          | 0.732       | R              | 0.718           | Marginal (+0.014) |
| RM          | 0.761       | R              | 0.718           | Yes (+0.043)  |
| CM          | 0.629       | C              | 0.624           | Marginal (+0.005) |
| RCM         | 0.759       | R              | 0.718           | Yes (+0.041)  |

RM and RCM show modest Sustainability gains over R alone. The improvement from RM to RCM is negligible (+0.002 → −0.002), suggesting Contracting adds nothing to the RM combination for Sustainability.

### Peace (final round)

| Combination | Final Peace | Best Component | Component Final | Improvement? |
|-------------|-------------|----------------|-----------------|--------------|
| RC          | 0.278       | R              | 0.262           | Marginal (+0.016) |
| RM          | 0.208       | R              | 0.262           | **Worse** (−0.054) |
| CM          | 0.237       | C              | 0.255           | **Worse** (−0.018) |
| RCM         | 0.162       | R              | 0.262           | **Worse** (−0.100) |

**Combinations generally do not improve Peace and often worsen it.** The full combination RCM produces the *worst* final Peace of any condition (0.162), a full 18 pp below baseline. Adding mechanisms appears to compound the Peace-degrading effect rather than mitigate it.

### Total Defections

| Combination | Defections | Best Component | Component Defections | Improvement? |
|-------------|-----------|----------------|---------------------|--------------|
| RC          | 836       | R (915)        | 915                 | Yes (−79)    |
| RM          | 795       | R (915)        | 915                 | Yes (−120)   |
| CM          | 1,952     | C (1,838)      | 1,838               | **Worse** (+114) |
| RCM         | 879       | R (915)        | 915                 | Yes (−36)    |

Reputation-containing combinations (RC, RM, RCM) reduce defections relative to their non-R components, but only RM and RC bring defections close to baseline levels. CM without R is essentially as bad as its worst component.

### Verdict
**Combinations show marginal or no improvement over the best single mechanism (R).** The pattern is clear: Reputation drives whatever gains exist, and adding C and/or M provides at best marginal Sustainability improvement while often degrading Peace. The full RCM combination is notably the worst performer on final Peace despite having the highest Sustainability.

---

## 4. What Is the Minimum Sufficient Mechanism Set?

**No mechanism set tested is sufficient to achieve marketplace cooperation.** The question of "minimum sufficient" cannot be answered because the sufficiency threshold is never met.

If we relax the question to "which mechanism set comes closest to cooperation," we can examine the joint distance from the (0.5, 0.5) threshold:

| Condition | Final Sust. | Final Peace | Sust. Surplus | Peace Deficit |
|-----------|-------------|-------------|---------------|---------------|
| B         | 0.523       | 0.342       | +0.023        | −0.158        |
| R         | 0.718       | 0.262       | +0.218        | −0.238        |
| RC        | 0.732       | 0.278       | +0.232        | −0.222        |
| RM        | 0.761       | 0.208       | +0.261        | −0.292        |
| RCM       | 0.759       | 0.162       | +0.259        | −0.338        |

**Paradoxically, the baseline (B) has the smallest Peace deficit** (−0.158), though it barely clears Sustainability. The mechanisms trade Peace for Sustainability, and no combination achieves a favorable balance.

If forced to recommend, **Reputation alone (R)** offers the best cost-benefit: it substantially improves Sustainability (+19.5 pp) with a moderate Peace penalty (−8 pp). But it remains insufficient.

---

## 5. Intermediate Variable Analysis

### 5.1 Whistleblowing Rate

| Condition | Mean WB Rate | Final WB Rate |
|-----------|-------------|---------------|
| B         | 0.0205      | 0.0251        |
| R         | 0.0040      | 0.0023        |
| C         | 0.0004      | 0.0009        |
| M         | 0.0007      | 0.0012        |
| RC        | 0.0086      | 0.0031        |
| RM        | 0.0000      | 0.0000        |
| CM        | 0.0018      | 0.0009        |
| RCM       | 0.0003      | 0.0010        |

**The baseline has the highest whistleblowing rate** (mean 0.0205, final 0.0251). Every mechanism *suppresses* whistleblowing rather than enhancing it. RM completely eliminates it (0.0 across all rounds). This suggests that formal mechanisms may crowd out informal information sharing — agents may rely on the mechanism rather than broadcasting warnings, or the mechanisms may alter agent behavior in ways that reduce the perceived need or incentive to whistleblow.

However, even baseline whistleblowing is extremely low (2% of defections result in warnings), so this channel is largely inactive across all conditions.

### 5.2 False Accusation Rate

| Condition | Mean FAR | Final FAR |
|-----------|----------|-----------|
| B         | 0.277    | 0.200     |
| R         | 0.107    | 0.000     |
| All others| 0.000–0.040 | 0.000  |

The baseline has the highest false accusation rate (27.7% mean), and Reputation reduces it substantially (10.7% mean, 0% final). All other conditions effectively eliminate false accusations — but this is likely because they also eliminate nearly all public negative mentions (the denominator), not because accusations become more accurate.

### 5.3 Warning Accuracy

| Condition | Mean Accuracy | Final Accuracy |
|-----------|--------------|----------------|
| B         | 0.041        | 0.180          |
| R         | 0.007        | 0.200          |
| All others| 0.000        | 0.000          |

Warning accuracy is near zero across all conditions. Only B and R show any non-zero values, and these are based on extremely small sample sizes (given the low whistleblowing rates). **The information propagation channel is essentially non-functional across all conditions.**

### 5.4 Mechanism Pathway Summary

The mechanisms did **not** work through improved information propagation. Whistleblowing, false accusation reduction, and warning accuracy are all negligible or suppressed by the mechanisms.

Did they work through direct defection reduction? **No — defections increased** under every mechanism relative to baseline. The Sustainability improvements under R-containing conditions appear to operate through a different channel: agents may maintain production despite defections, possibly because reputation tracking allows them to selectively trade with more reliable partners, preserving productive capacity even as overall defection rates rise.

The Peace metric's decline suggests that while agents may sustain production, the *proportion* of cooperative trades deteriorates — potentially because mechanisms encourage more trading attempts (including with unreliable partners), increasing the denominator of defection-prone interactions.

---

## 6. Unexpected Patterns and Anomalies

### 6.1 All Mechanisms Increase Defections
This is the most striking anomaly. Contracting (C) nearly triples defections (1,838 vs. 715), and Mediation (M) nearly triples them as well (2,065 vs. 715). Even Reputation increases defections by 28%. **Formal mechanisms appear to enable or encourage defection rather than deterring it.** Possible explanations:
- Mechanisms may increase the volume of trade (more interactions = more opportunities to defect)
- Agents may perceive mechanisms as a safety net and take more risks
- Contracting and mediation may create exploitable loopholes
- The mechanisms may not impose sufficiently costly penalties

### 6.2 Baseline Has the Best Final Peace
The condition with no mechanisms (B, final Peace 0.342) outperforms every mechanism condition on Peace. This suggests that informal social norms or the threat of unstructured retaliation may be more effective at deterring defection than formal mechanisms.

### 6.3 RCM Has the Worst Final Peace
The full mechanism combination (RCM, final Peace 0.162) produces the worst Peace outcome — worse than any single mechanism or partial combination. This suggests **negative interaction effects** between mechanisms. The combination may create complexity that agents exploit, or the mechanisms may work at cross-purposes (e.g., mediation may undermine reputation-based punishment by offering "forgiveness" pathways).

### 6.4 Sustainability-Peace Tradeoff
There is a clear negative correlation between final Sustainability and final Peace across conditions. Conditions with high Sustainability (RM: 0.761, RCM: 0.759) have low Peace (0.208, 0.162), while the baseline has the lowest Sustainability (0.523) but highest Peace (0.342). This suggests a structural tradeoff: mechanisms that keep production going may do so by enabling continued trading despite rampant defection, rather than by reducing defection.

### 6.5 Contracting and Mediation Suppress Information Sharing
C and M conditions show near-zero whistleblowing, false accusation, and warning accuracy rates. These mechanisms appear to substitute formal dispute resolution for informal reputation management, but the formal channels are apparently ineffective at deterring defection.

### 6.6 High Variance in Baseline Peace
Baseline Peace has the highest standard deviation (0.1808), suggesting that without mechanisms, outcomes are highly path-dependent. Some baseline sessions may have achieved relatively cooperative equilibria while others collapsed. The mechanisms reduce variance (C: 0.1178, M: 0.1115) but at a lower mean — they consistently produce poor Peace outcomes rather than occasionally good ones.

### 6.7 Reputation Reduces Variance in Sustainability
R has the lowest Sustainability std (0.1129 among single mechanisms, though RCM is 0.1052). Reputation appears to stabilize production even if it doesn't stabilize cooperation.

---

## 7. Implications for the Research Question

**Research Question:** *Which formal mechanism (or combination) allows self-interested agents to maintain marketplace cooperation in a repeated trading environment?*

### Primary Finding
**None of the tested mechanisms — individually or in combination — achieves marketplace cooperation as defined.** The 0% cooperation rate across all 40 sessions is a definitive negative result.

### Secondary Findings

1. **Reputation is the only mechanism with clear positive effects**, but only on Sustainability (production maintenance). It improves final Sustainability by ~19.5 pp over baseline while being the least harmful to Peace. However, it still fails the Peace threshold by a wide margin.

2. **Formal mechanisms paradoxically increase defection.** This is the study's most important finding. Contracting and Mediation — mechanisms designed to enforce cooperation — roughly triple defection counts. This suggests that in LLM agent populations, formal enforcement mechanisms may be gamed, exploited, or may create moral hazard.

3. **Mechanism combinations show diminishing or negative returns.** Adding mechanisms beyond Reputation provides marginal Sustainability gains at substantial Peace costs. The full RCM combination produces the worst Peace outcome, suggesting negative interaction effects.

4. **Information propagation channels are non-functional.** Whistleblowing rates are negligible across all conditions (≤2.5%), and mechanisms suppress rather than enhance them. The theoretical pathway from mechanisms → better information → better partner selection → less defection does not operate in this simulation.

5. **The Sustainability-Peace tradeoff suggests a structural problem.** Mechanisms may keep markets "alive" (high production) while allowing them to become increasingly exploitative (high defection). This is a form of institutional failure where the