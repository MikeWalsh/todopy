from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession


from .db import get_session
from .models import Todo
from .schema import TodoCreate, TodoRead, TodoUpdate

app = FastAPI(title="Todo")


@app.get("/todos", response_model=list[TodoRead])
async def list_todos(session: AsyncSession = Depends(get_session)):
    result = await session.execute(select(Todo).order_by(Todo.id))
    return result.scalars().all()

@app.get("/todos/{todo_id}", response_model=TodoRead)
async def get_todo(todo_id: int,session: AsyncSession = Depends(get_session)):
    todo = await session.get(Todo, todo_id)
    return todo

@app.post("/todos", response_model=TodoRead, status_code=201)
async def create_todo(payload: TodoCreate, session: AsyncSession = Depends(get_session)):
    todo = Todo(title=payload.title)
    session.add(todo)
    await session.commit();
    await session.refresh(todo)
    return todo

@app.patch("/todos/{todo_id}", response_model=TodoRead)
async def update_todo(todo_id: int, payload: TodoUpdate, session: AsyncSession = Depends(get_session)):
    todo = await session.get(Todo, todo_id)
    if todo is None:
        raise HTTPException(status_code=404, detail="not found")
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(todo, field, value)
    await session.commit()
    return todo
