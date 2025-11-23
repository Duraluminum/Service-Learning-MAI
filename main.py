import asyncio
import logging
import os
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


async def start_web():
    from app.api import app
    await init_db()
    return app


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    if os.getenv('RAILWAY_SERVICE_TYPE') == 'web':
        import uvicorn
        uvicorn.run('main:start_web', host='0.0.0.0', port=int(os.getenv('PORT', 8000)))
    else:
        try:
            asyncio.run(start_bot())
        except KeyboardInterrupt:
            print('Бот был остановлен пользователем')