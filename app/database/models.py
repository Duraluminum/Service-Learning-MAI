import os
import asyncio
from sqlalchemy import ForeignKey, String, BigInteger, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine

# Получаем DATABASE_URL из переменных окружения
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL не найден в переменных окружения!")

print(f"🔗 Исходный DATABASE_URL: {DATABASE_URL}")

# КРИТИЧЕСКИ ВАЖНО: Явно указываем использование asyncpg
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
elif DATABASE_URL.startswith("postgresql://"):
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://", 1)

print(f"🔗 Final DATABASE_URL: {DATABASE_URL}")

# Создаем engine с правильными настройками для PostgreSQL + asyncpg
engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    future=True,
    pool_pre_ping=True,
    pool_recycle=300,
)

async_session = async_sessionmaker(bind=engine, expire_on_commit=False)

class Base(AsyncAttrs, DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    notifications: Mapped[bool] = mapped_column(default=True)
    tg_id = mapped_column(BigInteger)

class Task(Base):
    __tablename__ = 'tasks'

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(128))
    deadline: Mapped[str] = mapped_column(String(16))
    completed: Mapped[bool] = mapped_column(default=False)
    user: Mapped[int] = mapped_column(ForeignKey('users.id', ondelete='CASCADE'))

async def init_db():
    """Инициализация базы данных с проверкой PostgreSQL"""
    max_retries = 3  # Уменьшим количество попыток
    for attempt in range(max_retries):
        try:
            async with engine.begin() as conn:
                result = await conn.execute(text("SELECT version();"))
                db_version = result.scalar()
                print(f"✅ Подключение к PostgreSQL: {db_version.split(',')[0]}")
                
                # Создаем таблицы
                await conn.run_sync(Base.metadata.create_all)
                print("✅ Таблицы успешно созданы в PostgreSQL")
            return
        except Exception as e:
            print(f"❌ Попытка {attempt + 1}/{max_retries} не удалась: {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(1)
            else:
                print("⚠️  Продолжаем запуск без базы данных...")
                # Не прерываем запуск при ошибке базы данных
                return

# Упрощенная инициализация для Railway
async def initialize_database():
    """Упрощенная инициализация базы данных"""
    try:
        await init_db()
    except Exception as e:
        print(f"⚠️  Предупреждение: Не удалось инициализировать базу данных: {e}")
        print("⚠️  Приложение продолжит работу, но функциональность базы данных будет ограничена")