from sqlalchemy.orm import Mapped, mapped_column

from .db import Base

class Todo(Base):
    __tablename__ = "todos"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(index=True)
    done: Mapped[bool] = mapped_column(default=False)
    