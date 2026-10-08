from typing import Literal

from pydantic import BaseModel, Field, field_validator

MAX_MESSAGE_LENGTH = 2000
MAX_HISTORY_ITEMS = 20


class HistoryItem(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=MAX_MESSAGE_LENGTH)


class ChatRequest(BaseModel):
    message: str = Field(max_length=MAX_MESSAGE_LENGTH)
    history: list[HistoryItem] = Field(default_factory=list, max_length=MAX_HISTORY_ITEMS)

    @field_validator("message")
    @classmethod
    def message_not_blank(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("message no puede estar vacío")
        return value


class ChatResponse(BaseModel):
    reply: str


class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"
