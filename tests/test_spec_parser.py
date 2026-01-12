from pathlib import Path

import pytest

from agentforge.core import spec_parser


def test_parse_spec_requires_sections(tmp_path: Path) -> None:
    spec_path = tmp_path / "spec.md"
    spec_path.write_text("# Goals\nShip it.\n", encoding="utf-8")

    with pytest.raises(ValueError, match="missing required sections"):
        spec_parser.parse_spec(str(spec_path))


def test_parse_spec_reads_preamble_and_sections(tmp_path: Path) -> None:
    spec_path = tmp_path / "spec.md"
    spec_path.write_text(
        "Preamble line.\n"
        "\n"
        "# Goals\n"
        "A goal.\n"
        "# Constraints\n"
        "A constraint.\n",
        encoding="utf-8",
    )

    parsed = spec_parser.parse_spec(str(spec_path))
    assert parsed["preamble"] == "Preamble line."
    assert parsed["sections"]["Goals"] == "A goal."
    assert parsed["sections"]["Constraints"] == "A constraint."


def test_parse_spec_rejects_missing_file(tmp_path: Path) -> None:
    missing = tmp_path / "missing.md"
    with pytest.raises(FileNotFoundError):
        spec_parser.parse_spec(str(missing))
