"""IOAgent and CoTAgent — replicating CoopEval's two reasoning styles.

IOAgent:  direct JSON output, no explicit reasoning trace.
CoTAgent: chain-of-thought reasoning before JSON output; JSON extracted from ```json block.
"""
from __future__ import annotations
import json
import re
import asyncio
import os
from typing import Any

from openai import AsyncOpenAI, RateLimitError, BadRequestError, APITimeoutError

from ..config import MODEL, MAX_RETRIES, COT_AGENT_IDS, GOODS, AGENTS_PER_GOOD, AZURE_ENDPOINT

_client = None
_model = MODEL


def configure_llm(base_url: str, api_key: str, model: str):
    """Override the LLM endpoint/model at runtime (called from main before any agents run)."""
    global _client, _model
    _client = AsyncOpenAI(api_key=api_key, base_url=base_url, timeout=120.0)
    _model = model


def _get_client() -> AsyncOpenAI:
    global _client
    if _client is None:
        _client = AsyncOpenAI(
            api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
            base_url=AZURE_ENDPOINT,
            timeout=120.0,
        )
    return _client

_IO_SUFFIX = "\nOutput your chosen actions as a JSON array. Respond with the JSON array only, no other text."

_COT_SUFFIX = (
    "\nBefore choosing actions, write your reasoning:\n\n"
    "<reasoning>\n"
    "1. My situation: (inventory, utility, what happened last round)\n"
    "2. Self-reflection: (have I been cooperating? how might others perceive me?)\n"
    "3. Gossip evaluation: (which warnings from others seem credible? who has reason to lie?)\n"
    "4. My assessment: (who can I trust, what are the risks)\n"
    "5. My strategy: (what I will do this round and why)\n"
    "</reasoning>\n\n"
    "Then output your chosen actions in a ```json\n...\n``` block."
)


def _extract_json(text: str) -> list[dict]:
    # Try bare JSON first
    text = text.strip()
    raw = None
    if text.startswith("["):
        raw = json.loads(text)
    if raw is None:
        # Try ```json block
        match = re.search(r"```json\s*(\[.*?\])\s*```", text, re.DOTALL)
        if match:
            raw = json.loads(match.group(1))
    if raw is None:
        # Fallback: find first [ ... ] in text
        match = re.search(r"(\[.*\])", text, re.DOTALL)
        if match:
            raw = json.loads(match.group(1))
    if raw is None:
        raise ValueError(f"No JSON array found in response:\n{text[:300]}")
    return [item for item in raw if isinstance(item, dict)]


class _BaseAgent:
    def __init__(self, agent_id: int, specialty: str, needs: tuple[str, str]):
        self.agent_id = agent_id
        self.specialty = specialty
        self.needs = needs
        self.last_utility: float = 0.0
        self.total_utility: float = 0.0
        self.last_raw_response: str = ""

    def _suffix(self) -> str:
        raise NotImplementedError

    async def call(self, prompt: str) -> list[dict[str, Any]]:
        full_prompt = prompt + self._suffix()
        backoff = 2.0
        for attempt in range(MAX_RETRIES):
            try:
                response = await _get_client().chat.completions.create(
                    model=_model,
                    messages=[{"role": "user", "content": full_prompt}],
                    temperature=0.7,
                )
                text = response.choices[0].message.content
                self.last_raw_response = text
                return _extract_json(text)
            except (RateLimitError, APITimeoutError) as e:
                wait = backoff * (2 ** attempt)
                label = "Rate limited" if isinstance(e, RateLimitError) else "Timed out"
                print(f"[Agent {self.agent_id}] {label} — waiting {wait:.1f}s (attempt {attempt+1}/{MAX_RETRIES})")
                await asyncio.sleep(wait)
            except BadRequestError as e:
                err_str = str(e).lower()
                if "flagged" in err_str or "usage policy" in err_str or "content_filter" in err_str:
                    wait = backoff * (2 ** attempt)
                    print(f"[Agent {self.agent_id}] Content filter triggered — retrying in {wait:.1f}s (attempt {attempt+1}/{MAX_RETRIES})")
                    await asyncio.sleep(wait)
                else:
                    raise
            except (json.JSONDecodeError, ValueError) as e:
                if attempt == MAX_RETRIES - 1:
                    print(f"[Agent {self.agent_id}] JSON parse failed after {MAX_RETRIES} attempts: {e}")
                    return []
        print(f"[Agent {self.agent_id}] All {MAX_RETRIES} attempts failed — returning empty actions")
        return []


class IOAgent(_BaseAgent):
    """Direct JSON output — no reasoning trace."""
    def _suffix(self) -> str:
        return _IO_SUFFIX


class CoTAgent(_BaseAgent):
    """Chain-of-thought before JSON output."""
    def _suffix(self) -> str:
        return _COT_SUFFIX


class TrollAgent(_BaseAgent):
    """Deterministic adversary: never produces, always defects, lies in messages."""

    def _suffix(self) -> str:
        return ""

    async def call(self, prompt: str) -> list[dict]:
        self.last_raw_response = "[TROLL — deterministic, no LLM call]"
        return [
            {
                "action": "send_public",
                "text": f"Agent {self.agent_id}: I'm committed to fair trading this round. Let's cooperate for mutual benefit!",
            }
        ]


def make_agents(n_trolls: int = 0) -> list[_BaseAgent]:
    """Create agents (AGENTS_PER_GOOD per good), using CoT or IO style.

    If n_trolls > 0, replace that many agents with deterministic TrollAgents,
    distributed round-robin across goods.
    """
    troll_indices: set[int] = set()
    if n_trolls > 0:
        placed = 0
        agent_offset = 0
        while placed < n_trolls:
            for good_idx in range(len(GOODS)):
                if placed >= n_trolls:
                    break
                troll_indices.add(good_idx * AGENTS_PER_GOOD + agent_offset)
                placed += 1
            agent_offset += 1

    agents = []
    idx = 0
    for good in GOODS:
        others = [g for g in GOODS if g != good]
        needs = (others[0], others[1])
        for _ in range(AGENTS_PER_GOOD):
            if idx in troll_indices:
                agents.append(TrollAgent(agent_id=idx, specialty=good, needs=needs))
            else:
                cls = CoTAgent if idx in COT_AGENT_IDS else IOAgent
                agents.append(cls(agent_id=idx, specialty=good, needs=needs))
            idx += 1
    return agents
