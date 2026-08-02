from pydantic import BaseModel, ConfigDict, Field

class TodoBase(BaseModel):
    title: str = Field(min_length=1, max_length=200)

class TodoCreate(TodoBase):
    """Id autocreated"""

class TodoUpdate(BaseModel):
    """All Optional. Missing field, no update"""
    title: str | None = Field(default=None, min_length=1, max_length=200)
    done: bool | None = None

class TodoRead(TodoBase):
    model_config = ConfigDict(from_attributes=True)

    id: int
    done: bool
    