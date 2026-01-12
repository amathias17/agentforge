import json

from agentforge.core.prompt_builder import build_agent_generation_prompt


def test_build_agent_generation_prompt_contains_spec_and_repo() -> None:
    spec = {"raw": "spec", "sections": {"Goals": "Ship"}}
    repo = {"primary_languages": ["Python"], "frameworks": []}

    prompt = build_agent_generation_prompt(spec, repo)

    assert "Specification:" in prompt
    assert "Repository Metadata:" in prompt
    assert json.dumps(spec, indent=2, sort_keys=True, ensure_ascii=True) in prompt
    assert json.dumps(repo, indent=2, sort_keys=True, ensure_ascii=True) in prompt
