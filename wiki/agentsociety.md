# AgentSociety

**Summary**: A large-scale social simulator from Tsinghua University integrating 10k+ LLM-driven agents with a realistic societal environment, validated against five real-world social phenomena.

**Sources**: `AgentSociety.pdf`

**Last updated**: 2026-05-16

---

## Overview

Authors: Tsinghua University (multiple). AgentSociety is a full-stack platform for simulating human societies at scale. It is the most comprehensive operational environment in this reading list and serves as the primary reference for *what a modeled society looks like*.

## Three-Component Architecture

### 1. Social Agents (Mind-Behavior Coupling)
Each agent has three coupled modules:
- **Needs** — drives behavior (hunger, social, safety, etc.), grounded in Maslow's hierarchy
- **Emotion** — modulates decision-making; emotional state is updated after each interaction
- **Cognition** — LLM-based reasoning that integrates needs, emotion, and environmental context to select actions

Actions span three behavioral domains: **Mobility** (where to go), **Social** (who to talk to, what to share), **Economy** (how to allocate resources).

### 2. Societal Environment
Three layered spaces:
- **Urban Space** — physical geography, POIs, transport (GIS-grounded)
- **Social Space** — social network graph; agents message via MQTT protocol
- **Economic Space** — income, consumption, GDP tracking

### 3. Simulation Engine
- **Ray** — distributed parallel computation for scaling to 10k+ agents
- **MQTT** — IoT messaging protocol for agent-to-agent communication; chosen over Redis/RabbitMQ/Kafka for throughput + GUI tooling
- Bottleneck: LLM API call latency dominates, not environment computation

## Five Validated Experiments

### Polarization (100 agents, gun control)
- Control: 39% became more polarized through neutral interaction
- Homophilic (echo chamber): 52% became more polarized
- Heterogeneous (exposure to opposing views): 89% became more moderate

**Implication for research question**: Social network structure is a cooperation mechanism. Heterogeneous interaction is functionally equivalent to a reputation or mediation mechanism — it forces agents to encounter information that disrupts defection-sustaining echo chambers.

### Inflammatory Message Spread (100 agents)
- Inflammatory messages spread faster and triggered higher emotional intensity than neutral content
- Node-level intervention (suspending repeat sharers) more effective than edge-level intervention (removing connections)
- Emotional factors and social responsibility drive sharing behavior

### Universal Basic Income (100 agents, Texas demographics)
- UBI ($1,000/month unconditional payment) increased consumption and reduced depression levels
- Results aligned with real Texas UBI experiment data
- Validates simulator as a policy evaluation tool

### Hurricane Dorian Mobility (1,000 agents, Columbia SC)
- Activity level dropped from 70–90% to ~30% during landfall, then recovered
- Simulated mobility closely tracked SafeGraph real-world data
- Slight discrepancy in magnitude and speed of response during peak

### Urban Sustainability (200 agents, Beijing)
- Six independent teams injected different eco-normative intervention systems
- **Personal norms** (internalized moral obligation) consistently outperformed **injunctive norms** (external expectation)
- Stronger normative internalization correlated with larger behavioral shifts (CO₂ emission reduction)

**Implication**: For a [[marketplace-society]], norm internalization (analogous to cultural values) may be more durable than external rule enforcement.

## Toolbox for Social Experiments
Three intervention types: Agent Configuration (pre-simulation), State Manipulation (during simulation), Message Notification (any time). Plus Interview and Survey tools for qualitative data from agents.

## Connection to Research Question

AgentSociety provides the most complete answer to "what does a modeled society look like?" for the marketplace project:

- The three-space environment maps to: **Urban** → physical marketplace, **Social** → communication network, **Economic** → trade ledger
- The mind-behavior coupling (needs + emotion + cognition) is a template for agent design
- The experiments show which interventions shift collective outcomes: heterogeneous interaction, UBI redistribution, personal norm formation
- The bottleneck finding (LLM API latency) is critical for implementation planning

## Related pages

- [[marketplace-society]]
- [[social-metrics]]
- [[cooperation-mechanisms]]
- [[cooperative-resilience]]
- [[social-dilemmas]]
