import pytest

from agentforge.core import agent_generator


def test_normalize_agent_strips_and_splits() -> None:
    agent = {
        "name": " Test ",
        "role": " Role ",
        "responsibilities": "- Ship feature\n- Own reviews",
        "constraints": "Stay within scope",
        "exclusions": None,
        "communication_style": " Clear, concise ",
    }

    normalized = agent_generator._normalize_agent(agent)

    assert normalized["name"] == "Test"
    assert normalized["role"] == "Role"
    assert normalized["responsibilities"] == ["Ship feature", "Own reviews"]
    assert normalized["constraints"] == ["Stay within scope"]
    assert normalized["exclusions"] == []
    assert normalized["communication_style"] == "Clear, concise"


def test_normalize_agent_rejects_non_string_items() -> None:
    agent = {
        "name": "Agent",
        "role": "Role",
        "responsibilities": [123],
        "constraints": ["Stay within scope"],
    }

    with pytest.raises(ValueError, match="responsibilities"):
        agent_generator._normalize_agent(agent)


def test_normalize_agent_requires_entries() -> None:
    agent = {
        "name": "Agent",
        "role": "Role",
        "responsibilities": "",
        "constraints": "  ",
    }

    with pytest.raises(ValueError, match="responsibilities"):
        agent_generator._normalize_agent(agent)
