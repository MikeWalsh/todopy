from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db import get_session
from app.models import Todo
from app.schema import TodoCreate, TodoRead, TodoUpdate

SessionDep = Annotated[AsyncSession, Depends(get_session)]

router = APIRouter(prefix="/todos", tags=["todos"])


@router.get("", response_model=list[TodoRead])
async def list_todos(session: SessionDep):
    result = await session.execute(select(Todo).order_by(Todo.id))
    return result.scalars().all()


@router.get("/{todo_id}", response_model=TodoRead)
async def get_todo(todo_id: int, session: SessionDep):
    todo = await session.get(Todo, todo_id)
    return todo


@router.post("", response_model=TodoRead, status_code=201)
async def create_todo(payload: TodoCreate, session: SessionDep):
    todo = Todo(title=payload.title)
    session.add(todo)
    await session.commit()
    await session.refresh(todo)
    return todo


@router.patch("/{todo_id}", response_model=TodoRead)
async def update_todo(todo_id: int, payload: TodoUpdate, session: SessionDep):
    todo = await session.get(Todo, todo_id)
    if todo is None:
        raise HTTPException(status_code=404, detail="not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(todo, field, value)
    await session.commit()
    return todo
