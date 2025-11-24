import asyncio
import logging
import sys
from aiogram import Dispatcher

from app.handlers import router
from app.database.models import init_db
from app.notifications import send_daily_reminders
from app.bot import bot

async def start_bot():
    await init_db()

    dp = Dispatcher()
    dp.include_router(router)
    
    asyncio.create_task(send_daily_reminders())
    await dp.start_polling(bot)


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    try:
        asyncio.run(start_bot())
    except KeyboardInterrupt:
        print('Бот был остановлен')
    except Exception as e:
        print(f'Критическая ошибка: {e}')
        sys.exit(1)