from __future__ import annotations

from flask import Blueprint, flash, redirect, render_template, request, url_for
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from .db import SessionLocal
from .models import Agent, Board, Role, Status, Task

bp = Blueprint("roles", __name__)


@bp.get("/")
def index() -> str:
    session = SessionLocal()
    board_id = request.args.get("board_id", type=int)
    current_board_name = None
    statuses = (
        session.execute(
            select(Status)
            .options(selectinload(Status.working_agents), selectinload(Status.board))
            .order_by(Status.board_id, Status.position)
        )
        .scalars()
        .all()
    )
    if board_id:
        statuses = [status for status in statuses if status.board_id == board_id]
        board = session.get(Board, board_id)
        current_board_name = board.name if board else None
    task_query = select(Task).order_by(Task.id)
    if board_id:
        task_query = task_query.where(Task.board_id == board_id)
    tasks = session.execute(task_query).scalars().all()

    tasks_by_status: dict[int, list[tuple[Task, Agent | None]]] = {}
    free_agents_by_status: dict[int, list[Agent]] = {}
    statuses_by_board: dict[int, list[Status]] = {}
    for status in statuses:
        agents = sorted(status.working_agents, key=lambda agent: agent.name.lower())
        status_tasks = [task for task in tasks if task.status_id == status.id]
        assigned: list[tuple[Task, Agent | None]] = []
        free_agents = agents.copy()
        for task in status_tasks:
            agent = free_agents.pop(0) if free_agents else None
            assigned.append((task, agent))
        tasks_by_status[status.id] = assigned
        free_agents_by_status[status.id] = free_agents
        statuses_by_board.setdefault(status.board_id, []).append(status)

    return render_template(
        "home.html",
        statuses_by_board=statuses_by_board,
        tasks_by_status=tasks_by_status,
        free_agents_by_status=free_agents_by_status,
        current_board_name=current_board_name,
    )


@bp.get("/roles")
def list_roles() -> str:
    session = SessionLocal()
    roles = session.execute(select(Role).order_by(Role.name)).scalars().all()
    return render_template("roles/list.html", roles=roles)


@bp.get("/roles/new")
def new_role() -> str:
    return render_template("roles/form.html", role=None)


@bp.post("/roles")
def create_role() -> str:
    name = request.form.get("name", "").strip()
    instruction = request.form.get("instruction", "").strip() or None

    if not name:
        flash("Имя обязательно.", "danger")
        return render_template("roles/form.html", role=None, name=name, instruction=instruction)

    session = SessionLocal()
    exists = session.execute(select(Role).where(Role.name == name)).scalar_one_or_none()
    if exists:
        flash("Роль с таким именем уже существует.", "danger")
        return render_template("roles/form.html", role=None, name=name, instruction=instruction)

    role = Role(name=name, instruction=instruction)
    session.add(role)
    session.commit()
    flash("Роль создана.", "success")
    return redirect(url_for("roles.list_roles"))


@bp.get("/roles/<int:role_id>/edit")
def edit_role(role_id: int) -> str:
    session = SessionLocal()
    role = session.get(Role, role_id)
    if not role:
        flash("Роль не найдена.", "danger")
        return redirect(url_for("roles.list_roles"))

    return render_template("roles/form.html", role=role)


@bp.post("/roles/<int:role_id>")
def update_role(role_id: int) -> str:
    name = request.form.get("name", "").strip()
    instruction = request.form.get("instruction", "").strip() or None

    session = SessionLocal()
    role = session.get(Role, role_id)
    if not role:
        flash("Роль не найдена.", "danger")
        return redirect(url_for("roles.list_roles"))

    if not name:
        flash("Имя обязательно.", "danger")
        return render_template("roles/form.html", role=role, name=name, instruction=instruction)

    exists = (
        session.execute(select(Role).where(Role.name == name, Role.id != role_id))
        .scalar_one_or_none()
    )
    if exists:
        flash("Роль с таким именем уже существует.", "danger")
        return render_template("roles/form.html", role=role, name=name, instruction=instruction)

    role.name = name
    role.instruction = instruction
    session.commit()
    flash("Роль обновлена.", "success")
    return redirect(url_for("roles.list_roles"))


@bp.post("/roles/<int:role_id>/delete")
def delete_role(role_id: int) -> str:
    session = SessionLocal()
    role = session.get(Role, role_id)
    if not role:
        flash("Роль не найдена.", "danger")
        return redirect(url_for("roles.list_roles"))

    session.delete(role)
    session.commit()
    flash("Роль удалена.", "success")
    return redirect(url_for("roles.list_roles"))


@bp.get("/agents")
def list_agents() -> str:
    session = SessionLocal()
    agents = (
        session.execute(
            select(Agent)
            .options(
                selectinload(Agent.role),
                selectinload(Agent.board),
                selectinload(Agent.success_status),
                selectinload(Agent.error_status),
                selectinload(Agent.working_status),
            )
            .order_by(Agent.name)
        )
        .scalars()
        .all()
    )
    return render_template("agents/list.html", agents=agents)


@bp.get("/agents/new")
def new_agent() -> str:
    session = SessionLocal()
    roles = session.execute(select(Role).order_by(Role.name)).scalars().all()
    boards = session.execute(select(Board).order_by(Board.name)).scalars().all()
    statuses = session.execute(
        select(Status).options(selectinload(Status.board)).order_by(Status.board_id, Status.position)
    ).scalars().all()
    return render_template(
        "agents/form.html", agent=None, roles=roles, boards=boards, statuses=statuses
    )


@bp.post("/agents")
def create_agent() -> str:
    name = request.form.get("name", "").strip()
    role_id = request.form.get("role_id", "").strip()
    board_id = request.form.get("board_id", "").strip()
    success_status_id = request.form.get("success_status_id", "").strip()
    error_status_id = request.form.get("error_status_id", "").strip()
    working_status_id = request.form.get("working_status_id", "").strip()
    acceptance_criteria = request.form.get("acceptance_criteria", "").strip() or None
    transfer_criteria = request.form.get("transfer_criteria", "").strip() or None

    session = SessionLocal()
    roles = session.execute(select(Role).order_by(Role.name)).scalars().all()
    boards = session.execute(select(Board).order_by(Board.name)).scalars().all()
    statuses = session.execute(
        select(Status).options(selectinload(Status.board)).order_by(Status.board_id, Status.position)
    ).scalars().all()

    if (
        not name
        or not role_id
        or not board_id
        or not success_status_id
        or not error_status_id
        or not working_status_id
    ):
        flash("Имя, роль, доска и статусы обязательны.", "danger")
        return render_template(
            "agents/form.html",
            agent=None,
            roles=roles,
            boards=boards,
            statuses=statuses,
            name=name,
            role_id=role_id,
            board_id=board_id,
            success_status_id=success_status_id,
            error_status_id=error_status_id,
            working_status_id=working_status_id,
            acceptance_criteria=acceptance_criteria,
            transfer_criteria=transfer_criteria,
        )

    role = session.get(Role, int(role_id))
    if not role:
        flash("Роль не найдена.", "danger")
        return render_template(
            "agents/form.html",
            agent=None,
            roles=roles,
            boards=boards,
            statuses=statuses,
            name=name,
            role_id=role_id,
            board_id=board_id,
            success_status_id=success_status_id,
            error_status_id=error_status_id,
            working_status_id=working_status_id,
            acceptance_criteria=acceptance_criteria,
            transfer_criteria=transfer_criteria,
        )

    board = session.get(Board, int(board_id))
    if not board:
        flash("Доска не найдена.", "danger")
        return render_template(
            "agents/form.html",
            agent=None,
            roles=roles,
            boards=boards,
            statuses=statuses,
            name=name,
            role_id=role_id,
            board_id=board_id,
            success_status_id=success_status_id,
            error_status_id=error_status_id,
            working_status_id=working_status_id,
            acceptance_criteria=acceptance_criteria,
            transfer_criteria=transfer_criteria,
        )

    success_status = session.get(Status, int(success_status_id))
    error_status = session.get(Status, int(error_status_id))
    working_status = session.get(Status, int(working_status_id))
    if (
        not success_status
        or not error_status
        or not working_status
        or success_status.board_id != board.id
        or error_status.board_id != board.id
        or working_status.board_id != board.id
    ):
        flash("Статусы должны принадлежать выбранной доске.", "danger")
        return render_template(
            "agents/form.html",
            agent=None,
            roles=roles,
            boards=boards,
            statuses=statuses,
            name=name,
            role_id=role_id,
            board_id=board_id,
            success_status_id=success_status_id,
            error_status_id=error_status_id,
            working_status_id=working_status_id,
            acceptance_criteria=acceptance_criteria,
            transfer_criteria=transfer_criteria,
        )

    agent = Agent(
        name=name,
        role_id=role.id,
        board_id=board.id,
        success_status_id=success_status.id,
        error_status_id=error_status.id,
        working_status_id=working_status.id,
        acceptance_criteria=acceptance_criteria,
        transfer_criteria=transfer_criteria,
    )
    session.add(agent)
    session.commit()
    flash("Агент создан.", "success")
    return redirect(url_for("roles.list_agents"))


@bp.get("/agents/<int:agent_id>/edit")
def edit_agent(agent_id: int) -> str:
    session = SessionLocal()
    agent = session.get(Agent, agent_id)
    if not agent:
        flash("Агент не найден.", "danger")
        return redirect(url_for("roles.list_agents"))

    roles = session.execute(select(Role).order_by(Role.name)).scalars().all()
    boards = session.execute(select(Board).order_by(Board.name)).scalars().all()
    statuses = session.execute(
        select(Status).options(selectinload(Status.board)).order_by(Status.board_id, Status.position)
    ).scalars().all()
    return render_template(
        "agents/form.html", agent=agent, roles=roles, boards=boards, statuses=statuses
    )


@bp.post("/agents/<int:agent_id>")
def update_agent(agent_id: int) -> str:
    name = request.form.get("name", "").strip()
    role_id = request.form.get("role_id", "").strip()
    board_id = request.form.get("board_id", "").strip()
    success_status_id = request.form.get("success_status_id", "").strip()
    error_status_id = request.form.get("error_status_id", "").strip()
    working_status_id = request.form.get("working_status_id", "").strip()
    acceptance_criteria = request.form.get("acceptance_criteria", "").strip() or None
    transfer_criteria = request.form.get("transfer_criteria", "").strip() or None

    session = SessionLocal()
    agent = session.get(Agent, agent_id)
    if not agent:
        flash("Агент не найден.", "danger")
        return redirect(url_for("roles.list_agents"))

    roles = session.execute(select(Role).order_by(Role.name)).scalars().all()
    boards = session.execute(select(Board).order_by(Board.name)).scalars().all()
    statuses = session.execute(
        select(Status).options(selectinload(Status.board)).order_by(Status.board_id, Status.position)
    ).scalars().all()

    if (
        not name
        or not role_id
        or not board_id
        or not success_status_id
        or not error_status_id
        or not working_status_id
    ):
        flash("Имя, роль, доска и статусы обязательны.", "danger")
        return render_template(
            "agents/form.html",
            agent=agent,
            roles=roles,
            boards=boards,
            statuses=statuses,
            name=name,
            role_id=role_id,
            board_id=board_id,
            success_status_id=success_status_id,
            error_status_id=error_status_id,
            working_status_id=working_status_id,
            acceptance_criteria=acceptance_criteria,
            transfer_criteria=transfer_criteria,
        )

    role = session.get(Role, int(role_id))
    if not role:
        flash("Роль не найдена.", "danger")
        return render_template(
            "agents/form.html",
            agent=agent,
            roles=roles,
            boards=boards,
            statuses=statuses,
            name=name,
            role_id=role_id,
            board_id=board_id,
            success_status_id=success_status_id,
            error_status_id=error_status_id,
            working_status_id=working_status_id,
            acceptance_criteria=acceptance_criteria,
            transfer_criteria=transfer_criteria,
        )

    board = session.get(Board, int(board_id))
    if not board:
        flash("Доска не найдена.", "danger")
        return render_template(
            "agents/form.html",
            agent=agent,
            roles=roles,
            boards=boards,
            statuses=statuses,
            name=name,
            role_id=role_id,
            board_id=board_id,
            success_status_id=success_status_id,
            error_status_id=error_status_id,
            working_status_id=working_status_id,
            acceptance_criteria=acceptance_criteria,
            transfer_criteria=transfer_criteria,
        )

    success_status = session.get(Status, int(success_status_id))
    error_status = session.get(Status, int(error_status_id))
    working_status = session.get(Status, int(working_status_id))
    if (
        not success_status
        or not error_status
        or not working_status
        or success_status.board_id != board.id
        or error_status.board_id != board.id
        or working_status.board_id != board.id
    ):
        flash("Статусы должны принадлежать выбранной доске.", "danger")
        return render_template(
            "agents/form.html",
            agent=agent,
            roles=roles,
            boards=boards,
            statuses=statuses,
            name=name,
            role_id=role_id,
            board_id=board_id,
            success_status_id=success_status_id,
            error_status_id=error_status_id,
            working_status_id=working_status_id,
            acceptance_criteria=acceptance_criteria,
            transfer_criteria=transfer_criteria,
        )

    agent.name = name
    agent.role_id = role.id
    agent.board_id = board.id
    agent.success_status_id = success_status.id
    agent.error_status_id = error_status.id
    agent.working_status_id = working_status.id
    agent.acceptance_criteria = acceptance_criteria
    agent.transfer_criteria = transfer_criteria
    session.commit()
    flash("Агент обновлен.", "success")
    return redirect(url_for("roles.list_agents"))


@bp.post("/agents/<int:agent_id>/delete")
def delete_agent(agent_id: int) -> str:
    session = SessionLocal()
    agent = session.get(Agent, agent_id)
    if not agent:
        flash("Агент не найден.", "danger")
        return redirect(url_for("roles.list_agents"))

    session.delete(agent)
    session.commit()
    flash("Агент удален.", "success")
    return redirect(url_for("roles.list_agents"))


@bp.get("/boards")
def list_boards() -> str:
    session = SessionLocal()
    boards = (
        session.execute(select(Board).options(selectinload(Board.statuses)).order_by(Board.name))
        .scalars()
        .all()
    )
    return render_template("boards/list.html", boards=boards)


@bp.get("/boards/new")
def new_board() -> str:
    return render_template("boards/form.html", board=None)


@bp.post("/boards")
def create_board() -> str:
    name = request.form.get("name", "").strip()

    if not name:
        flash("Имя обязательно.", "danger")
        return render_template("boards/form.html", board=None, name=name)

    session = SessionLocal()
    exists = session.execute(select(Board).where(Board.name == name)).scalar_one_or_none()
    if exists:
        flash("Доска с таким именем уже существует.", "danger")
        return render_template("boards/form.html", board=None, name=name)

    board = Board(name=name)
    session.add(board)
    session.commit()
    flash("Доска создана.", "success")
    return redirect(url_for("roles.list_boards"))


@bp.get("/boards/<int:board_id>/edit")
def edit_board(board_id: int) -> str:
    session = SessionLocal()
    board = session.get(Board, board_id)
    if not board:
        flash("Доска не найдена.", "danger")
        return redirect(url_for("roles.list_boards"))

    return render_template("boards/form.html", board=board)


@bp.post("/boards/<int:board_id>")
def update_board(board_id: int) -> str:
    name = request.form.get("name", "").strip()

    session = SessionLocal()
    board = session.get(Board, board_id)
    if not board:
        flash("Доска не найдена.", "danger")
        return redirect(url_for("roles.list_boards"))

    if not name:
        flash("Имя обязательно.", "danger")
        return render_template("boards/form.html", board=board, name=name)

    exists = (
        session.execute(select(Board).where(Board.name == name, Board.id != board_id))
        .scalar_one_or_none()
    )
    if exists:
        flash("Доска с таким именем уже существует.", "danger")
        return render_template("boards/form.html", board=board, name=name)

    board.name = name
    session.commit()
    flash("Доска обновлена.", "success")
    return redirect(url_for("roles.list_boards"))


@bp.post("/boards/<int:board_id>/delete")
def delete_board(board_id: int) -> str:
    session = SessionLocal()
    board = session.get(Board, board_id)
    if not board:
        flash("Доска не найдена.", "danger")
        return redirect(url_for("roles.list_boards"))

    session.delete(board)
    session.commit()
    flash("Доска удалена.", "success")
    return redirect(url_for("roles.list_boards"))


@bp.get("/statuses")
def list_statuses() -> str:
    session = SessionLocal()
    statuses = (
        session.execute(select(Status).options(selectinload(Status.board)).order_by(Status.position))
        .scalars()
        .all()
    )
    return render_template("statuses/list.html", statuses=statuses)


@bp.get("/statuses/new")
def new_status() -> str:
    session = SessionLocal()
    boards = session.execute(select(Board).order_by(Board.name)).scalars().all()
    return render_template("statuses/form.html", status=None, boards=boards)


@bp.post("/statuses")
def create_status() -> str:
    name = request.form.get("name", "").strip()
    position = request.form.get("position", "").strip()
    color = request.form.get("color", "").strip()
    board_id = request.form.get("board_id", "").strip()

    session = SessionLocal()
    boards = session.execute(select(Board).order_by(Board.name)).scalars().all()

    if not name or not position or not board_id:
        flash("Имя, позиция и доска обязательны.", "danger")
        return render_template(
            "statuses/form.html",
            status=None,
            boards=boards,
            name=name,
            position=position,
            color=color,
            board_id=board_id,
        )

    board = session.get(Board, int(board_id))
    if not board:
        flash("Доска не найдена.", "danger")
        return render_template(
            "statuses/form.html",
            status=None,
            boards=boards,
            name=name,
            position=position,
            color=color,
            board_id=board_id,
        )

    status = Status(
        name=name,
        position=int(position),
        color=color or "#0d6efd",
        board_id=board.id,
    )
    session.add(status)
    session.commit()
    flash("Статус создан.", "success")
    return redirect(url_for("roles.list_statuses"))


@bp.get("/statuses/<int:status_id>/edit")
def edit_status(status_id: int) -> str:
    session = SessionLocal()
    status = session.get(Status, status_id)
    if not status:
        flash("Статус не найден.", "danger")
        return redirect(url_for("roles.list_statuses"))

    boards = session.execute(select(Board).order_by(Board.name)).scalars().all()
    return render_template("statuses/form.html", status=status, boards=boards)


@bp.post("/statuses/<int:status_id>")
def update_status(status_id: int) -> str:
    name = request.form.get("name", "").strip()
    position = request.form.get("position", "").strip()
    color = request.form.get("color", "").strip()
    board_id = request.form.get("board_id", "").strip()

    session = SessionLocal()
    status = session.get(Status, status_id)
    if not status:
        flash("Статус не найден.", "danger")
        return redirect(url_for("roles.list_statuses"))

    boards = session.execute(select(Board).order_by(Board.name)).scalars().all()

    if not name or not position or not board_id:
        flash("Имя, позиция и доска обязательны.", "danger")
        return render_template(
            "statuses/form.html",
            status=status,
            boards=boards,
            name=name,
            position=position,
            color=color,
            board_id=board_id,
        )

    board = session.get(Board, int(board_id))
    if not board:
        flash("Доска не найдена.", "danger")
        return render_template(
            "statuses/form.html",
            status=status,
            boards=boards,
            name=name,
            position=position,
            color=color,
            board_id=board_id,
        )

    status.name = name
    status.position = int(position)
    status.color = color or "#0d6efd"
    status.board_id = board.id
    session.commit()
    flash("Статус обновлен.", "success")
    return redirect(url_for("roles.list_statuses"))


@bp.post("/statuses/<int:status_id>/delete")
def delete_status(status_id: int) -> str:
    session = SessionLocal()
    status = session.get(Status, status_id)
    if not status:
        flash("Статус не найден.", "danger")
        return redirect(url_for("roles.list_statuses"))

    session.delete(status)
    session.commit()
    flash("Статус удален.", "success")
    return redirect(url_for("roles.list_statuses"))


@bp.get("/tasks")
def list_tasks() -> str:
    session = SessionLocal()
    tasks = (
        session.execute(
            select(Task)
            .options(selectinload(Task.board), selectinload(Task.status))
            .order_by(Task.id)
        )
        .scalars()
        .all()
    )
    return render_template("tasks/list.html", tasks=tasks)


@bp.get("/tasks/new")
def new_task() -> str:
    session = SessionLocal()
    boards = session.execute(select(Board).order_by(Board.name)).scalars().all()
    statuses = session.execute(
        select(Status).options(selectinload(Status.board)).order_by(Status.board_id, Status.position)
    ).scalars().all()
    return render_template("tasks/form.html", task=None, boards=boards, statuses=statuses)


@bp.post("/tasks")
def create_task() -> str:
    description = request.form.get("description", "").strip()
    board_id = request.form.get("board_id", "").strip()
    status_id = request.form.get("status_id", "").strip()

    session = SessionLocal()
    boards = session.execute(select(Board).order_by(Board.name)).scalars().all()
    statuses = session.execute(
        select(Status).options(selectinload(Status.board)).order_by(Status.board_id, Status.position)
    ).scalars().all()

    if not description or not board_id or not status_id:
        flash("Описание, доска и статус обязательны.", "danger")
        return render_template(
            "tasks/form.html",
            task=None,
            boards=boards,
            statuses=statuses,
            description=description,
            board_id=board_id,
            status_id=status_id,
        )

    board = session.get(Board, int(board_id))
    status = session.get(Status, int(status_id))
    if not board or not status or status.board_id != board.id:
        flash("Статус должен принадлежать выбранной доске.", "danger")
        return render_template(
            "tasks/form.html",
            task=None,
            boards=boards,
            statuses=statuses,
            description=description,
            board_id=board_id,
            status_id=status_id,
        )

    task = Task(description=description, board_id=board.id, status_id=status.id)
    session.add(task)
    session.commit()
    flash("Задача создана.", "success")
    return redirect(url_for("roles.list_tasks"))


@bp.get("/tasks/<int:task_id>/edit")
def edit_task(task_id: int) -> str:
    session = SessionLocal()
    task = session.get(Task, task_id)
    if not task:
        flash("Задача не найдена.", "danger")
        return redirect(url_for("roles.list_tasks"))

    boards = session.execute(select(Board).order_by(Board.name)).scalars().all()
    statuses = session.execute(
        select(Status).options(selectinload(Status.board)).order_by(Status.board_id, Status.position)
    ).scalars().all()
    return render_template("tasks/form.html", task=task, boards=boards, statuses=statuses)


@bp.post("/tasks/<int:task_id>")
def update_task(task_id: int) -> str:
    description = request.form.get("description", "").strip()
    board_id = request.form.get("board_id", "").strip()
    status_id = request.form.get("status_id", "").strip()

    session = SessionLocal()
    task = session.get(Task, task_id)
    if not task:
        flash("Задача не найдена.", "danger")
        return redirect(url_for("roles.list_tasks"))

    boards = session.execute(select(Board).order_by(Board.name)).scalars().all()
    statuses = session.execute(
        select(Status).options(selectinload(Status.board)).order_by(Status.board_id, Status.position)
    ).scalars().all()

    if not description or not board_id or not status_id:
        flash("Описание, доска и статус обязательны.", "danger")
        return render_template(
            "tasks/form.html",
            task=task,
            boards=boards,
            statuses=statuses,
            description=description,
            board_id=board_id,
            status_id=status_id,
        )

    board = session.get(Board, int(board_id))
    status = session.get(Status, int(status_id))
    if not board or not status or status.board_id != board.id:
        flash("Статус должен принадлежать выбранной доске.", "danger")
        return render_template(
            "tasks/form.html",
            task=task,
            boards=boards,
            statuses=statuses,
            description=description,
            board_id=board_id,
            status_id=status_id,
        )

    task.description = description
    task.board_id = board.id
    task.status_id = status.id
    session.commit()
    flash("Задача обновлена.", "success")
    return redirect(url_for("roles.list_tasks"))


@bp.post("/tasks/<int:task_id>/delete")
def delete_task(task_id: int) -> str:
    session = SessionLocal()
    task = session.get(Task, task_id)
    if not task:
        flash("Задача не найдена.", "danger")
        return redirect(url_for("roles.list_tasks"))

    session.delete(task)
    session.commit()
    flash("Задача удалена.", "success")
    return redirect(url_for("roles.list_tasks"))
