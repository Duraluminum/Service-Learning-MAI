import asyncio
import logging
import os

from collections import defaultdict
from dotenv import load_dotenv
from sqlalchemy import select
from datetime import datetime, timedelta, UTC
from aiogram import Bot, Dispatcher
from aiogram.exceptions import TelegramBadRequest

from app.handlers import router
from app.database.requests import async_session
from app.database.models import Task, User, init_db, async_session
import app.keyboards as kb

load_dotenv()

TOKEN = os.getenv('BOT_TOKEN')
bot = Bot(token=TOKEN)


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
                    task_lines.append(f'• «{task.title}» нужно сдать через {days} {'день' if days == 1 else 'дня'} (на {deadline_date.strftime('%d.%m.%Y')})')

                msg = '❗ У тебя есть невыполненные задания:\n\n' + '\n'.join(task_lines)
                
                try:
                    await bot.send_message(chat_id=user.tg_id, text=msg, reply_markup=kb.homework)
                except TelegramBadRequest:
                    pass

        await asyncio.sleep(60)




async def main():
    await init_db()

    dp = Dispatcher()
    dp.include_router(router)
    asyncio.create_task(send_reminders())
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Exit')
