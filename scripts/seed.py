from __future__ import annotations

import os
import sys

import sqlalchemy as sa

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app.db import SessionLocal
from app.models import Agent, Board, Role, Status, Task


def clear_data(session) -> None:
    session.execute(sa.delete(Task))
    session.execute(sa.delete(Agent))
    session.execute(sa.delete(Status))
    session.execute(sa.delete(Board))
    session.execute(sa.delete(Role))


def main() -> None:
    session = SessionLocal()
    try:
        clear_data(session)

        board = Board(name="Проект по выращиванию динозавров")
        session.add(board)
        session.flush()

        statuses = [
            Status(name="Анализ", position=1, color="#0d6efd", board_id=board.id),
            Status(name="Разработка", position=2, color="#198754", board_id=board.id),
            Status(name="Тестирование", position=3, color="#fd7e14", board_id=board.id),
            Status(name="Эксплуатация", position=4, color="#dc3545", board_id=board.id),
        ]
        session.add_all(statuses)

        roles = [
            Role(
                name="Аналитик",
                instruction="Сбор требований, описание сценариев, согласование ожиданий заказчика.",
            ),
            Role(
                name="Java разработчик",
                instruction="Проектирование и реализация сервисов, код-ревью, техническая документация.",
            ),
            Role(
                name="Тестировщик",
                instruction="Планирование тестов, регрессия, отчетность по дефектам.",
            ),
            Role(
                name="Эксплуатация",
                instruction="Мониторинг, управление инцидентами, эксплуатационные регламенты.",
            ),
            Role(
                name="Девопс",
                instruction="CI/CD, инфраструктура, автоматизация окружений, наблюдаемость.",
            ),
        ]
        session.add_all(roles)
        session.flush()

        status_by_name = {status.name: status for status in statuses}
        role_by_name = {role.name: role for role in roles}

        agent_specs = [
            (
                "Александр Сафонов",
                "Аналитик",
                "Анализ",
                "Разработка",
                "Анализ",
                "Согласован бэклог, описаны пользовательские сценарии.",
                "Переданы уточнения по данным и SLA.",
            ),
            (
                "Петр Власов",
                "Аналитик",
                "Анализ",
                "Разработка",
                "Анализ",
                "Сформированы требования и бизнес-правила.",
                "Переданы макеты и справочники.",
            ),
            (
                "Николай Титов",
                "Java разработчик",
                "Разработка",
                "Тестирование",
                "Анализ",
                "Функционал реализован, покрыт тестами.",
                "Подготовлены миграции и инструкции деплоя.",
            ),
            (
                "Виталий Орлов",
                "Java разработчик",
                "Разработка",
                "Тестирование",
                "Анализ",
                "Готова интеграция со сторонними сервисами.",
                "Переданы схемы API и контракты.",
            ),
            (
                "Елена Морозова",
                "Тестировщик",
                "Тестирование",
                "Тестирование",
                "Разработка",
                "Проведена регрессия, критические дефекты закрыты.",
                "Сформирован отчет и чек-лист.",
            ),
            (
                "Ирина Лебедева",
                "Тестировщик",
                "Тестирование",
                "Тестирование",
                "Разработка",
                "Проверены граничные сценарии и нагрузки.",
                "Переданы результаты тестов.",
            ),
            (
                "Иван Платонов",
                "Эксплуатация",
                "Эксплуатация",
                "Тестирование",
                "Разработка",
                "Настроены алерты, дежурства и инструкции.",
                "Переданы runbook и доступы.",
            ),
            (
                "Сергей Кузнецов",
                "Девопс",
                "Эксплуатация",
                "Тестирование",
                "Разработка",
                "Настроен CI/CD, готово окружение.",
                "Переданы шаблоны инфраструктуры и мониторинг.",
            ),
        ]
        for (
            name,
            role_name,
            working,
            success,
            error,
            acceptance,
            transfer,
        ) in agent_specs:
            session.add(
                Agent(
                    name=name,
                    role_id=role_by_name[role_name].id,
                    board_id=board.id,
                    working_status_id=status_by_name[working].id,
                    success_status_id=status_by_name[success].id,
                    error_status_id=status_by_name[error].id,
                    acceptance_criteria=acceptance,
                    transfer_criteria=transfer,
                )
            )

        task_specs = [
            ("Сбор требований по инкубаторам", "Анализ"),
            ("Описание бизнес-процессов выращивания", "Анализ"),
            ("Реализация сервиса расписаний кормления", "Разработка"),
            ("Интеграция датчиков температуры", "Разработка"),
            ("Стабилизация мониторинга и алертов", "Эксплуатация"),
            ("Регрессия: цикл инкубации", "Тестирование"),
            ("Смоук: контроль температуры и влажности", "Тестирование"),
        ]
        for description, status_name in task_specs:
            session.add(
                Task(
                    description=description,
                    board_id=board.id,
                    status_id=status_by_name[status_name].id,
                )
            )

        session.commit()
        print("Seed data applied.")
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
