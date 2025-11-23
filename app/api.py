from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from app.database.requests import add_user, get_active_tasks, create_task, delete_task
from app.database.models import init_db
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(lifespan=lifespan)

# Обновите CORS для GitHub Pages
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        'https://duraluminum.github.io',
        'https://t.me', 
        'https://web.telegram.org',
        'http://localhost:3000'
    ],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

class TaskCreate(BaseModel):
    tg_id: int
    title: str
    deadline: str  # YYYY-MM-DD

@app.get('/')
async def root():
    return {'status': 'ok', 'service': 'Telegram Bot API'}

@app.post('/user/init')
async def init_user(tg_id: int):
    await add_user(tg_id)
    return {'ok': True}

@app.get('/tasks/{tg_id}')
async def get_tasks(tg_id: int):
    return await get_active_tasks(tg_id)

@app.post('/tasks/')
async def add_new_task(task: TaskCreate):
    return await create_task(task.tg_id, task.title, task.deadline)

@app.delete('/tasks/{task_id}')
async def remove_task(task_id: int):
    await delete_task(task_id)
    return {'ok': True}