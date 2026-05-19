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

from openai import AsyncOpenAI, RateLimitError

from ..config import MODEL, MAX_RETRIES, COT_AGENT_IDS, GOODS, AGENTS_PER_GOOD, AZURE_ENDPOINT

client = AsyncOpenAI(
    api_key=os.environ.get("AZURE_OPENAI_API_KEY"),
    base_url=AZURE_ENDPOINT,
)

_IO_SUFFIX = "\nOutput your chosen actions as a JSON array. Respond with the JSON array only, no other text."

_COT_SUFFIX = (
    "\nBefore choosing actions, write your reasoning:\n\n"
    "<reasoning>\n"
    "1. My situation: (inventory, utility, what happened last round)\n"
    "2. My assessment: (who can I trust, what are the risks)\n"
    "3. My strategy: (what I will do this round and why)\n"
    "</reasoning>\n\n"
    "Then output your chosen actions in a ```json\n...\n``` block."
)


def _extract_json(text: str) -> list[dict]:
    # Try bare JSON first
    text = text.strip()
    if text.startswith("["):
        return json.loads(text)
    # Try ```json block
    match = re.search(r"```json\s*(\[.*?\])\s*```", text, re.DOTALL)
    if match:
        return json.loads(match.group(1))
    # Fallback: find first [ ... ] in text
    match = re.search(r"(\[.*\])", text, re.DOTALL)
    if match:
        return json.loads(match.group(1))
    raise ValueError(f"No JSON array found in response:\n{text[:300]}")


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
                response = await client.chat.completions.create(
                    model=MODEL,
                    messages=[{"role": "user", "content": full_prompt}],
                    temperature=0.7,
                )
                text = response.choices[0].message.content
                self.last_raw_response = text
                return _extract_json(text)
            except RateLimitError:
                wait = backoff * (2 ** attempt)
                print(f"[Agent {self.agent_id}] Rate limited — waiting {wait:.1f}s (attempt {attempt+1}/{MAX_RETRIES})")
                await asyncio.sleep(wait)
            except (json.JSONDecodeError, ValueError) as e:
                if attempt == MAX_RETRIES - 1:
                    print(f"[Agent {self.agent_id}] JSON parse failed after {MAX_RETRIES} attempts: {e}")
                    return []
        return []


class IOAgent(_BaseAgent):
    """Direct JSON output — no reasoning trace."""
    def _suffix(self) -> str:
        return _IO_SUFFIX


class CoTAgent(_BaseAgent):
    """Chain-of-thought before JSON output."""
    def _suffix(self) -> str:
        return _COT_SUFFIX


def make_agents() -> list[_BaseAgent]:
    """Create 9 agents (3 per good), mixing CoT and IO styles."""
    agents = []
    idx = 0
    for good in GOODS:
        others = [g for g in GOODS if g != good]
        needs = (others[0], others[1])
        for _ in range(AGENTS_PER_GOOD):
            cls = CoTAgent if idx in COT_AGENT_IDS else IOAgent
            agents.append(cls(agent_id=idx, specialty=good, needs=needs))
            idx += 1
    return agents
