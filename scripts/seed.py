from __future__ import annotations

import os
import sys

import sqlalchemy as sa

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app.db import SessionLocal
from app.models import Agent, Board, Message, Role, Status, Task


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
        board_lab = Board(name="Лаборатория генетики")
        session.add_all([board, board_lab])
        session.flush()

        statuses = [
            Status(name="Анализ", position=1, color="#0d6efd", board_id=board.id),
            Status(name="Разработка", position=2, color="#198754", board_id=board.id),
            Status(name="Тестирование", position=3, color="#fd7e14", board_id=board.id),
            Status(name="Эксплуатация", position=4, color="#dc3545", board_id=board.id),
            Status(name="Исследование", position=1, color="#6f42c1", board_id=board_lab.id),
            Status(name="Эксперимент", position=2, color="#20c997", board_id=board_lab.id),
            Status(name="Отчет", position=3, color="#0dcaf0", board_id=board_lab.id),
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

        status_by_name = {(status.board_id, status.name): status for status in statuses}
        role_by_name = {role.name: role for role in roles}

        agent_specs = [
            (
                "Александр Сафонов",
                "Аналитик",
                board.id,
                "Анализ",
                "Разработка",
                "Анализ",
                "Согласован бэклог, описаны пользовательские сценарии.",
                "Переданы уточнения по данным и SLA.",
            ),
            (
                "Петр Власов",
                "Аналитик",
                board.id,
                "Анализ",
                "Разработка",
                "Анализ",
                "Сформированы требования и бизнес-правила.",
                "Переданы макеты и справочники.",
            ),
            (
                "Николай Титов",
                "Java разработчик",
                board.id,
                "Разработка",
                "Тестирование",
                "Анализ",
                "Функционал реализован, покрыт тестами.",
                "Подготовлены миграции и инструкции деплоя.",
            ),
            (
                "Виталий Орлов",
                "Java разработчик",
                board.id,
                "Разработка",
                "Тестирование",
                "Анализ",
                "Готова интеграция со сторонними сервисами.",
                "Переданы схемы API и контракты.",
            ),
            (
                "Елена Морозова",
                "Тестировщик",
                board.id,
                "Тестирование",
                "Тестирование",
                "Разработка",
                "Проведена регрессия, критические дефекты закрыты.",
                "Сформирован отчет и чек-лист.",
            ),
            (
                "Ирина Лебедева",
                "Тестировщик",
                board.id,
                "Тестирование",
                "Тестирование",
                "Разработка",
                "Проверены граничные сценарии и нагрузки.",
                "Переданы результаты тестов.",
            ),
            (
                "Иван Платонов",
                "Эксплуатация",
                board.id,
                "Эксплуатация",
                "Тестирование",
                "Разработка",
                "Настроены алерты, дежурства и инструкции.",
                "Переданы runbook и доступы.",
            ),
            (
                "Сергей Кузнецов",
                "Девопс",
                board.id,
                "Эксплуатация",
                "Тестирование",
                "Разработка",
                "Настроен CI/CD, готово окружение.",
                "Переданы шаблоны инфраструктуры и мониторинг.",
            ),
            (
                "Мария Соколова",
                "Аналитик",
                board_lab.id,
                "Исследование",
                "Эксперимент",
                "Отчет",
                "Собраны требования по биобезопасности.",
                "Переданы протоколы наблюдений.",
            ),
            (
                "Артем Власов",
                "Java разработчик",
                board_lab.id,
                "Эксперимент",
                "Отчет",
                "Исследование",
                "Автоматизированы протоколы фиксации данных.",
                "Переданы скрипты и инструкции.",
            ),
            (
                "Полина Юдина",
                "Тестировщик",
                board_lab.id,
                "Отчет",
                "Отчет",
                "Эксперимент",
                "Согласованы критерии верификации экспериментов.",
                "Подготовлены результаты испытаний.",
            ),
        ]
        agent_by_name = {}
        for (
            name,
            role_name,
            board_id,
            working,
            success,
            error,
            acceptance,
            transfer,
        ) in agent_specs:
            agent = Agent(
                name=name,
                role_id=role_by_name[role_name].id,
                board_id=board_id,
                working_status_id=status_by_name[(board_id, working)].id,
                success_status_id=status_by_name[(board_id, success)].id,
                error_status_id=status_by_name[(board_id, error)].id,
                acceptance_criteria=acceptance,
                transfer_criteria=transfer,
            )
            session.add(agent)
            agent_by_name[name] = agent
        session.flush()

        task_specs = [
            ("Сбор требований по инкубаторам", board.id, "Анализ", "Александр Сафонов"),
            ("Описание бизнес-процессов выращивания", board.id, "Анализ", "Петр Власов"),
            ("Реализация сервиса расписаний кормления", board.id, "Разработка", "Николай Титов"),
            ("Интеграция датчиков температуры", board.id, "Разработка", "Виталий Орлов"),
            ("Стабилизация мониторинга и алертов", board.id, "Эксплуатация", "Сергей Кузнецов"),
            ("Регрессия: цикл инкубации", board.id, "Тестирование", "Елена Морозова"),
            ("Смоук: контроль температуры и влажности", board.id, "Тестирование", "Ирина Лебедева"),
            ("План экспериментов по скорости роста", board_lab.id, "Исследование", "Мария Соколова"),
            ("Настройка датчиков ДНК-контроля", board_lab.id, "Эксперимент", "Артем Власов"),
            ("Отчет по устойчивости эмбрионов", board_lab.id, "Отчет", "Полина Юдина"),
        ]
        for description, task_board_id, status_name, author_name in task_specs:
            task = Task(
                board_id=task_board_id,
                status_id=status_by_name[(task_board_id, status_name)].id,
            )
            session.add(task)
            session.flush()
            author = agent_by_name[author_name]
            session.add(Message(task_id=task.id, author_id=author.id, text=description))

        session.commit()
        print("Seed data applied.")
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


if __name__ == "__main__":
    main()
