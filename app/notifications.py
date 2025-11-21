import asyncio
from collections import defaultdict
from datetime import datetime, timedelta, UTC
from aiogram.exceptions import TelegramBadRequest

from sqlalchemy import select

from app.database.models import Task, User, async_session
from app.bot import bot
import app.keyboards as kb


async def send_reminders():
    while True:
        now = datetime.now(UTC).date()
        target_dates = [now + timedelta(days=1), now + timedelta(days=3)]
        date_strings = [d.isoformat() for d in target_dates]

        async with async_session() as session:
            tasks = await session.scalars(
                select(Task)
                .where(Task.completed == False)
                .where(Task.deadline.in_(date_strings))
            )
            task_list = tasks.all()

            tasks_by_user = defaultdict(list)
            for task in task_list:
                tasks_by_user[task.user].append(task)

            for user_id, user_tasks in tasks_by_user.items():
                user = await session.get(User, user_id)
                if not user or not user.notifications:
                    continue

                task_lines = []
                for task in user_tasks:
                    deadline_date = datetime.fromisoformat(task.deadline).date()
                    days = (deadline_date - now).days
                    if days == 1:
                        day_word = "день"
                    elif 2 <= days <= 4:
                        day_word = "дня"
                    else:
                        day_word = "дней"
                    task_lines.append(
                        f'- Задание "{task.title}" нужно сдать через {days} {day_word}\n(на {deadline_date.strftime("%d.%m.%Y")})'
                    )

                msg = '❗ У тебя есть невыполненные задания:\n\n' + '\n'.join(task_lines)
                
                try:
                    await bot.send_message(chat_id=user.tg_id, text=msg, reply_markup=kb.homework)
                except TelegramBadRequest:
                    pass

        await asyncio.sleep(60)