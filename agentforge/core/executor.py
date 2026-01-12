"""Execution coordination for AgentForge commands."""
# TODO: Implement command execution coordination.

from __future__ import annotations

from pathlib import Path
import json
import subprocess


def execute(prompt: str) -> str:
    result = subprocess.run(
        ["codex"],
        input=prompt,
        text=True,
        capture_output=True,
        check=True,
    )
    return result.stdout


def run_with_agent(agent_path: str, task: str, context: dict) -> str:
    agent_text = Path(agent_path).read_text(encoding="utf-8")
    context_text = json.dumps(context, indent=2, sort_keys=True, ensure_ascii=True)

    prompt = (
        f"{agent_text}\n\n"
        "Context:\n"
        f"{context_text}\n\n"
        "Task:\n"
        f"{task}\n"
    )

    return execute(prompt)
