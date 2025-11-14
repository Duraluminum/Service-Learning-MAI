from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
from app.database.requests import add_user, get_active_tasks, create_task, delete_task

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['https://duraluminum.github.io', 'https://t.me', 'https://web.telegram.org'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

class TaskCreate(BaseModel):
    tg_id: int
    title: str
    deadline: str  # YYYY-MM-DD

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