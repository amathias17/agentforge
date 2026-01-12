"""Agent definition generation utilities for AgentForge."""
# TODO: Implement agent definition generation.

from __future__ import annotations

from pathlib import Path
import json
import re

from jinja2 import Environment, BaseLoader

from agentforge.core import executor, repo_analyzer, spec_parser
from agentforge.core.prompt_builder import build_agent_generation_prompt


_REQUIRED_FIELDS = {"name", "role", "responsibilities", "constraints"}
_OPTIONAL_FIELDS = {"exclusions", "communication_style"}
_TEMPLATE_PATH = Path(__file__).resolve().parent.parent / "templates" / "agent.md.j2"


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
        unknown = set(agent.keys()) - _REQUIRED_FIELDS - _OPTIONAL_FIELDS
        if unknown:
            raise ValueError(f"Agent has unknown fields: {sorted(unknown)}")
        normalized.append(agent)

    return normalized


def generate_agent_files(spec_path: str, repo_root: str, output_dir: str) -> list[dict]:
    spec = spec_parser.parse_spec(spec_path)
    repo_meta = repo_analyzer.analyze_repo(repo_root)
    agents = generate_agents(spec, repo_meta)
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    _render_agent_files(agents, output_path)
    return agents


def _render_agent_files(agents: list[dict], output_path: Path) -> None:
    template = _load_template()
    used_slugs: set[str] = set()
    for agent in agents:
        slug = _unique_slug(_slugify(agent.get("name", "")), used_slugs)
        used_slugs.add(slug)
        agent_dir = output_path / slug
        agent_dir.mkdir(parents=True, exist_ok=True)
        rendered = template.render(_build_template_context(agent))
        (agent_dir / "agent.md").write_text(rendered.rstrip() + "\n", encoding="utf-8")


def _load_template():
    template_text = _TEMPLATE_PATH.read_text(encoding="utf-8")
    env = Environment(loader=BaseLoader(), autoescape=False)
    return env.from_string(template_text)


def _build_template_context(agent: dict) -> dict:
    return {
        "agent_name": agent.get("name", ""),
        "role": agent.get("role", ""),
        "responsibilities": _format_section(agent.get("responsibilities", "")),
        "constraints": _format_section(agent.get("constraints", "")),
        "exclusions": _format_section(agent.get("exclusions", "")),
        "communication_style": agent.get("communication_style", ""),
    }


def _format_section(value: object) -> str:
    if isinstance(value, list):
        items = [str(item).strip() for item in value if str(item).strip()]
        return "\n".join(f"- {item}" for item in items)
    if value is None:
        return ""
    return str(value).strip()


def _slugify(value: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9]+", "-", value.strip().lower())
    cleaned = cleaned.strip("-")
    return cleaned or "agent"


def _unique_slug(slug: str, used: set[str]) -> str:
    if slug not in used:
        return slug
    suffix = 2
    while f"{slug}-{suffix}" in used:
        suffix += 1
    return f"{slug}-{suffix}"
