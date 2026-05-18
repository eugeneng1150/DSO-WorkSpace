"""Mediation mechanism: session-start design/vote, then per-trade delegation."""
from __future__ import annotations
import asyncio
from .base import Mechanism
from ..engine.market import MediatorDesign
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from ..engine.market import Market
    from ..engine.agent import _BaseAgent


class MediationMechanism(Mechanism):
    name = "mediation"

    async def on_session_start(self, market: "Market", agents: list["_BaseAgent"]) -> None:
        """Run design phase (stage 1) then vote phase (stage 2) before Round 1."""
        await self._design_and_vote(market, agents)

    async def _design_and_vote(self, market: "Market", agents: list["_BaseAgent"]) -> None:
        from ..engine.prompt_builder import build_prompt

        metrics = {k: 1.0 for k in ["efficiency", "equality", "sustainability", "peace"]}

        # Stage 1: all agents propose a design
        design_prompts = [
            build_prompt(
                agent_id=a.agent_id,
                specialty=a.specialty,
                needs=a.needs,
                last_utility=a.last_utility,
                total_utility=a.total_utility,
                metrics=metrics,
                market=market,
                mechanisms=["mediation"],
                stage_overrides={"mediation": "1"},
            )
            for a in agents
        ]
        design_responses = await asyncio.gather(*[a.call(p) for a, p in zip(agents, design_prompts)])

        for agent, actions in zip(agents, design_responses):
            for action in actions:
                if action.get("action") == "propose_mediator":
                    design = action.get("design", {})
                    market.mediator_designs.append(
                        MediatorDesign(
                            designer_id=agent.agent_id,
                            action_both=design.get("2", "execute_fair"),
                            action_one=design.get("1", "cancel"),
                            rationale=action.get("rationale", ""),
                        )
                    )

        # Stage 2: all agents vote
        vote_prompts = [
            build_prompt(
                agent_id=a.agent_id,
                specialty=a.specialty,
                needs=a.needs,
                last_utility=a.last_utility,
                total_utility=a.total_utility,
                metrics=metrics,
                market=market,
                mechanisms=["mediation"],
                stage_overrides={"mediation": "2"},
            )
            for a in agents
        ]
        vote_responses = await asyncio.gather(*[a.call(p) for a, p in zip(agents, vote_prompts)])

        for agent, actions in zip(agents, vote_responses):
            for action in actions:
                if action.get("action") == "vote_mediator":
                    approved_ids = action.get("approved", [])
                    market.mediation_votes[agent.agent_id] = [int(x) for x in approved_ids]

        # Tally votes: design with most approvals wins
        approval_counts = {d.designer_id: 0 for d in market.mediator_designs}
        for voter_id, approved in market.mediation_votes.items():
            for designer_id in approved:
                if designer_id in approval_counts:
                    approval_counts[designer_id] += 1

        if approval_counts:
            winner_id = max(approval_counts, key=approval_counts.__getitem__)
            market.active_mediator = next(
                d for d in market.mediator_designs if d.designer_id == winner_id
            )

    def on_trade_phase(self, market: "Market", agents: list["_BaseAgent"]) -> None:
        """Execute mediated trades where both parties delegated."""
        # Mediated trade execution is handled in game.py when processing accept/delegate actions.
        pass

    def get_stage_override(self, agent: "_BaseAgent", market: "Market") -> dict[str, str]:
        # After session start, always stage 3 (delegation decision per round)
        return {"mediation": "3"}
