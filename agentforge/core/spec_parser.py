"""Specification parsing utilities for AgentForge."""
# TODO: Implement agent specification parsing.

from __future__ import annotations

from pathlib import Path


REQUIRED_SECTIONS = {"Goals", "Constraints"}
OPTIONAL_SECTIONS = {
    "Context",
    "Deliverables",
    "Out of Scope",
    "Agents",
    "Responsibilities",
}


def parse_spec(path: str) -> dict:
    spec_path = Path(path)
    if not spec_path.exists():
        raise FileNotFoundError(f"Spec file not found: {spec_path}")
    if spec_path.is_dir():
        raise ValueError(f"Spec path is a directory: {spec_path}")

    raw_text = spec_path.read_text(encoding="utf-8")
    if raw_text.startswith("\ufeff"):
        raw_text = raw_text.lstrip("\ufeff")
    if not raw_text.strip():
        raise ValueError(f"Spec file is empty: {spec_path}")

    sections: dict[str, str] = {}
    preamble_lines: list[str] = []
    preamble_text = ""
    current_heading: str | None = None
    current_lines: list[str] = []

    for line in raw_text.splitlines():
        if line.startswith("# "):
            if current_heading is None:
                preamble_text = "\n".join(preamble_lines).rstrip("\n")
            else:
                sections[current_heading] = "\n".join(current_lines).rstrip("\n")
            current_heading = line[2:].strip()
            if not current_heading:
                raise ValueError("Section headings must include a title.")
            if current_heading in sections:
                raise ValueError(f"Duplicate section heading: {current_heading}")
            current_lines = []
            continue

        if current_heading is None:
            preamble_lines.append(line)
        else:
            current_lines.append(line)

    if current_heading is not None:
        sections[current_heading] = "\n".join(current_lines).rstrip("\n")

    missing = REQUIRED_SECTIONS - sections.keys()
    if missing:
        raise ValueError(f"Spec missing required sections: {sorted(missing)}")

    return {
        "raw": raw_text,
        "preamble": preamble_text,
        "sections": sections,
    }
