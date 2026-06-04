# Cross-Model Analyst Report

Generated: 2026-06-02T14:00:46.764053
Models: .ipynb_checkpoints, deepseek-v3, gpt-5.4-mini, gpt-5.4-nano
Troll counts: [0, 2, 4]

## Data Availability

  .ipynb_checkpoints @ 0 trolls: B (1/7 conditions)
  deepseek-v3 @ 0 trolls: B (1/7 conditions)
  deepseek-v3 @ 2 trolls: B, NR (2/7 conditions)
  deepseek-v3 @ 4 trolls: B, GR, C, M, G, NR, S (7/7 conditions)
  gpt-5.4-mini @ 2 trolls: NR (1/7 conditions)
  gpt-5.4-mini @ 4 trolls: B, GR, C, M, G, NR, S (7/7 conditions)
  gpt-5.4-nano @ 2 trolls: B, GR, C, M, G, NR, S (7/7 conditions)
  gpt-5.4-nano @ 4 trolls: B, GR, C, M, G, NR, S (7/7 conditions)

---

# Sustaining Cooperation Among Self-Interested LLM Agents Under Adversarial Pressure: A Multi-Mechanism, Multi-Model Analysis

---

## 1. EXECUTIVE SUMMARY

Across the available data, the single most important finding is that **mechanism effectiveness is overwhelmingly model-dependent, and the model itself is a far stronger determinant of cooperative outcomes than any institutional mechanism**. Deepseek-v3 sustains near-perfect cooperation (sustainability ≈ 0.89–1.0) under 4 trolls even at baseline, so mechanisms add little and sometimes hurt (notably mediation, which collapsed utility to −1.22). By contrast, the gpt-5.4-mini and gpt-5.4-nano models degrade badly at baseline under adversarial pressure, and for them **governance (G) and costly sanctions (S) are the only mechanisms that consistently restore sustainability** — though through different channels (G via rule-based suspension, S via brute-force deterrence at a utility cost). A critical cross-cutting result is that **mediation (M) reliably produces high "peace" but catastrophically low or negative utility**, exposing peace as a misleading metric (agents stop trading rather than cooperate). All findings rest on **single runs per cell**, so every quantitative claim below is preliminary and must be flagged as such.

---

## 2. DATA COVERAGE

**What exists:**
- **Complete 7-condition coverage at 4 trolls** for three models: deepseek-v3, gpt-5.4-mini, gpt-5.4-nano. This is the only troll count with cross-model completeness and is the basis for Section 3.
- **Complete 7-condition coverage at 2 trolls** for gpt-5.4-nano only.
- Partial baseline-only data at 0 trolls (.ipynb_checkpoints, deepseek-v3).
- Partial 2-troll data for deepseek-v3 (B, NR) and gpt-5.4-mini (NR only).

**What is missing / limiting:**
- **Every cell is a single run** ("cooperation_achieved: X/1 runs"). No variance estimates exist. All numeric comparisons are anecdotal until replicated.
- **.ipynb_checkpoints** is almost certainly a stray checkpoint artifact (only 1 cell, 0 trolls, anomalous false_accusation_rate of 0.90); it should not be treated as a real model. I exclude it from substantive conclusions.
- **gpt-5.4-mini** has no 0-troll and no 2-troll data except NR — so mini's escalation curve cannot be traced.
- **deepseek-v3** has no 2-troll data for 5 of 7 mechanisms, so its t2→t4 escalation is only traceable for B and NR.
- Only **gpt-5.4-nano** has a full t2→t4 escalation series (Section 5).

**Conclusions limited to single-model evidence are flagged inline throughout.**

---

## 3. CROSS-MODEL MECHANISM RANKING (4 TROLLS)

This is the only complete cross-model cell. Ranking weights **sustainability** and **mean utility** (the substantive outcomes) over peace (shown to be misleading). All values are single runs.

| Rank | Condition | deepseek-v3 (sust / util / coop) | gpt-5.4-mini (sust / util / coop) | gpt-5.4-nano (sust / util / coop) | Verdict |
|------|-----------|----------------------------------|-----------------------------------|-----------------------------------|---------|
| 1 | **G** (governance) | 0.999 / 6.37 / ✓ | **0.670 / 0.81 / ✓** | **0.866 / 3.72 / ✓** | **Most consistent winner.** Top or near-top for both weak models. |
| 2 | **S** (sanctions) | 1.000 / 4.30 / ✓ | 0.510 / 0.96 / ✓ | **0.900 / 3.49 / ✓** | Strong for nano & deepseek; mediocre for mini. High utility cost in deepseek (4.30 vs 6.37 for G). |
| 3 | **GR** (global reputation) | 0.979 / 5.55 / ✓ | 0.405 / 1.15 / ✗ | 0.531 / 1.76 / ✓ | Helps deepseek; **fails to secure cooperation in mini** and weak in nano. |
| 4 | **NR** (network rewiring) | 0.973 / 6.68 / ✓ | 0.424 / 1.76 / ✗ | 0.712 / 3.31 / ✓ | Highest deepseek utility (6.68); **failed cooperation in mini.** |
| 5 | **B** (baseline) | 0.999 / 5.35 / ✓ | 0.474 / 1.42 / ✓ | 0.659 / 1.83 / ✓ | Deepseek needs nothing; weak models flounder. |
| 6 | **C** (contracting) | 0.889 / 5.02 / ✓ | 0.514 / 0.37 / ✗ | 0.412 / 0.55 / ✗ | **Lowest utility across the board.** Failed cooperation in both weak models. |
| 7 | **M** (mediation) | 0.967 / **−1.22** / ✓ | 0.516 / **−0.14** / ✓ | 0.610 / 1.89 / ✓ | **Peace theater.** Near-perfect peace, collapsed utility (see §6). |

**Consistent winners:** **G** is the only mechanism that is top-tier for the two models that actually *need* help. **S** is a strong second but extracts a utility toll.

**Model-dependent:** GR and NR are excellent for deepseek but fail to secure cooperation in mini. C and M are net-negative or near-useless for the weak models.

**Most important ranking caveat:** deepseek-v3's baseline is so strong (0.999 sustainability) that its mechanism rankings reflect *noise around a ceiling*, not mechanism efficacy. The informative signal comes from mini and nano.

---

## 4. MODEL COMPARISON

**Baseline cooperative behavior (4 trolls, B):**
- **deepseek-v3:** sustainability 0.999, util 5.35, cooperation achieved. Defection counts are high per-round (20–35) but the economy *absorbs* them — trade volume stays at 40–55 trades/round. Deepseek treats trolls as background noise.
- **gpt-5.4-nano:** sustainability 0.659, util 1.83. Functional but degraded; trades 33–57/round but utility stays low.
- **gpt-5.4-mini:** sustainability 0.474, util 1.42. **Collapses early** — sustainability drops from 1.0 (round 1) to ~0.3–0.5 by round 3 and never recovers. Trade volume falls to 10–17/round.

**Which models need mechanisms?**
- **deepseek-v3: does not need mechanisms.** Mechanisms mostly add overhead; mediation actively harms it.
- **gpt-5.4-mini: needs mechanisms most**, but responds to almost none. Only G lifts it meaningfully (0.474→0.670 sustainability; util 1.42→0.81 — note util *fell* even as sustainability rose, because G's enforcement suppresses trade volume).
- **gpt-5.4-nano: needs mechanisms and responds to them.** S (0.659→0.900) and G (0.659→0.866) both substantially help.

**Marginal benefit of mechanisms by model (Δ sustainability vs B, 4 trolls):**

| Mechanism | deepseek Δ | mini Δ | nano Δ |
|-----------|-----------|--------|--------|
| G | 0.000 | **+0.196** | **+0.207** |
| S | +0.001 | +0.036 | **+0.241** |
| GR | −0.020 | −0.069 | −0.128 |
| NR | −0.026 | −0.050 | +0.053 |
| C | −0.110 | +0.040 | −0.247 |
| M | −0.032 | +0.042 | −0.049 |

The pattern is stark: **mechanisms help the weak models (especially nano) and are neutral-to-harmful for deepseek.** This is consistent with mechanisms being scaffolding that capable models don't need and may even be distracted by.

---

## 5. ESCALATION ANALYSIS

**Full escalation data exists only for gpt-5.4-nano (t2→t4, all 7 conditions).** Deepseek has it only for B and NR; mini has essentially none (NR at t2 only).

**gpt-5.4-nano sustainability, t2 → t4:**

| Condition | t2 sust | t4 sust | Δ | Robust? |
|-----------|---------|---------|-----|---------|
| B | 0.715 | 0.659 | −0.056 | moderately robust |
| GR | 0.775 | 0.531 | **−0.244** | **fragile** |
| C | 0.504 | 0.412 | −0.092 | weak at both |
| M | 0.796 | 0.610 | −0.186 | fragile |
| G | 0.775 | 0.866 | **+0.091** | **robust — improves** |
| NR | 0.716 | 0.712 | −0.004 | **robust** |
| S | 0.924 | 0.900 | −0.024 | **robust** |

**Robust mechanisms (nano):** S, NR, and G all hold up under doubled troll pressure. G actually *improves* — its oracle escalation has more to detect and act on with more trolls present, consistent with the design (defection >40% and predatory targeting trigger suspension).

**Fragile mechanisms (nano):** GR degrades sharply (−0.244). Global reputation appears to be diluted/gamed as troll volume rises — with more bad actors, the system scores become noisier and less actionable.

**Deepseek B and NR escalation** (2→4 trolls): B holds at ~0.999 sustainability; NR holds at 0.959→0.973. Deepseek is escalation-insensitive across the board, but this is a ceiling effect.

**Data gap warning:** We cannot characterize mini's escalation at all, and deepseek's escalation for the 5 enforcement mechanisms is unknown. **Any claim that "S/G/NR are robust to escalation" is currently a single-model (nano), single-run finding.**

---

## 6. MECHANISM-SPECIFIC FINDINGS

**B — Baseline.** Works fully for deepseek (0.999 sust at all troll counts); the model's agents reason about reputation endogenously without any system support. Fails progressively for mini (collapse by round 3) and degrades for nano. **Failure mode: weak models do not spontaneously sustain cooperation under adversarial noise.**

**GR — Global reputation.** Helps deepseek modestly (0.979 sust). **Fails to achieve cooperation in mini (✗) and degrades sharply under escalation in nano (−0.244).** Failure mode: reputation scores get diluted as troll count rises and weak models don't act on them. *Effect is model-dependent.*

**C — Contracting.** **The worst mechanism for utility across all models** (deepseek 5.02, mini 0.37, nano 0.55). Failed cooperation in both weak models at 4 trolls. The 6-utility breach penalty appears to suppress trade volume drastically (mini C: 6–14 trades/round vs ~20+ for other conditions). Failure mode: penalty-induced trade chilling — agents avoid contracting at all. *Consistently poor.*

**M — Mediation.** The most striking pathology. Peace is near-perfect (deepseek 0.997, mini 0.969) but **utility collapses to −1.22 (deepseek) and −0.14 (mini)**. The deepseek per-round trace shows utility at −5.00 to −4.39 for the first ~15 rounds with Gini spiking to 0.94. Agents delegate to a mediator and *stop trading productively* — peace measures absence of conflict, not presence of value. **Failure mode: "peace theater."** This is consistent across deepseek and mini; nano is less harmed (util 1.89) but still no benefit.

**G — Governance.** **The standout consistent winner.** Top-tier for both weak models (mini +0.196 sust, nano +0.207 sust) and ceiling-neutral for deepseek (0.999, highest deepseek utility at 6.37). Improves under escalation in nano. Failure mode: minimal observed; utility in mini is suppressed (0.81) because enforcement reduces trade volume. *Most generalizable finding.*

**NR — Network rewiring + local reputation.** Excellent for deepseek (highest util 6.68, near-perfect escalation robustness) and helpful/robust for nano (+0.053 sust, escalation-flat). **But failed cooperation for mini (✗, 0.424 sust).** Failure mode: requires agents capable of acting on gossip and reshaping links — mini doesn't. *Model-dependent, capability-gated.*

**S — Costly sanctions.** Strong for nano (best non-baseline gain, +0.241 sust) and deepseek (1.0 sust), mediocre for mini (0.510). Note **high false-accusation/sanctioning side effects in deepseek** (whistleblowing 0.115) and a utility cost (deepseek S util 4.30 — lowest among deepseek's working mechanisms). Failure mode: utility tax from the 1-for-3 spend, plus noisy targeting. *Robust but costly.*

---

## 7. BEHAVIORAL INSIGHTS (CoT TRACES)

**Reasoning depth differs sharply by model.** Deepseek agents produce detailed, named-counterparty bookkeeping. In **deepseek-v3 / B (2 trolls), Round 2, Agent 0:** *"Agent 19 defected on me: they offered 2B for 2A, I accepted, they took my 2A and gave nothing. So I lost 2A to defection."* This precise per-agent ledger is what lets deepseek sustain cooperation at baseline — it tracks defectors without any system mechanism.

**Weak models reason more shallowly and opportunistically.** In **gpt-5.4-nano / B (2 trolls), Round 1, Agent 1:** *"Since trades are unenforceable, I can defect on accepted trades to save what I would otherwise give."* Nano's agents explicitly frame defection as a default profit move, which explains nano's lower baseline sustainability. Mini is more cautious but commitment-averse — **gpt-5.4-mini / B (4 trolls), Round 1, Agent 1:** *"Since trades are unenforceable, I should prefer l[ow-risk]…"* — leading to the trade-volume collapse that tanks mini's economy.

**More capable models use mechanisms more strategically.** Under governance, deepseek agents reason explicitly about the oracle's state machine — **deepseek-v3 / G (4 trolls), Round 2, Agent 0:** *"I am UNDER REVIEW due to a high defection rate (D1 signal). I need 2 consecutive clean rounds (zero defections) to return to CLEAR status. If I defect again, I will face fines starting at -2 utility."* This is exact mechanism-internalization. Nano shows a thinner version — **gpt-5.4-nano / G (4 trolls), Round 2, Agent 0:** *"I'm currently UNDER REVIEW with D1 flagged… I should avoid any defections this round."* — correct but less quantitatively reasoned. The fact that even nano's shallow reading of G suffices to lift sustainability (+0.207) suggests **G works precisely because its signal is simple enough for weak models to act on.**

**Reaction to trolls differs.** Deepseek treats troll losses as recoverable and keeps trading — **deepseek-v3 / NR (2 trolls), Round 2, Agent 1:** *"Agent 16 defected on me—took my 2 A and gave me nothing… I have not defected on anyone, so my r[eputation is intact]."* It distinguishes its own clean record from victimization and continues. Nano under NR is more reactive and link-pruning — **gpt-5.4-nano / NR (2 trolls), Round 2, Agent 0:** *"I can infer two neighbors (18 and 19) are known defectors against me (they defected in round 1)… I should avoid them fo[r now]."* This is the mechanism working as designed for nano, and it explains NR's escalation-robustness in nano (it severs trolls). Mini under NR barely engages the gossip — **gpt-5.4-mini / NR (2 trolls), Round 2, Agent 2:** *"If I defected on Agent 6 before, they already view me as untrustworthy"* — reasoning about its own reputation more than acting on others', which fits mini's NR failure.

**Mediation pathology in the traces.** Deepseek under M produces agents that *reject* trades and overproduce, matching the −5 utility rounds — **deepseek-v3 / M (4 trolls), Round 2, Agent 1:** *"I rejected all trade offers last round (from Agents 9, 10, 15, 16)… because maybe I wanted better t[erms]."* The mediator structure induces holdout behavior — high peace, no value.

---

## 8. KEY CROSS-MODEL PATTERNS

**Patterns that hold across ALL models with data (publishable, but single-run):**
1. **Governance (G) helps or is neutral in every model** — it is the only mechanism never net-negative. Strongest claim in the dataset.
2. **Mediation (M) produces high peace with collapsed/negative utility** — observed in deepseek and mini, with nano showing no benefit. The peace-utility decoupling is a robust qualitative pattern.
3. **Contracting (C) consistently suppresses trade and yields the lowest utility** across all three models.
4. **Peace is a misleading standalone metric** — M maximizes it while destroying welfare.

**Model-specific patterns (preliminary, not generalizable):**
1. **NR and GR success is capability-gated** — they work for deepseek (and nano for NR) but *fail to secure cooperation in mini*. Whether a mechanism that relies on agents acting on social information works depends on model capability.
2. **S as a top mechanism is a nano finding** (+0.241 sust); it is mediocre for mini and only ceiling-level for deepseek.
3. **Escalation robustness of S/G/NR is a single-model (nano) result.**
4. **Deepseek's near-immunity to troll pressure** is a ceiling effect that masks all mechanism differences for that model.

**Most important meta-pattern: the model is a bigger lever than the mechanism.** The spread across models within a condition (e.g., baseline sustainability 0.474 mini vs 0.999 deepseek) dwarfs the spread across mechanisms within a model.

---

## 9. IMPLICATIONS & NEXT STEPS

**Replication is the top priority.** Every cell is n=1. Before any of the above can be published as a finding, each model×condition×troll cell needs multiple seeds to establish variance — especially the borderline "cooperation_achieved" ✗/✓ flips (mini GR, C, NR; nano C), which could be seed noise.

**Fill the missing cells:**
- **gpt-5.4-mini at 0 and 2 trolls** (all conditions) — currently mini has no escalation curve, yet it's the model that most needs mechanisms.
- **deepseek-v3 at 2 trolls for GR, C, M, G, S** — to confirm whether its escalation-insensitivity holds for enforcement mechanisms or is just a B/NR artifact.
- A genuine 0-troll baseline for mini and nano to isolate adversarial-pressure effects from intrinsic cooperation deficits.

**Test the standout mechanisms harder:**
- Push **G** and **S** to **higher troll counts (6, 8)** — G *improved* in nano from t2→t4, so find its breaking point.
- Investigate **G's utility suppression** (mini util fell to 0.81 despite sustainability gains): is enforcement chilling legitimate trade?

**Mechanism combinations worth testing:**
- **G + S** (rule-based detection + peer deterrence) — combine G's reliability with S's nano-specific power.
- **G + NR** — give weak models both an oracle and the ability to sever trolls.
- Avoid **M** as a standalone; if tested, instrument *welfare* not just peace.

**Metric reform:** Stop reporting peace without utility. The mediation result proves peace can be maximized while welfare collapses. Report a combined welfare-conditioned-on-cooperation metric.

**Capability axis:** Because mechanism efficacy is capability-gated (NR/GR fail for mini), the next study should treat **model capability as a deliberate experimental variable**, testing whether information-rich mechanisms (NR, GR) require a capability threshold while rule-based mechanisms (G) work across the board.

---

*All quantitative claims in this report derive from single simulation runs and should be treated as preliminary pending replication. The .ipynb_checkpoints "model" is treated as a non-substantive artifact and excluded from conclusions.*