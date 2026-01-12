"""Command-line interface entry points for AgentForge."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

from agentforge.core import agent_generator, executor, repo_analyzer, spec_parser


def _load_json_file(path: str) -> dict:
    data = Path(path).read_text(encoding="utf-8")
    try:
        parsed = json.loads(data)
    except json.JSONDecodeError as exc:
        raise ValueError(f"Invalid JSON in {path}: {exc}") from exc
    if not isinstance(parsed, dict):
        raise ValueError(f"Expected JSON object in {path}.")
    return parsed


def _write_output(path: str | None, payload: dict | list[dict]) -> None:
    output = json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True)
    if path:
        Path(path).write_text(output + "\n", encoding="utf-8")
    else:
        print(output)


def main() -> None:
    parser = argparse.ArgumentParser(prog="agentforge")
    subparsers = parser.add_subparsers(dest="command", required=True)

    generate_parser = subparsers.add_parser("generate", help="Generate agent definitions.")
    generate_parser.add_argument("--spec", required=True, help="Path to the spec file.")
    generate_parser.add_argument(
        "--repo",
        default=".",
        help="Repository root used for metadata analysis (default: .).",
    )
    generate_parser.add_argument(
        "--output-dir",
        help="Write generated agents JSON into this directory (defaults to stdout).",
    )
    generate_parser.add_argument(
        "--codex-path",
        help="Path to the codex CLI executable (overrides AGENTFORGE_CODEX_PATH).",
    )

    run_parser = subparsers.add_parser("run", help="Run an agent definition.")
    run_parser.add_argument("--agent", required=True, help="Path to an agent definition.")
    task_group = run_parser.add_mutually_exclusive_group(required=True)
    task_group.add_argument("--task", help="Task text to run.")
    task_group.add_argument("--task-file", help="Path to a task file.")
    run_parser.add_argument(
        "--context",
        help="Path to a JSON file providing execution context.",
    )
    run_parser.add_argument(
        "--codex-path",
        help="Path to the codex CLI executable (overrides AGENTFORGE_CODEX_PATH).",
    )

    args = parser.parse_args()

    try:
        if args.codex_path:
            os.environ["AGENTFORGE_CODEX_PATH"] = args.codex_path

        if args.command == "generate":
            if args.output_dir:
                output_dir = Path(args.output_dir)
                agents = agent_generator.generate_agent_files(
                    args.spec, args.repo, str(output_dir)
                )
                _write_output(str(output_dir / "agents.json"), agents)
            else:
                spec = spec_parser.parse_spec(args.spec)
                repo_meta = repo_analyzer.analyze_repo(args.repo)
                agents = agent_generator.generate_agents(spec, repo_meta)
                _write_output(None, agents)
            return

        if args.command == "run":
            task_text = args.task
            if args.task_file:
                task_text = Path(args.task_file).read_text(encoding="utf-8")
            context = _load_json_file(args.context) if args.context else {}
            result = executor.run_with_agent(args.agent, task_text, context)
            print(result)
            return
    except (OSError, ValueError, RuntimeError, subprocess.CalledProcessError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    print("Error: Unknown command.", file=sys.stderr)
    sys.exit(2)
