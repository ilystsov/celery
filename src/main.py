# main.py
import os
import random

from celery.result import AsyncResult
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from .celery import user_task
from .db import fetch_tasks

app = FastAPI()

current_dir = os.path.dirname(os.path.abspath(__file__))
templates_dir = os.path.join(current_dir, "templates")
templates = Jinja2Templates(directory=templates_dir)

active_tasks: set[AsyncResult] = set()


@app.get("/", response_class=HTMLResponse)
async def get_form(request: Request):
    completed_tasks = fetch_tasks()

    completed_task_ids = {task[0] for task in completed_tasks}
    tasks_to_remove = {task for task in active_tasks if task.id in completed_task_ids}
    active_tasks.difference_update(tasks_to_remove)

    return templates.TemplateResponse(
        request=request, name="task_form.html",
        context={"tasks": active_tasks, "completed_tasks": completed_tasks}
    )


@app.post("/submit", response_class=HTMLResponse)
async def handle_form(request: Request):
    should_fail: bool = random.choice([True, False])
    new_task = user_task.delay(should_fail)
    active_tasks.add(new_task)
    return templates.TemplateResponse(
        request=request, name="task_created.html", context={"new_task": new_task}
    )


@app.get("/get-status/{task_id}")
async def get_task_status(task_id, request: Request):
    task_result = AsyncResult(task_id)
    return templates.TemplateResponse(
        request=request,
        name="task_status.html",
        context={"task_id": task_id, "task_status": task_result.status},
    )