from fastapi import FastAPI, HTTPException
from .\schema import TodoCreate, TodoRead, TodoUpdate

app = FastAPI(title="Todo")

TODOS: list[dict] = [
    {"id": 1, "title": "learn fastapi", "done": False},
]

@app.get("/todos", response_model=list[TodoRead])
def list_todos() -> list[dict]:
    return TODOS

@app.get("/todos/{todo_id}", response_model=TodoRead)
def get_todo(todo_id: int) -> dict:
    return _find(todo_id)

@app.post("/todos", response_model=TodoRead, status_code=201)
def create_todo(payload: TodoCreate):
    todo = {"id": max((t["id"] for t in TODOS), default=0) + 1,
            "title": payload.title,
            "done": False}
    TODOS.append(todo)
    return todo

@app.patch("/todos/{todo_id}", response_model=TodoRead)
def update_todo(todo_id: int, payload: TodoUpdate):
    todo = _find(todo_id)
    todo.update(payload.model_dump(exclude_unset=True))
    return todo

def _find(todo_id: int) -> dict:
    for t in TODOS:
        if (t["id"] == todo_id):
            return t
    raise HTTPException(status_code=404, detail="Not Found")