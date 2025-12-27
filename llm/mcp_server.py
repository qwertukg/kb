from __future__ import annotations

from agents import Agent, Runner
from agents.models.openai_provider import OpenAIProvider
from mcp.server.fastmcp import FastMCP

from .sandbox_tools import list_files, make_dir, read_file, run_git, write_file

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
) -> str:
    if not prompt:
        return ""
    if not api_key:
        raise ValueError("Не задан API_KEY в настройках.")
    if not model:
        raise ValueError("Не задан MODEL в настройках.")
    provider = OpenAIProvider(api_key=api_key)
    sandbox_note = (
        "Рабочая папка: sandbox. Для файлов используй list_files/read_file/write_file/make_dir. "
        "Для коммитов используй run_git."
    )
    combined_instructions = "\n\n".join(
        part for part in [instructions, sandbox_note] if part
    )
    agent = Agent(
        name="codex",
        instructions=combined_instructions or None,
        model=provider.get_model(model),
        tools=[list_files, make_dir, read_file, run_git, write_file],
    )
    result = await Runner.run(agent, prompt)
    return str(result.final_output or "")


def main() -> None:
    server.run(transport="stdio")


if __name__ == "__main__":
    main()
