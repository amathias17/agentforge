"""Agent definition generation utilities for AgentForge."""
# TODO: Implement agent definition generation.

import json

from agentforge.core import executor
from agentforge.core.prompt_builder import build_agent_generation_prompt


_REQUIRED_FIELDS = {"name", "role", "responsibilities", "constraints"}


def generate_agents(spec: dict, repo_meta: dict) -> list[dict]:
    prompt = build_agent_generation_prompt(spec, repo_meta)
    response = executor.execute(prompt)

    parsed = json.loads(response)
    agents = parsed.get("agents") if isinstance(parsed, dict) else parsed
    if not isinstance(agents, list):
        raise ValueError("Expected a JSON array of agents or an object with 'agents'.")

    normalized: list[dict] = []
    for agent in agents:
        if not isinstance(agent, dict):
            raise ValueError("Each agent must be a JSON object.")
        missing = _REQUIRED_FIELDS - agent.keys()
        if missing:
            raise ValueError(f"Agent missing required fields: {sorted(missing)}")
        normalized.append(agent)

    return normalized
