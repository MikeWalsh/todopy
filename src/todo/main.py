from fastapi import FastAPI, HTTPException

app = FastAPI(title="Todo")

TODOS: list[dict] = [
    {"id": 1, "title": "learn fastapi", "done": False},
]

@app.get("/todos")
def list_todos() -> list[dict]:
    return TODOS

@app.get("/todos/{todo_id}")
def get_todo(todo_id: int) -> dict:
    for t in TODOS:
        if t["id"] == todo_id:
            return t
    raise HTTPException(status_code=404, detail="Not Found")

@app.post("/todos", status_code=201)
def create_todo(title: str) -> dict:
    todo = {"id": max((t["id"] for t in TODOS), default=0) + 1,
            "title": title,
            "done": False}
    TODOS.append(todo)
    return todo

