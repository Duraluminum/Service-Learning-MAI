import os
from sqlalchemy import ForeignKey, String, BigInteger
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./test.db")

if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)
else:
    DATABASE_URL = "sqlite+aiosqlite:///./db.sqlite3"

engine = create_async_engine(DATABASE_URL, echo=True, future=True)
async_session = async_sessionmaker(bind=engine, expire_on_commit=False)

engine = create_async_engine(url='sqlite+aiosqlite:///db.sqlite3', echo=True)

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
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
