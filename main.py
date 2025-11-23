import asyncio
import logging
import os
import sys
from aiogram import Dispatcher

from app.handlers import router
from app.database.models import init_db
from app.notifications import send_daily_reminders
from app.bot import bot

async def start_bot():
    """Запуск бота (для worker)"""
    try:
        await init_db()
        dp = Dispatcher()
        dp.include_router(router)
        
        # Запускаем уведомления только если это worker процесс
        asyncio.create_task(send_daily_reminders())
        
        print("🤖 Бот запущен и слушает сообщения...")
        await dp.start_polling(bot)
    except Exception as e:
        print(f"❌ Ошибка запуска бота: {e}")
        sys.exit(1)

async def start_web():
    """Запуск веб-сервера (для web)"""
    from app.api import app
    await init_db()
    print("🌐 Web API запущен")
    return app

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    # Определяем тип сервиса по переменной окружения Railway
    service_type = os.getenv('RAILWAY_SERVICE_TYPE')
    
    if service_type == 'web':
        # Запускаем только FastAPI
        import uvicorn
        port = int(os.getenv("PORT", 8000))
        uvicorn.run("app.api:app", host="0.0.0.0", port=port, log_level="info")
    else:
        # Запускаем только бота (worker)
        try:
            asyncio.run(start_bot())
        except KeyboardInterrupt:
            print('Бот был остановлен пользователем')
        except Exception as e:
            print(f'Критическая ошибка бота: {e}')
            sys.exit(1)