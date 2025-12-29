from __future__ import annotations

import os

import inspect
import os

from agents import Agent, Runner
from agents.models.openai_provider import OpenAIProvider
from mcp.server.fastmcp import FastMCP

from .sandbox_tools import list_files, make_dir, read_file, run_cmd, run_git, write_file

server = FastMCP("kb-codex")


@server.tool(
    name="run_codex",
    description="Run a Codex prompt via OpenAI Agents SDK.",
)
async def run_codex(
    prompt: str,
    instructions: str | None = None,
    api_key: str | None = None,
    model: str | None = None,
    task_id: int | None = None,
    status_id: int | None = None,
) -> str:
    if not prompt:
        return ""
    if not api_key:
        raise ValueError("Не задан API_KEY в настройках.")
    if not model:
        raise ValueError("Не задан MODEL в настройках.")
    timeout = float(os.getenv("LLM_TIMEOUT_SEC", "120"))
    max_retries = int(os.getenv("LLM_MAX_RETRIES", "4"))
    provider_kwargs = {"api_key": api_key}
    provider_params = inspect.signature(OpenAIProvider).parameters
    if "timeout" in provider_params:
        provider_kwargs["timeout"] = timeout
    if "max_retries" in provider_params:
        provider_kwargs["max_retries"] = max_retries
    provider = OpenAIProvider(**provider_kwargs)
    sandbox_note = (
        "Рабочая папка: sandbox. Для файлов используй list_files/read_file/write_file/make_dir. "
        "Для запуска команд используй run_cmd, для коммитов используй run_git."
    )
    combined_instructions = "\n\n".join(
        part for part in [instructions, sandbox_note] if part
    )
    previous_task_id = os.environ.get("CODEX_TASK_ID")
    previous_status_id = os.environ.get("CODEX_STATUS_ID")
    if task_id is not None:
        os.environ["CODEX_TASK_ID"] = str(task_id)
    else:
        os.environ.pop("CODEX_TASK_ID", None)
    if status_id is not None:
        os.environ["CODEX_STATUS_ID"] = str(status_id)
    else:
        os.environ.pop("CODEX_STATUS_ID", None)

    try:
        agent = Agent(
            name="codex",
            instructions=combined_instructions or None,
            model=provider.get_model(model),
            tools=[list_files, make_dir, read_file, run_cmd, run_git, write_file],
        )
        result = await Runner.run(agent, prompt)
    finally:
        if previous_task_id is not None:
            os.environ["CODEX_TASK_ID"] = previous_task_id
        else:
            os.environ.pop("CODEX_TASK_ID", None)
        if previous_status_id is not None:
            os.environ["CODEX_STATUS_ID"] = previous_status_id
        else:
            os.environ.pop("CODEX_STATUS_ID", None)
    return str(result.final_output or "")


def main() -> None:
    server.run(transport="stdio")


if __name__ == "__main__":
    main()
