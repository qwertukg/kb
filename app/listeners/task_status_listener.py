from __future__ import annotations

from sqlalchemy import event
from sqlalchemy.orm import Session, attributes

from app.models import Task
from app.services import tasks as tasks_service


@event.listens_for(Session, "after_flush")
def _track_task_status_changes(session: Session, flush_context) -> None:
    task_ids = session.info.setdefault("status_change_task_ids", set())
    for obj in session.dirty:
        if not isinstance(obj, Task):
            continue
        history = attributes.get_history(obj, "status_id")
        if history.has_changes() and history.deleted:
            if obj.id is not None:
                task_ids.add(obj.id)


@event.listens_for(Session, "after_commit")
def _run_task_status_observers(session: Session) -> None:
    task_ids = session.info.pop("status_change_task_ids", set())
    if not task_ids:
        return
    for task_id in task_ids:
        tasks_service.sent_to_llm(task_id)
