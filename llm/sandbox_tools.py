from __future__ import annotations

import os
from pathlib import Path
import subprocess

try:
    from agents import function_tool as tool
except Exception:  # pragma: no cover - fallback for older/newer agents
    try:
        from agents.tool import function_tool as tool
    except Exception:  # pragma: no cover - final fallback
        from agents import tool as tool_module

        tool = getattr(tool_module, "tool", None) or getattr(tool_module, "function_tool", None)
        if tool is None or not callable(tool):
            raise ImportError("Cannot resolve tool decorator from agents package.")


_SANDBOX_DIR = Path(
    os.getenv("CODEX_SANDBOX_DIR", str(Path.cwd() / "sandbox"))
).resolve()


def _ensure_sandbox_dir() -> Path:
    _SANDBOX_DIR.mkdir(parents=True, exist_ok=True)
    return _SANDBOX_DIR


def _resolve_path(path: str) -> Path:
    if not path:
        path = "."
    candidate = Path(path)
    if candidate.is_absolute():
        raise ValueError("Absolute paths are not allowed.")
    base = _ensure_sandbox_dir()
    resolved = (base / candidate).resolve()
    if resolved != base and base not in resolved.parents:
        raise ValueError("Path escapes sandbox.")
    return resolved


def _ensure_git_repo() -> None:
    base = _ensure_sandbox_dir()
    if not (base / ".git").exists():
        subprocess.run(
            ["git", "init"],
            cwd=str(base),
            check=True,
            capture_output=True,
            text=True,
        )
    _ensure_git_config(base)


def _ensure_git_config(base: Path) -> None:
    name_result = subprocess.run(
        ["git", "config", "--get", "user.name"],
        cwd=str(base),
        capture_output=True,
        text=True,
    )
    email_result = subprocess.run(
        ["git", "config", "--get", "user.email"],
        cwd=str(base),
        capture_output=True,
        text=True,
    )
    if name_result.returncode != 0:
        subprocess.run(
            ["git", "config", "user.name", "codex-agent"],
            cwd=str(base),
            check=False,
            capture_output=True,
            text=True,
        )
    if email_result.returncode != 0:
        subprocess.run(
            ["git", "config", "user.email", "codex-agent@localhost"],
            cwd=str(base),
            check=False,
            capture_output=True,
            text=True,
        )


@tool
def list_files(path: str = ".") -> str:
    """List files in the sandbox directory."""
    target = _resolve_path(path)
    if not target.exists():
        raise ValueError("Path does not exist.")
    if target.is_file():
        return target.name
    entries = []
    for entry in sorted(target.iterdir(), key=lambda item: item.name):
        suffix = "/" if entry.is_dir() else ""
        entries.append(f"{entry.name}{suffix}")
    return "\n".join(entries)


@tool
def read_file(path: str) -> str:
    """Read a UTF-8 text file from the sandbox directory."""
    target = _resolve_path(path)
    if not target.is_file():
        raise ValueError("File does not exist.")
    return target.read_text(encoding="utf-8")


@tool
def write_file(path: str, content: str, append: bool = False) -> str:
    """Write a UTF-8 text file into the sandbox directory."""
    target = _resolve_path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    mode = "a" if append else "w"
    with open(target, mode, encoding="utf-8") as output_file:
        output_file.write(content)
    written_path = target.relative_to(_SANDBOX_DIR)
    return f"Wrote {len(content)} bytes to {written_path}"


@tool
def make_dir(path: str) -> str:
    """Create a directory inside the sandbox."""
    target = _resolve_path(path)
    target.mkdir(parents=True, exist_ok=True)
    return f"Created {target.relative_to(_SANDBOX_DIR)}"


@tool
def run_git(args: list[str]) -> str:
    """Run a git command inside the sandbox directory."""
    if not isinstance(args, list) or not all(isinstance(item, str) for item in args):
        raise ValueError("args must be a list of strings.")
    _ensure_git_repo()
    result = subprocess.run(
        ["git", *args],
        cwd=str(_SANDBOX_DIR),
        capture_output=True,
        text=True,
    )
    output = (result.stdout + result.stderr).strip()
    if result.returncode != 0:
        raise RuntimeError(output or f"git exited with {result.returncode}")
    return output or "ok"
