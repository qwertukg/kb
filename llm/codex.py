from __future__ import annotations

from dataclasses import dataclass
import os
import re
import sys
import time

import anyio

from app.models import Agent
from app.services import settings as settings_service

LLM_TIMEOUT_SEC = int(os.getenv("LLM_TIMEOUT_SEC", "120"))
LLM_MAX_RETRIES = int(os.getenv("LLM_MAX_RETRIES", "4"))
LLM_RETRY_BACKOFF_SEC = float(os.getenv("LLM_RETRY_BACKOFF_SEC", "2"))


@dataclass(slots=True)
class CodexAgent:
    instructions: str
    api_key: str | None
    model: str | None

    def run(
        self,
        prompt: str,
        task_id: int | None = None,
        status_id: int | None = None,
    ) -> str | None:
        if not prompt:
            return None
        if not self.api_key:
            raise ValueError("Не задан API_KEY в настройках.")
        if not self.model:
            raise ValueError("Не задан MODEL в настройках.")
        response = _run_mcp_codex(
            prompt=prompt,
            instructions=self.instructions,
            api_key=self.api_key,
            model=self.model,
            task_id=task_id,
            status_id=status_id,
        )
        return response or None


def build_codex_instructions(agent: Agent) -> str:
    parts: list[str] = []
    base_instructions = settings_service.get_parameter_value("INSTRUCTIONS")
    if base_instructions:
        parts.append(base_instructions.strip())
    if agent.role and agent.role.instruction:
        parts.append(agent.role.instruction.strip())
    if agent.acceptance_criteria:
        parts.append(f"Критерии приемки: {agent.acceptance_criteria.strip()}")
    if agent.transfer_criteria:
        parts.append(f"Критерии передачи: {agent.transfer_criteria.strip()}")
    return "\n".join(parts).strip()


_CODEX_AGENTS: dict[int, CodexAgent] = {}


def register_codex_agent(agent: Agent, api_key: str | None, model: str | None) -> CodexAgent:
    codex_agent = CodexAgent(
        instructions=build_codex_instructions(agent),
        api_key=api_key,
        model=model,
    )
    _CODEX_AGENTS[agent.id] = codex_agent
    return codex_agent


def get_codex_agent(agent_id: int) -> CodexAgent | None:
    return _CODEX_AGENTS.get(agent_id)


def remove_codex_agent(agent_id: int) -> None:
    _CODEX_AGENTS.pop(agent_id, None)


def write_codex_config(config_text: str | None) -> None:
    if not config_text:
        return
    codex_home = os.getenv("CODEX_HOME", os.path.expanduser("~/.codex"))
    os.makedirs(codex_home, exist_ok=True)
    config_path = os.path.join(codex_home, "config.toml")
    with open(config_path, "w", encoding="utf-8") as output_file:
        output_file.write(config_text)


def _extract_tool_text(result) -> str:
    structured = getattr(result, "structuredContent", None)
    if isinstance(structured, dict):
        text = structured.get("text")
        if isinstance(text, str) and text.strip():
            return text.strip()
    if structured is not None:
        print(f"[codex] structuredContent={structured}")
    parts: list[str] = []
    for block in result.content or []:
        text = getattr(block, "text", None)
        if isinstance(text, str) and text.strip():
            parts.append(text)
        elif text is not None:
            print(f"[codex] empty text block: {text!r}")
        else:
            print(f"[codex] non-text block: {block!r}")
    return "\n".join(parts).strip()


def _run_mcp_codex(
    *,
    prompt: str,
    instructions: str | None,
    api_key: str,
    model: str,
    task_id: int | None = None,
    status_id: int | None = None,
) -> str | None:
    try:
        from mcp.client.session import ClientSession
        from mcp.client.stdio import StdioServerParameters, stdio_client
    except ModuleNotFoundError as exc:  # pragma: no cover - environment-specific
        raise RuntimeError(
            "Пакет 'mcp' не установлен. Установите зависимости или запускайте через Docker."
        ) from exc

    async def _run() -> str | None:
        server_params = StdioServerParameters(
            command=sys.executable,
            args=["-m", "llm.mcp_server"],
        )
        async with stdio_client(server_params) as streams:
            async with ClientSession(*streams) as session:
                await session.initialize()
                with anyio.fail_after(LLM_TIMEOUT_SEC):
                    result = await session.call_tool(
                        "run_codex",
                        {
                            "prompt": prompt,
                            "instructions": instructions or "",
                            "api_key": api_key,
                            "model": model,
                            "task_id": task_id,
                            "status_id": status_id,
                        },
                    )
        if getattr(result, "isError", False):
            message = _extract_tool_text(result) or "Codex MCP вернул ошибку."
            raise RuntimeError(message)
        response_text = _extract_tool_text(result)
        return response_text or None

    last_error: Exception | None = None
    for attempt in range(LLM_MAX_RETRIES + 1):
        try:
            return anyio.run(_run)
        except Exception as exc:
            last_error = exc
            if attempt < LLM_MAX_RETRIES:
                time.sleep(LLM_RETRY_BACKOFF_SEC * (attempt + 1))
                continue
            raise

    if last_error:
        raise last_error
    return None


def _extract_agent_status(response: str) -> tuple[str, bool | None]:
    matches = list(re.finditer(r"STATUS:\s*(SUCCESS|ERROR)", response, re.IGNORECASE))
    if not matches:
        return response, None
    last_match = matches[-1]
    status_value = last_match.group(1).upper()
    cleaned = (response[: last_match.start()] + response[last_match.end() :]).strip()
    cleaned = re.sub(r"\n\s*\n", "\n", cleaned).strip()
    if status_value == "SUCCESS":
        return cleaned, True
    if status_value == "ERROR":
        return cleaned, False
    return cleaned, None


def run_task_prompt(
    agent: Agent,
    prompt: str,
    api_key: str | None,
    model: str | None,
    task_id: int | None = None,
    status_id: int | None = None,
) -> tuple[str | None, bool, str | None]:
    codex_agent = get_codex_agent(agent.id)
    if not codex_agent or codex_agent.api_key != api_key or codex_agent.model != model:
        codex_agent = register_codex_agent(agent, api_key, model)

    status_instruction = (
        "\n\nВ конце ответа добавь строку строго в формате:\n"
        "STATUS: SUCCESS\n"
        "или\n"
        "STATUS: ERROR\n"
    )
    try:
        response = codex_agent.run(
            f"{prompt}{status_instruction}",
            task_id=task_id,
            status_id=status_id,
        )
    except Exception as exc:  # pragma: no cover - safety net
        error_message = f"Ошибка Codex-agent: {exc}"
        return None, False, error_message

    if not response:
        print(f"[codex] empty response for agent_id={agent.id}")
        return None, False, "Codex-agent не вернул результат."

    cleaned_response, is_completed = _extract_agent_status(response)
    if is_completed is None:
        print("[codex] Агент не указал статус, используем ERROR.")
        return cleaned_response, False, None
    return cleaned_response, is_completed, None
