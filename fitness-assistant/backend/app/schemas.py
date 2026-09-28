"""Request / response models (they define the API contract used by the React app)."""
from typing import Literal

from pydantic import BaseModel, Field


class HistoryItem(BaseModel):
    role: Literal["user", "assistant"]
    text: str = Field(max_length=4000)


class ChatRequest(BaseModel):
    question: str = Field(min_length=1, max_length=2000)
    history: list[HistoryItem] = Field(default_factory=list)


class Source(BaseModel):
    title: str
    category: str


class ChatResponse(BaseModel):
    response: str
    sources: list[Source]


class Exercise(BaseModel):
    id: int
    title: str
    description: str
    category: str
    level: str
    muscles: list[str]
