import asyncio
import logging
import os

from dotenv import load_dotenv
from sqlalchemy import select
from datetime import datetime, timedelta, UTC
from aiogram import Bot, Dispatcher
from aiogram.exceptions import TelegramBadRequest

from app.handlers import router
from app.database.requests import async_session
from app.database.models import Task, User, init_db, async_session

load_dotenv()

TOKEN = os.getenv('BOT_TOKEN')
bot = Bot(token=TOKEN)


async def send_reminders():
    while True:
        now = datetime.now(UTC).date()
        target_dates = [now + timedelta(days=1), now + timedelta(days=3)]

        async with async_session() as session:
            tasks = await session.scalars(
                select(Task)
                .where(Task.completed == False)
                .where(Task.deadline.in_([d.isoformat() for d in target_dates]))
            )
            task_list = tasks.all()

            for task in task_list:
                user = await session.get(User, task.user)
                if not user or not user.notifications:
                    continue

                days = (datetime.fromisoformat(task.deadline).date() - now).days
                msg = f'Напоминание: задание «{task.title}» нужно сдать через {days} день(дня)!'
                try:
                    await bot.send_message(chat_id=user.tg_id, text=msg)
                except TelegramBadRequest:
                    pass

        await asyncio.sleep(3600)




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
