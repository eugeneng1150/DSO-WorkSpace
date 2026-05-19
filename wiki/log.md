# Wiki Log

---

## 2026-05-16 — Initial ingest

**Sources ingested**:
- `Cooperation and Exploitation in LLM.pdf` (Gallego, Komorebi AI, 9 pages)
- `Autonomous Research.pdf` (Yang et al., SJTU, 21 pages)
- `AgentSociety.pdf` (Tsinghua University, 49 pages)
- `Cooperateive Resilience in AI multiagent systems.pdf` (Chacon-Chamorro et al., Univ. de los Andes, 16 pages)
- `CoopEval.pdf` (Tewolde, Zhang et al., CMU/Toronto/ETH Zürich, 65 pages)

**Pages created**:
- `cooperation-exploitation-llm.md` — source summary
- `aris-autonomous-research.md` — source summary
- `agentsociety.md` — source summary
- `cooperative-resilience-paper.md` — source summary
- `coopeval.md` — source summary
- `social-dilemmas.md` — concept page
- `cooperation-mechanisms.md` — concept page
- `social-metrics.md` — concept page
- `evolutionary-dynamics.md` — concept page
- `cooperative-resilience.md` — concept page
- `reward-hacking.md` — concept page
- `marketplace-society.md` — synthesis/concept page (research question)
- `index.md` — table of contents
- `log.md` — this file

**Context**: Wiki tailored to research question "What mechanism allows the survival of a society with self-interested agents?" with marketplace modeling as the concrete target.

---

## 2026-05-17 — Experimental design and simulation spec

**Design decisions captured**:
- Communication is baseline (always on); formal mechanisms benchmarked on top
- Confirmed by user

**Pages created**:
- `marketplace-spec.md` — full simulation spec: environment, agent architecture, communication protocol, mechanism implementations, measurement plan, experimental runs

**Pages updated**:
- `marketplace-spec.md` — added Intermediate Variables table to Section 5 (Measurement): whistleblowing rate, false accusation rate, warning accuracy. These decompose mechanism effects into direct (fewer defections) vs indirect (better information propagation) channels, addressing the 2nd-order dilemma confound in the Reputation mechanism.

---

## 2026-05-17 — Research paper draft

**Files created**:
- `paper.tex` — full LaTeX research paper draft

---

## 2026-05-17 — Prompt mechanism folder created

**Files created** (`prompts/`):
- `base_agent.txt` — core agent prompt (always on, all conditions); contains inventory, social metrics, inbox, pending offers, action space, JSON output format
- `baseline.txt` — mechanism block for Condition B (no formal mechanism)
- `reputation.txt` — mechanism block for +Reputation; two-layer system (objective engine score + subjective public mentions)
- `contracting.txt` — all 4 stages: proposal, review/sign, play with active contract, play with rejected contract
- `mediation.txt` — all 3 stages: mediator design (session start), vote, per-trade delegation decision
- `README.md` — composition guide: how blocks combine per condition, when each stage fires

Prompts adapted from CoopEval's "here is the twist" injection pattern, rewritten for the marketplace's multi-good, multi-party, bilateral trade structure.

---

## 2026-05-19 — Ingested dynamic pricing paper

**Sources ingested**:
- `dynaimic pricing.pdf` (Chen, Liu, Xu — Tianjin University, JASSS 2018)

**Pages created**:
- `dynamic-pricing-perishable.md` — source summary: 4 competing retailer agents selling perishable grapes, Q-learning dynamic pricing vs 3 fixed strategies, dual spoilage model (quantity + value decay), key finding that perishability punishes hoarding and overpricing

**Pages updated**:
- `index.md` — added dynamic-pricing-perishable entry to Source Summaries table

**Context**: Paper cited to motivate the inventory spoilage mechanic (30% flat decay per round) added to the simulation. The spoilage concept comes from this paper; our implementation is simplified to a flat percentage rather than their dual quantity/value decay model.

---

## 2026-05-17 — Removed resilience tests

**Decision**: resilience testing (resource shock + social shock) removed from scope to keep the experiment clean and focused.

**Pages updated**:
- `marketplace-spec.md` — removed Resilience Testing subsection from Section 5; removed resilience test note from Section 6
- `paper.tex` — removed resilience tests subsection, updated conditions table, cleaned Discussion covering Introduction, Related Work, Environment Setup, Communication Protocol, Formal Mechanisms, Agent Architecture, Experimental Design, Measurement, Discussion, and Conclusion. Placeholders left for all figures and charts. Bibliography populated from ingested sources.
