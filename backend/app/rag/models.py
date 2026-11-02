
from pydantic import BaseModel, Field, ConfigDict
from enum import Enum
from typing import Literal


class AnswerStatus(str, Enum):
    ANSWERED = "answered"
    PARTIAL = "partial"
    INSUFFICIENT_EVIDENCE = "insufficient_evidence"


class HistoryMessage(BaseModel):
    model_config = ConfigDict(extra="forbid")

    role: Literal["user", "assistant"]
    content: str = Field(
        min_length=1,
        max_length=1500,
    )


class ChatRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    message: str = Field(
        min_length=1,
        max_length=1000,
    )

    history: list[HistoryMessage] = Field(
        default_factory=list,
        max_length=6,
    )



class SourceReference(BaseModel):
    id: int
    chunk_id: str
    document_id: str
    title: str
    url: str
    content: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[SourceReference] = Field(
        default_factory=list
    )
    status: AnswerStatus
    grounded: bool = False
