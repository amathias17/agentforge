from pathlib import Path

from agentforge.core import repo_analyzer


def test_analyze_repo_aggregates_languages(tmp_path: Path) -> None:
    (tmp_path / "a.py").write_text("print('hi')\n", encoding="utf-8")
    (tmp_path / "b.pyi").write_text("def foo() -> None: ...\n", encoding="utf-8")
    (tmp_path / "c.js").write_text("console.log('hi')\n", encoding="utf-8")

    metadata = repo_analyzer.analyze_repo(str(tmp_path))

    assert metadata["languages"]["Python"] == 2
    assert metadata["languages"]["JavaScript"] == 1
    assert "Python" in metadata["primary_languages"]
