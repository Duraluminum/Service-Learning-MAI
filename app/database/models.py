import os
import asyncio
from sqlalchemy import ForeignKey, String, BigInteger, text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine

DATABASE_URL = os.getenv('DATABASE_URL')


if DATABASE_URL.startswith('postgres://'):
    DATABASE_URL = DATABASE_URL.replace('postgres://', 'postgresql+asyncpg://', 1)
elif DATABASE_URL.startswith('postgresql://'):
    DATABASE_URL = DATABASE_URL.replace('postgresql://', 'postgresql+asyncpg://', 1)

print(f'DATABASE_URL: {DATABASE_URL}')


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
    max_retries = 3
    for attempt in range(max_retries):
        try:
            async with engine.begin() as conn:
                result = await conn.execute(text('SELECT version();'))
                db_version = result.scalar()
                print(f'✅ Подключение к PostgreSQL: {db_version.split(',')[0]}')
                
                await conn.run_sync(Base.metadata.create_all)
                print('✅ Таблицы успешно созданы')
            return
        except Exception as e:
            print(f'Попытка {attempt + 1}/{max_retries} не удалась: {e}')
            if attempt < max_retries - 1:
                await asyncio.sleep(1)
            else:
                return

async def initialize_database():
    try:
        await init_db()
    except Exception as e:
        print(f'Не удалось инициализировать базу данных: {e}')