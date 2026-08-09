from fastapi import FastAPI

from app.routers import todos
from app.routers import web

app = FastAPI(title="Todo")
app.include_router(todos.router)
app.include_router(web.router)


