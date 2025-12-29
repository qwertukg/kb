from __future__ import annotations

from sqlalchemy import event
from sqlalchemy.orm import Session, attributes

from app.models import Task
from app.services import tasks as tasks_service
from app.socketio import socketio


@event.listens_for(Session, "after_flush")
def _track_task_status_changes(session: Session, flush_context) -> None:
    task_ids = session.info.setdefault("status_change_task_ids", {})
    for obj in session.dirty:
        if not isinstance(obj, Task):
            continue
        history = attributes.get_history(obj, "status_id")
        if history.has_changes() and history.deleted:
            if obj.id is not None:
                new_status_id = history.added[-1] if history.added else obj.status_id
                task_ids[obj.id] = new_status_id


@event.listens_for(Session, "after_commit")
def _run_task_status_observers(session: Session) -> None:
    task_ids = session.info.pop("status_change_task_ids", {})
    if not task_ids:
        return
    for task_id, status_id in task_ids.items():
        socketio.emit(
            "task_status_changed",
            {"task_id": task_id, "status_id": status_id},
        )
        socketio.start_background_task(_run_llm_for_task, task_id)


def _run_llm_for_task(task_id: int) -> None:
    try:
        tasks_service.sent_to_llm(task_id)
    except Exception as exc:  # pragma: no cover - фоновые ошибки
        print(f"[listener] Ошибка LLM для задачи {task_id}: {exc}")
