"""Repository analysis utilities for AgentForge."""
# TODO: Implement repository scanning and metadata extraction.

from __future__ import annotations

from collections import Counter
from pathlib import Path
import configparser
import json
import os
import tomllib


_EXTENSION_LANGUAGE = {
    ".py": "Python",
    ".pyi": "Python",
    ".js": "JavaScript",
    ".jsx": "JavaScript",
    ".ts": "TypeScript",
    ".tsx": "TypeScript",
    ".java": "Java",
    ".kt": "Kotlin",
    ".rb": "Ruby",
    ".go": "Go",
    ".rs": "Rust",
    ".cs": "C#",
    ".cpp": "C++",
    ".cxx": "C++",
    ".cc": "C++",
    ".c": "C",
    ".h": "C/C++",
    ".hpp": "C/C++",
    ".html": "HTML",
    ".css": "CSS",
    ".scss": "SCSS",
    ".md": "Markdown",
    ".json": "JSON",
    ".yaml": "YAML",
    ".yml": "YAML",
}

_FRAMEWORK_DEPENDENCIES = {
    "fastapi": "FastAPI",
    "django": "Django",
    "flask": "Flask",
    "react": "React",
    "next": "Next.js",
    "vue": "Vue",
    "svelte": "Svelte",
    "express": "Express",
}

_IGNORE_DIRS = {
    ".git",
    "__pycache__",
    ".venv",
    "venv",
    "node_modules",
    "dist",
    "build",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
}


def analyze_repo(root: str) -> dict:
    root_path = Path(root)
    extension_counts: Counter[str] = Counter()
    total_files = 0
    tests_exist = False
    frameworks: set[str] = set()

    for dirpath, dirnames, filenames in os.walk(root_path):
        dirnames[:] = [d for d in dirnames if d not in _IGNORE_DIRS]

        for filename in filenames:
            total_files += 1
            ext = Path(filename).suffix.lower()
            if ext in _EXTENSION_LANGUAGE:
                extension_counts[ext] += 1

            lower_name = filename.lower()
            if (
                lower_name.startswith("test_")
                or lower_name.endswith("_test.py")
                or lower_name.endswith(".spec.js")
                or lower_name.endswith(".test.js")
                or lower_name.endswith(".spec.ts")
                or lower_name.endswith(".test.ts")
            ):
                tests_exist = True

        if not tests_exist:
            for dirname in dirnames:
                if dirname.lower() in {"tests", "test", "__tests__"}:
                    tests_exist = True
                    break

    frameworks.update(_detect_frameworks_from_files(root_path))
    frameworks.update(_detect_frameworks_from_dependencies(root_path))

    languages = Counter(
        {_EXTENSION_LANGUAGE[ext]: count for ext, count in extension_counts.items()}
    )
    primary_languages = [name for name, _ in languages.most_common()]

    size = _classify_size(total_files)

    return {
        "root": str(root_path),
        "primary_languages": primary_languages,
        "languages": dict(languages),
        "frameworks": sorted(frameworks),
        "tests": tests_exist,
        "size": size,
    }


def analyze_repository(path: str) -> dict:
    return analyze_repo(path)


def _classify_size(total_files: int) -> str:
    if total_files < 50:
        return "small"
    if total_files < 200:
        return "medium"
    return "large"


def _detect_frameworks_from_files(root_path: Path) -> set[str]:
    frameworks: set[str] = set()

    if (root_path / "manage.py").exists():
        frameworks.add("Django")

    if (root_path / "next.config.js").exists() or (root_path / "next.config.mjs").exists():
        frameworks.add("Next.js")

    if (root_path / "vite.config.js").exists() or (root_path / "vite.config.ts").exists():
        frameworks.add("Vite")

    return frameworks


def _detect_frameworks_from_dependencies(root_path: Path) -> set[str]:
    frameworks: set[str] = set()
    dependency_names = set()

    dependency_names.update(_read_requirements_txt(root_path))
    dependency_names.update(_read_pyproject_dependencies(root_path))
    dependency_names.update(_read_setup_cfg_dependencies(root_path))
    dependency_names.update(_read_setup_py_dependencies(root_path))
    dependency_names.update(_read_pipfile_dependencies(root_path))
    dependency_names.update(_read_package_json_dependencies(root_path))

    for dep in dependency_names:
        key = dep.lower()
        if key in _FRAMEWORK_DEPENDENCIES:
            frameworks.add(_FRAMEWORK_DEPENDENCIES[key])

    return frameworks


def _read_requirements_txt(root_path: Path) -> set[str]:
    reqs = set()
    path = root_path / "requirements.txt"
    if not path.exists():
        return reqs

    for line in path.read_text(encoding="utf-8").splitlines():
        cleaned = line.strip()
        if not cleaned or cleaned.startswith("#"):
            continue
        package = cleaned.split()[0].split("==")[0].split(">=")[0].split("<=")[0]
        reqs.add(package.strip())
    return reqs


def _read_pyproject_dependencies(root_path: Path) -> set[str]:
    deps = set()
    path = root_path / "pyproject.toml"
    if not path.exists():
        return deps

    data = tomllib.loads(path.read_text(encoding="utf-8"))
    project = data.get("project", {})
    for item in project.get("dependencies", []) or []:
        deps.add(_normalize_dep_name(item))

    poetry = data.get("tool", {}).get("poetry", {})
    for name in (poetry.get("dependencies", {}) or {}).keys():
        deps.add(name)
    for name in (poetry.get("group", {}) or {}).get("dev", {}).get("dependencies", {}).keys():
        deps.add(name)

    return deps


def _read_setup_cfg_dependencies(root_path: Path) -> set[str]:
    deps = set()
    path = root_path / "setup.cfg"
    if not path.exists():
        return deps

    parser = configparser.ConfigParser()
    parser.read(path, encoding="utf-8")
    for section in ("options", "options.extras_require"):
        if not parser.has_section(section):
            continue
        for key, value in parser.items(section):
            if section == "options" and key != "install_requires":
                continue
            for line in value.splitlines():
                deps.add(_normalize_dep_name(line))
    return deps


def _read_setup_py_dependencies(root_path: Path) -> set[str]:
    deps = set()
    path = root_path / "setup.py"
    if not path.exists():
        return deps

    content = path.read_text(encoding="utf-8").lower()
    for dep_name in _FRAMEWORK_DEPENDENCIES.keys():
        if dep_name in content:
            deps.add(dep_name)
    return deps


def _read_pipfile_dependencies(root_path: Path) -> set[str]:
    deps = set()
    path = root_path / "Pipfile"
    if not path.exists():
        return deps

    content = path.read_text(encoding="utf-8")
    for line in content.splitlines():
        cleaned = line.strip()
        if cleaned.startswith("[") or cleaned.startswith("#") or "=" not in cleaned:
            continue
        name = cleaned.split("=", 1)[0].strip()
        if name:
            deps.add(name)
    return deps


def _read_package_json_dependencies(root_path: Path) -> set[str]:
    deps = set()
    path = root_path / "package.json"
    if not path.exists():
        return deps

    data = json.loads(path.read_text(encoding="utf-8"))
    for section in ("dependencies", "devDependencies", "peerDependencies"):
        deps.update((data.get(section, {}) or {}).keys())
    return deps


def _normalize_dep_name(raw: str) -> str:
    cleaned = raw.strip().split(";")[0].strip()
    if not cleaned:
        return ""
    for sep in ("==", ">=", "<=", "~=", ">", "<"):
        if sep in cleaned:
            cleaned = cleaned.split(sep, 1)[0].strip()
            break
    return cleaned
