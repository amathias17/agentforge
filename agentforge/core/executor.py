"""Execution coordination for AgentForge commands."""
# TODO: Implement command execution coordination.

from __future__ import annotations

from pathlib import Path
import json
import os
import subprocess


DEFAULT_TIMEOUT_SECONDS = 300


def execute(prompt: str, timeout: int = DEFAULT_TIMEOUT_SECONDS) -> str:
    executable = os.environ.get("AGENTFORGE_CODEX_PATH") or "codex"
    try:
        result = subprocess.run(
            [executable],
            input=prompt,
            text=True,
            capture_output=True,
            check=True,
            timeout=timeout,
        )
    except FileNotFoundError as exc:
        if executable == "codex":
            message = (
                "Codex executable not found on PATH. Install the Codex CLI and "
                "ensure it is available in PATH, or set AGENTFORGE_CODEX_PATH."
            )
        else:
            message = (
                "Codex executable not found at AGENTFORGE_CODEX_PATH. "
                "Update the environment variable or install the Codex CLI."
            )
        raise RuntimeError(message) from exc
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError(
            f"Codex execution exceeded timeout ({timeout}s)."
        ) from exc
    except subprocess.CalledProcessError as exc:
        stderr = (exc.stderr or "").strip()
        stdout = (exc.stdout or "").strip()
        detail = stderr or stdout or "No output captured from codex."
        raise RuntimeError(f"Codex execution failed: {detail}") from exc
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
