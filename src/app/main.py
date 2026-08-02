from fastapi import FastAPI

from app.routers import todos

app = FastAPI(title="Todo")
app.include_router(todos.router)


