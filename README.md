# AgentForge

AgentForge is a Python CLI that creates and manages role-based AI agent definition files (`agent.md`) for use with Codex.

## What It Does Not Do

AgentForge intentionally avoids orchestration, autonomous execution, background processes, plugins, and any networking logic.

## Usage Philosophy

AgentForge is CLI-first, minimal, and predictable. It focuses on straightforward file generation and management without hidden behavior or side effects.

## How To Use

Use the CLI to generate agent definitions or run a task with a chosen agent file.

Generate agent files:

```
agentforge generate --spec spec/spec.md --output-dir output
```

Run a task with an existing agent definition:

```
agentforge run --agent output/<agent-name>/agent.md --task "Describe the task"
```

## Codex CLI Setup

AgentForge shells out to the Codex CLI. Install it and ensure `codex` is on PATH,
or pass a full path with `--codex-path` (or set `AGENTFORGE_CODEX_PATH`).

## Spec Location

A sample spec template lives at `spec/spec.md`. Edit it or replace it with your own
spec file, then pass the path via `--spec`.

## Agent Schema

Generated agent definitions use the following fields:

Required:
- `name`
- `role`
- `responsibilities`
- `constraints`

Optional:
- `exclusions`
- `communication_style`

## Spec Format

Specs are Markdown files with `# ` headings for each top-level section.

Required sections:
- `Goals`
- `Constraints`

Optional sections:
- `Context`
- `Deliverables`
- `Out of Scope`
- `Agents`
- `Responsibilities`
