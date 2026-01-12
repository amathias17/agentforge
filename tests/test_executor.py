import os
import subprocess

import pytest

from agentforge.core import executor


def test_execute_success(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_run(*_args, **_kwargs):
        return subprocess.CompletedProcess(args=["codex"], returncode=0, stdout="ok\n")

    monkeypatch.setattr(subprocess, "run", fake_run)
    assert executor.execute("prompt") == "ok\n"


def test_execute_missing_binary(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_run(*_args, **_kwargs):
        raise FileNotFoundError("codex")

    monkeypatch.setattr(subprocess, "run", fake_run)
    with pytest.raises(RuntimeError, match="executable not found"):
        executor.execute("prompt")


def test_execute_timeout(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_run(*_args, **_kwargs):
        raise subprocess.TimeoutExpired(cmd=["codex"], timeout=1)

    monkeypatch.setattr(subprocess, "run", fake_run)
    with pytest.raises(RuntimeError, match="timeout"):
        executor.execute("prompt", timeout=1)


def test_execute_called_process_error_uses_stderr(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_run(*_args, **_kwargs):
        raise subprocess.CalledProcessError(1, ["codex"], output="out", stderr="err")

    monkeypatch.setattr(subprocess, "run", fake_run)
    with pytest.raises(RuntimeError, match="err"):
        executor.execute("prompt")


def test_execute_wraps_cmd_executable(monkeypatch: pytest.MonkeyPatch) -> None:
    seen = {}

    def fake_run(args, **_kwargs):
        seen["args"] = args
        return subprocess.CompletedProcess(args=args, returncode=0, stdout="ok")

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setenv("AGENTFORGE_CODEX_PATH", r"C:\tools\codex.cmd")

    executor.execute("prompt")

    assert seen["args"][:2] == ["cmd", "/c"]
    assert seen["args"][2].endswith("codex.cmd")
    assert seen["args"][3:5] == ["exec", "-"]


def test_execute_wraps_powershell_script(monkeypatch: pytest.MonkeyPatch) -> None:
    seen = {}

    def fake_run(args, **_kwargs):
        seen["args"] = args
        return subprocess.CompletedProcess(args=args, returncode=0, stdout="ok")

    monkeypatch.setattr(subprocess, "run", fake_run)
    monkeypatch.setenv("AGENTFORGE_CODEX_PATH", r"C:\tools\codex.ps1")

    executor.execute("prompt")

    assert seen["args"][:4] == ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass"]
    assert seen["args"][4] == "-File"
    assert seen["args"][5].endswith("codex.ps1")
    assert seen["args"][6:8] == ["exec", "-"]
