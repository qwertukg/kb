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
from models import Agent, Column, Message, Project, Role, Status, Task


def clear_data(session) -> None:
    session.execute(sa.delete(Message))
    session.execute(sa.delete(Task))
    session.execute(sa.delete(Agent))
    session.execute(sa.delete(Column))
    session.execute(sa.delete(Status))
    session.execute(sa.delete(Project))
    session.execute(sa.delete(Role))


def main() -> None:
    session = SessionLocal()
    try:
        clear_data(session)

        project = Project(name="ИС Библиотека")
        session.add(project)
        session.flush()

        statuses = [
            Status(name="Бэклог", color="#6c757d", project_id=project.id),
            Status(name="Разработка", color="#0d6efd", project_id=project.id),
            Status(name="Тестирование", color="#ffc107", project_id=project.id),
            Status(name="Готово", color="#198754", project_id=project.id),
        ]
        session.add_all(statuses)
        session.flush()
        session.add_all(
            [
                Column(position=1, project_id=project.id, status_id=statuses[0].id),
                Column(position=2, project_id=project.id, status_id=statuses[1].id),
                Column(position=3, project_id=project.id, status_id=statuses[2].id),
                Column(position=4, project_id=project.id, status_id=statuses[3].id),
            ]
        )

        role = Role(
            name="Разработчик",
            instruction="- пишешь код на Python",
        )
        session.add(role)
        session.flush()
        tester_role = Role(
            name="Тестировщик",
            instruction="- пишешь юнит тесты (если нужно)\n- пишешь интеграционные тесты (если нужно)\n- пишешь UI тесты (если нужно)\n ",
        )
        session.add(tester_role)
        session.flush()

        status_by_name = {status.name: status for status in statuses}

        agent = Agent(
            name="Колян",
            role_id=role.id,
            project_id=project.id,
            working_status_id=status_by_name["Разработка"].id,
            success_status_id=status_by_name["Тестирование"].id,
            error_status_id=status_by_name["Бэклог"].id,
            acceptance_criteria="- задача относится к теме проекта",
            transfer_criteria="- код по задаче написан\n- список измененных/созданных файлов в ответе",
        )
        session.add(agent)
        session.flush()

        tester = Agent(
            name="Леночка",
            role_id=tester_role.id,
            project_id=project.id,
            working_status_id=status_by_name["Тестирование"].id,
            success_status_id=status_by_name["Готово"].id,
            error_status_id=status_by_name["Бэклог"].id,
            acceptance_criteria="- задача относится к тестированию\n- код по задаче есть",
            transfer_criteria="- тесты по задаче выполнены\n- результат проверки описан в ответе",
        )
        session.add(tester)
        session.flush()

        task = Task(
            title="Тест времени",
            project_id=project.id,
            status_id=status_by_name["Бэклог"].id,
        )
        session.add(task)
        session.flush()

        session.add(
            Message(
                task_id=task.id,
                author_id=agent.id,
                text="Напиши программу которая возвращает сегодняшнюю дату",
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
