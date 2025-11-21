import asyncio
import logging
from aiogram import Dispatcher

from app.handlers import router
from app.database.models import init_db
from app.notifications import send_reminders
from app.bot import bot


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
        print('Бот был остановлен пользователем')