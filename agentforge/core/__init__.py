"""Core package for AgentForge domain operations."""

__all__ = [
    "generate_agents",
    "generate_agent_files",
    "analyze_repo",
    "parse_spec",
    "build_agent_generation_prompt",
    "execute",
    "run_with_agent",
]

from agentforge.core.agent_generator import generate_agent_files, generate_agents
from agentforge.core.repo_analyzer import analyze_repo
from agentforge.core.spec_parser import parse_spec
from agentforge.core.prompt_builder import build_agent_generation_prompt
from agentforge.core.executor import execute, run_with_agent
