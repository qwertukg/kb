from __future__ import annotations

from dataclasses import dataclass
import os
import subprocess
import tempfile

from ..models import Agent
from ..services import settings as settings_service


@dataclass(slots=True)
class CodexAgent:
    instructions: str
    api_key: str | None
    model: str | None

    def run(self, prompt: str) -> str | None:
        if not prompt:
            return None
        if not self.api_key:
            raise ValueError("Не задан API_KEY в настройках.")
        if not self.model:
            raise ValueError("Не задан MODEL в настройках.")
        full_prompt = prompt
        if self.instructions:
            full_prompt = f"{self.instructions}\n\n{prompt}"
        env = os.environ.copy()
        env["CODEX_API_KEY"] = self.api_key
        env["OPENAI_API_KEY"] = self.api_key
        env["CODEX_MODEL"] = self.model
        env["OPENAI_MODEL"] = self.model
        with tempfile.NamedTemporaryFile(delete=False) as output_file:
            output_path = output_file.name
        args = ["codex", "exec", "--color", "never", "--output-last-message", output_path]
        if self.model:
            args.extend(["-m", self.model])
        result = subprocess.run(
            args,
            input=full_prompt,
            text=True,
            capture_output=True,
            env=env,
            check=False,
        )
        if result.returncode != 0:
            error_text = result.stderr.strip() or "Codex CLI вернул ошибку."
            raise RuntimeError(error_text)
        try:
            with open(output_path, "r", encoding="utf-8") as output_file:
                response = output_file.read().strip()
        finally:
            os.unlink(output_path)
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


def _is_task_completed(response: str) -> bool:
    normalized = response.strip().lower()
    if not normalized:
        return False
    success_prefixes = (
        "готово",
        "сделал",
        "сделано",
        "выполнено",
        "выполнена",
        "задача выполнена",
        "done",
        "completed",
    )
    return any(normalized.startswith(prefix) for prefix in success_prefixes)


def run_task_prompt(
    agent: Agent,
    prompt: str,
    api_key: str | None,
    model: str | None,
) -> tuple[str | None, bool, str | None]:
    codex_agent = get_codex_agent(agent.id)
    if not codex_agent or codex_agent.api_key != api_key or codex_agent.model != model:
        codex_agent = register_codex_agent(agent, api_key, model)

    try:
        response = codex_agent.run(prompt)
    except Exception as exc:  # pragma: no cover - safety net
        error_message = f"Ошибка Codex-agent: {exc}"
        return None, False, error_message

    if not response:
        return None, False, "Codex-agent не вернул результат."

    return response, _is_task_completed(response), None
