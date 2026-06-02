# Analyst Report — deepseek-v3

Generated: 2026-06-02T09:33:32.939790
Troll counts: [0, 2, 4]

# INSTITUTIONAL MECHANISMS FOR SUSTAINING LLM-AGENT COOPERATION UNDER ADVERSARIAL PRESSURE
## A Research Analysis Report

---

## 1. EXECUTIVE SUMMARY

Across all troll counts, **baseline cooperation proved remarkably robust** — even with zero formal mechanisms, sustainability stayed at or near 1.0 and cooperation was achieved in every run, suggesting LLM agents possess strong intrinsic cooperative priors. The most striking finding is that **adding mechanisms frequently *reduced* mean utility relative to baseline** (e.g., M collapsed to **−1.22**, S fell to **4.30**, C to **5.02** vs. baseline's **5.35** at 4 trolls), while only **Governance (G, 6.37)** and **Network Rewiring (NR, 6.68)** clearly beat baseline. **Global Reputation (GR) and Governance (G) were most effective at isolating trolls** (34 and 43 damaging trades, with G's last-half average dropping to 0.67), whereas information-rich NR paradoxically generated *more* troll damage in the 2-troll case (117 damaging trades) because rewiring encouraged aggressive trade-proposing. **Critical caveat: every cell is a single run (1/1), so all numerical comparisons are directional hypotheses, not statistically validated claims.**

---

## 2. MECHANISM RANKING

Ranked by overall effectiveness (weighting cooperation, mean utility, troll isolation, and equity), focused on the 4-troll stress test where mechanisms matter most:

| Rank | Cond | Coop Rate | Mean Util (4-troll) | Troll Isolation (damaging trades / last-half avg) | Verdict |
|------|------|-----------|---------------------|---------------------------------------------------|---------|
| 1 | **G** (Governance) | 1/1 | **6.37** | 43 / **0.67** | Best utility + sustainability 0.999, but false-accusation 1.0 is a red flag. |
| 2 | **NR** (Network Rewiring) | 1/1 | **6.68** | 27 / **0.13** | Highest utility & best late-game troll isolation; high whistleblowing churn. |
| 3 | **GR** (Global Reputation) | 1/1 | 5.55 | **34** / 1.47 | Cleanest isolation signal; modest utility; sustainability dipped to 0.944. |
| 4 | **B** (Baseline) | 1/1 | 5.35 | 97 / 3.73 | Surprisingly resilient default; poor troll containment late-game. |
| 5 | **C** (Contracting) | 1/1 | 5.02 | 29 / 0.87 | Good troll containment but suppressed trade volume crushed utility. |
| 6 | **S** (Costly Sanctions) | 1/1 | **4.30** | 66 / 1.33 | Sanction costs drained the commons; worst non-pathological utility. |
| 7 | **M** (Mediation) | 1/1 | **−1.22** | 45 / 1.0 | Catastrophic: peace 0.997 but agents hoarded, gini 0.63, negative utility. |

**Note:** NR's mean utility (6.68) technically exceeds G's (6.37), but G is ranked #1 for combining high utility with near-perfect sustainability (0.999 vs NR's 0.973) and superior equity stability. These are within-single-run differences and could easily reorder under replication.

---

## 3. ESCALATION ANALYSIS (0 → 2 → 4 trolls)

Data limitation: not all mechanisms were tested at all troll counts. **B** was tested at 0/2/4; **NR** at 2/4; **GR, C, M, G, S** only at 4. This severely limits trajectory analysis.

| Mechanism | 0 trolls | 2 trolls | 4 trolls | Trajectory |
|-----------|----------|----------|----------|------------|
| **B** | util 6.0, peace 0.65, FA* 0.65 | util 6.24, peace 0.70, FA 0.38 | util 5.35, peace 0.67, FA 0.067 | **Robust** — util declines gently; warning accuracy *rises* (0.011→0.66) as trolls give agents real signal. |
| **NR** | — | util 5.87, **117 damaging** | util 6.68, 27 damaging | **Improves under pressure** — more trolls → more rewiring → better late isolation (last-half 1.26→0.13). |
| **GR** | — | — | util 5.55, 34 damaging | Single point; sustainability 0.978, handled 4 trolls cleanly. |
| **C** | — | — | util 5.02, sustain 0.889 | Single point; lowest sustainability — penalties chilled trade. |
| **M** | — | — | util −1.22 | Single point; **catastrophic failure**. |
| **G** | — | — | util 6.37, sustain 0.999 | Single point; best combined profile. |
| **S** | — | — | util 4.30 | Single point; sanction tax dominated. |

*FA = false accusation rate

**Robust:** B (gentle degradation), NR (anti-fragile — improves). **Fragile:** M (total collapse), S (utility erosion), C (trade suppression).

**Key escalation insight for B:** As trolls increase, baseline agents get *better* at identifying real threats. Warning accuracy: 0.011 (0 trolls) → 0.151 (2 trolls) → **0.664 (4 trolls)**. False accusations correspondingly fell from 0.65 → 0.38 → **0.067**. With no real adversaries (0 trolls), agents accuse each other baselessly; trolls provide a genuine target that focuses social punishment.

---

## 4. TROLL RESILIENCE

**Damaging troll trades** (non-troll proposed → troll stole), 4-troll condition:

| Cond | Total Damaging | Last-Half Avg | Interpretation |
|------|---------------|---------------|----------------|
| NR | **27** | **0.13** | Best — links to trolls severed and stayed severed |
| C | 29 | 0.87 | Contracts deterred troll engagement |
| GR | 34 | 1.47 | Visible scores steered agents away |
| S | 66 | 1.33 | Sanctions didn't prevent initial victimization |
| G | 43 | **0.67** | Oracle suspension cut late damage |
| M | 45 | 1.0 | Mediator delegated trades *into* trolls |
| B | **97** | **3.73** | No memory mechanism → repeated victimization |

**Mechanisms that genuinely isolated trolls:** NR (severing), GR (reputation steering), G (suspension), C (contract avoidance). The last-half average is the cleaner metric — it measures whether agents *learned*. NR (0.13) and G (0.67) show real learning/isolation; baseline's **3.73** shows agents kept walking into the same trap.

**Why mechanisms failed despite information:**

- **The 2-troll NR paradox (117 damaging trades vs B's 42):** Network rewiring *encouraged* aggressive trade-proposing to many neighbors to find good links, which mechanically increased exposure to trolls (who "propose to all neighbors"). More information enabled more probing, which fed trolls. Note NR's defect/trade counts (e.g., Round 1: 23 defects across 55 trades) show high churn.
- **Baseline (97 damaging at 4 trolls):** Agents only see "last 5 rounds detail" + lifetime summary. With no gossip or scores, each agent must independently rediscover each troll — and with 4 trolls proposing to everyone, re-victimization recurs (last-half avg 3.73).
- **Sanctions (66 damaging):** S punishes *after* the fact but does nothing to prevent the initial proposing-to-troll behavior; the damaging trade still happens, then the sanction adds cost on top.

---

## 5. INFORMATION GRADIENT (B → NR → GR)

The gradient hypothesis (more info → better outcomes) is **not cleanly supported.**

**At 2 trolls:**
- B (least info): util **6.24**, 42 damaging trades, sustain 0.999
- NR (more info): util **5.87**, **117 damaging trades**, sustain 0.959

Here **more information produced worse outcomes** — NR underperformed baseline on every headline metric. The added affordances (rewiring, gossip) induced churn and exposure rather than protection.

**At 4 trolls:**
- B: util 5.35, 97 damaging, warning accuracy 0.664
- NR: util **6.68**, **27 damaging**, warning accuracy 0.044
- GR: util 5.55, 34 damaging, warning accuracy 0.535

Under heavier pressure, **NR's information finally paid off** — once enough trolls existed, severing links durably isolated them (best utility + best late isolation). GR's visible scores produced clean, low-variance isolation but only middling utility.

**Conclusion:** Information value is *non-monotonic and pressure-dependent.* Below a threshold of adversarial density, richer information mechanisms add coordination cost without commensurate benefit (NR @ 2 trolls). Above that threshold, structural information (NR's severable links) becomes valuable. Interestingly, **baseline agents extract surprisingly good warning accuracy (0.664) from private experience alone** at 4 trolls — exceeding both NR (0.044) and GR (0.535). With single runs, this could be noise, but it suggests private experience is a strong signal when adversaries are dense.

---

## 6. BEHAVIORAL INSIGHTS (from CoT traces)

**How agents decide to cooperate vs defect — the universal Round-1 reasoning:**

The cooperative default is explicit. B (0 trolls), Round 1, Agent 1:
> *"I could defect and take goods for free, but that would likely burn bridges with that partner and potentially others if word spreads via public [warnings]... Early defection could lead to public warnings and isolation."*

This reputation-anticipation logic appears even with no enforcement mechanism, explaining baseline's robustness.

**How agents react to troll encounters — accurate threat identification:**

B (2 trolls), Round 2, Agent 0:
> *"Agent 19 defected on me: they offered 2B for 2A, I accepted, they took my 2A and gave nothing... I should not trust them. I have not defected on anyone yet."*

B (4 trolls), Round 3, Agent 0 correctly enumerates multiple trolls:
> *"In Round 2, I was defected on by Agent 7 (1 of 2 trades), Agent 19 (2 of 2 trades), and Agent 20 (1 of 1 trade)."*

Agents track per-partner defection accurately — this is *why* warning accuracy rises to 0.664 at 4 trolls.

**Whether agents use mechanisms strategically:**

*Governance (G, 4 trolls), Round 2, Agent 0* — shows the oracle changing behavior:
> *"I am UNDER REVIEW by the regulator due to a high defection rate (D1 signal)... I need 2 consecutive clean rounds (zero defections) to return to CLEAR status. If I defect again, I will face fines starting at -2 utility."*

By Round 3 the same agent internalizes the penalty:
> *"I'm now under a Tier 1 penalty of -2 utility this round due to governance violations... I need 2 consecutive [clean rounds]."*

This is genuine strategic mechanism-use — and explains G's strong sustainability.

*NR (4 trolls), Round 3, Agent 0* — uses severing/local reputation explicitly:
> *"Reliable partners (0% defection): Agents 6, 7, 8, 12, 13, 14, 16. Defectors: Agent 19 (100% defection), Agent 20 (100% defection)... Agent 7 and 8 are not currently neighbors (I have no link to them)."*

This trace shows the rewiring mechanism functioning as intended — and explains NR's best-in-class late isolation (0.13).

**Mechanism *misuse* — Mediation's catastrophe:**

M (4 trolls), Round 2, Agent 1 reveals the failure mode — agents over-rejected and over-produced:
> *"I rejected all trade offers last round (from Agents 9, 10, 15, 16)... 1A (costs me 1) for 1B (gives +3) is net +2 utility per trade, which is good. I [shouldn't have rejected]."*

M, Round 3, Agent 0:
> *"Last round utility was -5, cumulative -10... I have not yet completed any trades (only rejected or been defected on)... holding 7 A is inefficient."*

Agents under mediation hoarded unsellable Good A, accumulating production debt (note M's negative AvgUtil through Round 19). The mediator delegation suppressed the very trading that generates utility — peace 0.997 but util −1.22 is the signature of a "peaceful graveyard."

**Behavior change 2-troll → 4-troll (NR):**

At 2 trolls, NR agents *themselves* defected opportunistically. NR (2 trolls), Round 3, Agent 1:
> *"In Round 2 I defected on several partners: I defected on Agent 15 (who had been reliable with me). I defected on Agent 17... I defected on Agent 13."*

This self-defection (contributing to NR's 117 damaging trades and high whistleblowing 0.78) contrasts with 4-troll NR, where agents focused on *severing trolls* rather than free-riding (Round 3, Agent 0 above carefully tracks reliable vs. defector partners). More adversaries shifted agent strategy from opportunism to defensive consolidation.

---

## 7. MECHANISM-SPECIFIC FINDINGS

**B (Baseline):** *Worked* — robust cooperation (sustain 0.999) from intrinsic cooperative priors and private-experience tracking; warning accuracy improved with troll density. *Didn't work* — no memory-sharing meant repeated re-victimization (97 damaging trades, last-half 3.73).

**GR (Global Reputation):** *Worked* — visible scores steered agents away from trolls cleanly (34 damaging trades, lowest non-NR). *Didn't work* — sustainability dipped to 0.944 (lowest among the "good" mechanisms); utility only middling (5.55). Agents trusted scores but scores didn't translate to higher throughput.

**C (Contracting):** *Worked* — strong troll deterrence (29 damaging, last-half 0.87); good equity (gini 0.271). *Didn't work* — chilled trade volume catastrophically (Round 14: only 7 trades; Round 18: 5 trades) and tanked sustainability (0.889, lowest of all). The 6-utility breach penalty made agents trade-averse.

**M (Mediation):** *Worked* — peace 0.997 (essentially no conflict). *Didn't work* — everything else. Util −1.22, gini 0.626 (worst inequality), agents hoarded and over-produced. Delegation removed agents' agency to complete profitable trades. **A textbook case of optimizing the wrong metric.**

**G (Governance):** *Worked* — best combined profile (util 6.37, sustain 0.999, gini 0.283); oracle penalties demonstrably changed behavior (see traces); late troll damage cut to 0.67. *Didn't work* — **false accusation rate 1.0** and warning accuracy 0.0 — the oracle's enforcement may be flagging legitimately, but the social-warning channel became pure noise.

**NR (Network Rewiring):** *Worked* — best utility (6.68) and best late troll isolation (0.13) at 4 trolls; agents used severing strategically. *Didn't work* — at 2 trolls it backfired badly (117 damaging trades, util below baseline); high whistleblowing churn (0.46–0.78).

**S (Costly Sanctions):** *Worked* — perfect sustainability (1.0). *Didn't work* — the 1-utility sanction cost was a continuous drain (worst non-pathological util, 4.30); sanctions punished after damage already occurred (66 damaging trades). Net-negative on the commons.

---

## 8. BREAKING POINTS

| Mechanism | Breaking Point | Evidence |
|-----------|---------------|----------|
| **G** | **Not reached at 4 trolls** | Util 6.37, sustain 0.999 — highest practical breaking point |
| **NR** | Not reached at 4 (but *backfires* at 2) | Anti-fragile at 4 (util 6.68); inefficient at 2 |
| **GR** | Not reached at 4 | Sustain 0.944 — degrading but functional |
| **B** | Degrading but not broken at 4 | Util 5.35; 97 damaging trades suggests strain |
| **S** | Functionally strained at 4 | Sustain perfect but util collapsing to 4.30 |
| **C** | Strained at 4 | Sustain 0.889 — trade suppression visible |
| **M** | **Already broken at 4** | Util −1.22 — the only outright failure |

**Highest breaking point:** **G and NR** — neither showed failure at 4 trolls; both exceeded baseline utility. **Lowest:** **M** — failed completely at the only troll count tested.

**Major gap:** No mechanism except B and NR was tested below 4 trolls, and none above 4. We cannot identify true breaking points without testing 6, 8, 10+ trolls. M's failure at 4 might also occur at 0 trolls (it may be a mechanism-design flaw, not an adversarial breaking point) — this is untestable from current data.

---

## 9. IMPLICATIONS

**For the research question** (which institutions sustain LLM cooperation under adversarial pressure):

1. **The cooperative baseline is the most important finding.** LLM agents cooperate strongly by default (sustain ~1.0 even at 4 trolls with no mechanism). This means mechanisms must be evaluated on their *marginal* benefit — and most mechanisms here were *marginally harmful* to utility. The question reframes from "what enables cooperation" to "what doesn't break already-cooperative agents."

2. **Process metrics can mask welfare collapse.** Mediation achieved near-perfect "peace" (0.997) while destroying welfare (util −1.22). Sanctions achieved perfect "sustainability" while draining utility. **Peace and sustainability are necessary but radically insufficient success metrics.**

3. **Information is non-monotonically valuable.** NR's richer information *hurt* at 2 trolls and *helped* at 4. Mechanism value is contingent on adversarial density.

4. **Light-touch enforcement (G) beat heavy-touch (M, C, S).** The governance oracle that targeted only egregious behavior (>40% defection, predatory targeting) preserved trade flow while deterring trolls. Mechanisms imposing per-interaction friction (C's penalties, S's costs) suppressed the beneficial trade that drives utility.

**What should be tested next:**

1. **Replication — urgently.** Every cell is **1/1 runs**. No statistical claim is defensible. Minimum 10–20 seeds per cell before any ranking is trusted. NR's 117-vs-42 damaging-trade gap and M's collapse especially need confirmation.
2. **Fill the troll × mechanism matrix:** test all 7 mechanisms at 0 and 2 trolls (to isolate mechanism-design failure from adversarial failure — critical for M) and extend to 6/8/10 trolls to find real breaking points.
3. **Decompose NR's 2-troll backfire:** is it the rewiring affordance, the gossip, or the proposal-to-many strategy that drives the 117 damaging trades?
4. **Investigate G's false-accusation rate of 1.0 / warning-accuracy 0.0** — is the social channel broken, redundant, or actively harmful when an oracle exists?
5. **Test mechanism combinations** (e.g., G + NR) since the two best performers operate on different channels (enforcement vs. structure).
6. **Disentangle M's failure** — is it the agent-designed mediator quality, free delegation removing agency, or the LLM's mediation reasoning? The hoarding behavior (traces) suggests a delegation-incentive bug, not adversarial pressure.

**Bottom line:** Governance and network rewiring are the leading candidates, baseline is a stubbornly strong control, and mediation/sanctions/contracting impose costs exceeding their adversarial benefits — but **all conclusions are provisional pending replication.**