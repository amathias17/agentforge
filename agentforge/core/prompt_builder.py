"""Prompt construction utilities for AgentForge."""
# TODO: Implement prompt building for agent outputs.

import json


def build_agent_generation_prompt(spec: dict, repo_meta: dict) -> str:
    spec_text = json.dumps(spec, indent=2, sort_keys=True, ensure_ascii=True)
    repo_text = json.dumps(repo_meta, indent=2, sort_keys=True, ensure_ascii=True)

    return (
        "You are designing role-based AI agents.\n"
        "You must not execute tasks, run commands, write files, or perform any actions.\n"
        "Return structured JSON only.\n"
        "Minimize the number of agents and ensure roles do not overlap.\n\n"
        "Specification:\n"
        f"{spec_text}\n\n"
        "Repository Metadata:\n"
        f"{repo_text}\n"
    )
