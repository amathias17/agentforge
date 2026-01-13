"""Execution coordination for AgentForge commands."""
# TODO: Implement command execution coordination.

from __future__ import annotations

from pathlib import Path
import shutil
import json
import os
import subprocess


DEFAULT_TIMEOUT_SECONDS = 300


def execute(prompt: str, timeout: int = DEFAULT_TIMEOUT_SECONDS) -> str:
    executable = os.environ.get("AGENTFORGE_CODEX_PATH") or "codex"
    command = _build_command(executable) + ["exec", "-"]
    try:
        result = subprocess.run(
            command,
            input=prompt,
            text=True,
            encoding="utf-8",
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


def _build_command(executable: str) -> list[str]:
    lowered = executable.lower()
    if lowered.endswith(".cmd") or lowered.endswith(".bat"):
        return ["cmd", "/c", executable]
    if lowered.endswith(".ps1"):
        cmd_candidate = _resolve_cmd_for_ps1(executable)
        if cmd_candidate:
            return ["cmd", "/c", cmd_candidate]
        return ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", executable]

    resolved = _resolve_windows_shim(executable)
    if resolved:
        return resolved

    return [executable]


def _resolve_windows_shim(executable: str) -> list[str] | None:
    path = Path(executable)
    if path.suffix:
        return None

    for suffix in (".cmd", ".bat"):
        candidate = _resolve_candidate(path, suffix)
        if candidate:
            return ["cmd", "/c", candidate]

    candidate = _resolve_candidate(path, ".ps1")
    if candidate:
        return [
            "powershell",
            "-NoProfile",
            "-ExecutionPolicy",
            "Bypass",
            "-File",
            candidate,
        ]

    return None


def _resolve_cmd_for_ps1(executable: str) -> str | None:
    path = Path(executable)
    if path.suffix.lower() != ".ps1":
        return None

    base = path.with_suffix("")
    if path.parent != Path(".") or path.is_absolute():
        for suffix in (".cmd", ".bat"):
            candidate = base.with_suffix(suffix)
            if candidate.exists():
                return str(candidate)
        return None

    for suffix in (".cmd", ".bat"):
        resolved = shutil.which(f"{base}{suffix}")
        if resolved:
            return resolved

    return None


def _resolve_candidate(path: Path, suffix: str) -> str | None:
    if path.parent != Path(".") or path.is_absolute():
        candidate = path.with_suffix(suffix)
        if candidate.exists():
            return str(candidate)
        return None

    return shutil.which(f"{path}{suffix}")


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
