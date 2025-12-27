from __future__ import annotations

import os
import sys

import sqlalchemy as sa

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
APP_ROOT = os.path.join(ROOT, "app")
if APP_ROOT not in sys.path:
    sys.path.insert(0, APP_ROOT)

from db import SessionLocal
from models import Agent, Board, Message, Role, Status, Task


def clear_data(session) -> None:
    session.execute(sa.delete(Message))
    session.execute(sa.delete(Task))
    session.execute(sa.delete(Agent))
    session.execute(sa.delete(Status))
    session.execute(sa.delete(Board))
    session.execute(sa.delete(Role))


def main() -> None:
    session = SessionLocal()
    try:
        clear_data(session)

        board = Board(name="Разработка")
        session.add(board)
        session.flush()

        statuses = [
            Status(name="Бэклог", position=1, color="#6c757d", board_id=board.id),
            Status(name="Разработка", position=2, color="#0d6efd", board_id=board.id),
            Status(name="Готово", position=3, color="#198754", board_id=board.id),
        ]
        session.add_all(statuses)
        session.flush()

        role = Role(
            name="Разработчик",
            instruction="Проектирование и реализация функционала, код-ревью, документация.",
        )
        session.add(role)
        session.flush()

        status_by_name = {status.name: status for status in statuses}

        agent = Agent(
            name="Колян",
            role_id=role.id,
            board_id=board.id,
            working_status_id=status_by_name["Разработка"].id,
            success_status_id=status_by_name["Готово"].id,
            error_status_id=status_by_name["Бэклог"].id,
            acceptance_criteria="Задача выполнена и результат сохранен в файл.",
            transfer_criteria="Ответ сохранен, файл доступен в sandbox.",
        )
        session.add(agent)
        session.flush()

        task = Task(
            title="скажи сколько сейчас времени и сохрани ответ в файл TIME.md",
            board_id=board.id,
            status_id=status_by_name["Разработка"].id,
        )
        session.add(task)
        session.flush()

        session.add(
            Message(
                task_id=task.id,
                author_id=agent.id,
                text="скажи сколько сейчас времени и сохрани ответ в файл TIME.md",
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
