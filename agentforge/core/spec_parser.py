"""Specification parsing utilities for AgentForge."""
# TODO: Implement agent specification parsing.

def parse_spec(path: str) -> dict:
    with open(path, "r", encoding="utf-8") as handle:
        raw_text = handle.read()

    sections: dict[str, str] = {}
    current_heading: str | None = None
    current_lines: list[str] = []

    for line in raw_text.splitlines():
        if line.startswith("# "):
            if current_heading is not None:
                sections[current_heading] = "\n".join(current_lines).rstrip("\n")
            current_heading = line[2:].strip()
            current_lines = []
            continue

        if current_heading is not None:
            current_lines.append(line)

    if current_heading is not None:
        sections[current_heading] = "\n".join(current_lines).rstrip("\n")

    return {"raw": raw_text, "sections": sections}
