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
