import os
import asyncio
from sqlalchemy import ForeignKey, String, BigInteger
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine

# Получаем DATABASE_URL из переменных окружения
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL не найден в переменных окружения!")

print(f"🔗 Подключаемся к базе: {DATABASE_URL.split('@')[1] if '@' in DATABASE_URL else DATABASE_URL}")

# Обязательно преобразуем postgres:// в postgresql+asyncpg://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)

# Создаем engine с правильными настройками для PostgreSQL
engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    future=True,
    pool_pre_ping=True,  # Проверяем соединение перед использованием
    pool_recycle=300,    # Переподключаемся каждые 5 минут
)

async_session = async_sessionmaker(bind=engine, expire_on_commit=False)

class Base(AsyncAttrs, DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    notifications: Mapped[bool] = mapped_column(default=False)
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
    max_retries = 5
    for attempt in range(max_retries):
        try:
            async with engine.begin() as conn:
                # Проверяем, что мы используем PostgreSQL
                result = await conn.execute("SELECT version();")
                db_version = result.scalar()
                print(f"✅ Подключение к PostgreSQL: {db_version.split(',')[0]}")
                
                # Создаем таблицы
                await conn.run_sync(Base.metadata.create_all)
                print("✅ Таблицы успешно созданы в PostgreSQL")
            return
        except Exception as e:
            print(f"❌ Попытка {attempt + 1}/{max_retries} не удалась: {e}")
            if attempt < max_retries - 1:
                await asyncio.sleep(2)
            else:
                raise e