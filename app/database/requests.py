from sqlalchemy import select, update, delete, func
from .models import async_session, User, Task
from typing import Optional

async def add_user(tg_id: int) -> User:
    print(f"[DEBUG] add_user вызван для tg_id={tg_id}")
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if user:
            print(f"[DEBUG] Пользователь найден: id={user.id}")
            return user
        new_user = User(tg_id=tg_id)
        session.add(new_user)
        await session.commit()
        await session.refresh(new_user)
        print(f"[DEBUG] Создан новый пользователь: id={new_user.id}")
        return new_user


async def get_user_by_tg_id(tg_id: int) -> Optional[User]:
    async with async_session() as session:
        return await session.scalar(select(User).where(User.tg_id == tg_id))


async def toggle_notifications(tg_id: int) -> bool:
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if not user:
            return False
        user.notifications = not user.notifications
        await session.commit()
        return user.notifications


async def get_user_notifications_enabled(tg_id: int) -> bool:
    user = await get_user_by_tg_id(tg_id)
    return user.notifications if user else False


async def get_active_tasks(tg_id: int):
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.tg_id == tg_id))
        if not user:
            return []
        tasks = await session.scalars(
            select(Task)
            .where(Task.user == user.id)
            .where(Task.completed == False)
        )
        return [{'id': t.id, 'title': t.title, 'deadline': t.deadline} for t in tasks]


async def create_task(tg_id: int, title: str, deadline: str):
    user = await add_user(tg_id)
    async with async_session() as session:
        task = Task(title=title, deadline=deadline, user=user.id)
        session.add(task)
        await session.commit()
        await session.refresh(task)
        return {'id': task.id, 'title': task.title, 'deadline': task.deadline}


async def delete_task(task_id: int):
    async with async_session() as session:
        task = await session.get(Task, task_id)
        if task:
            await session.delete(task)
            await session.commit()