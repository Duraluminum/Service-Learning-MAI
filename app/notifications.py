import asyncio
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from aiogram.exceptions import TelegramBadRequest
from sqlalchemy import select

from app.database.models import Task, User, async_session
from app.bot import bot
import app.keyboards as kb


async def send_daily_reminders():
    while True:
        now = datetime.now(timezone.utc)
        
        moscow_tz = timezone(timedelta(hours=3))
        now_moscow = now.astimezone(moscow_tz)
        
        target_time = now_moscow.replace(hour=19, minute=0, second=0, microsecond=0)
        
        if now_moscow >= target_time:
            target_time += timedelta(days=1)
        
        target_utc = target_time.astimezone(timezone.utc)
        sleep_seconds = (target_utc - now).total_seconds()
        
        print(f'Следующая отправка напоминаний: {target_time.strftime('%Y-%m-%d %H:%M')} (МСК)')
        await asyncio.sleep(sleep_seconds)
        

        today_moscow = target_time.date()
        now_for_deadline = today_moscow 
        
        target_dates = [
            now_for_deadline + timedelta(days=1),
            now_for_deadline + timedelta(days=3)
        ]
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
                    days = (deadline_date - now_for_deadline).days
                    if days == 1:
                        day_word = 'день'
                    elif 2 <= days <= 4:
                        day_word = 'дня'
                    else:
                        day_word = 'дней'
                    task_lines.append(
                        f'– Задание "{task.title}" нужно сдать через {days} {day_word}\n(на {deadline_date.strftime('%d.%m.%Y')})'
                    )

                msg = '❗ У тебя есть невыполненные задания:\n\n' + '\n'.join(task_lines)
                
                try:
                    await bot.send_message(chat_id=user.tg_id, text=msg, reply_markup=kb.homework)
                except TelegramBadRequest:
                    pass