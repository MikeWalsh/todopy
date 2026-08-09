from pathlib import Path
from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, Response
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.models import Todo

templates = Jinja2Templates(directory=Path(__file__).parent.parent / "templates")

router = APIRouter(tags=["web"])

@router.get("/", response_class=HTMLResponse)
async def index(request: Request, session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Todo).order_by(Todo.id))
    return templates.TemplateResponse(
        request, "index.html", {"todos": result.scalars().all()}
    )

@router.post("/web/todos", response_class=HTMLResponse)
async def create(request: Request, title: str = Form(...), session: AsyncSession =  Depends(get_session)):
    todo = Todo(title=title)
    session.add(todo)
    await session.commit()
    await session.refresh(todo)
    return templates.TemplateResponse(request, "partials/todo_item.html", {"todo": todo})

@router.patch("/web/todos/{todo_id}/toggle", response_class=HTMLResponse)
async def toggle(request: Request, todo_id: int, session: AsyncSession = Depends(get_session)):
    todo = await session.get(Todo, todo_id)
    if todo is None:
        raise HTTPException(status_code=404)
    todo.done = not todo.done
    await session.commit()
    return templates.TemplateResponse(request, "partials/todo_item.html", {"todo": todo})

@router.delete("/web/todos/{todo_id}")
async def delete(todo_id: int, session: AsyncSession = Depends(get_session)):
    todo = await session.get(Todo, todo_id)
    if todo is not None:
        await session.delete(todo)
        await session.commit()
    return Response(status_code=200)