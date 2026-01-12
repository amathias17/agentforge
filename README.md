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
agentforge generate
```

Run a task with an existing agent definition:

```
agentforge run
```
