from fastapi import FastAPI

from app.routers import todos, web

app = FastAPI(title="Todo")
app.include_router(todos.router)
app.include_router(web.router)
