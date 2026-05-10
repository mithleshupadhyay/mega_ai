from __future__ import annotations

from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class RetrievedChunkCreate(BaseModel):
    chunk_id: str
    title: str
    content: str
    source_url: str
    tags: list[str] = Field(default_factory=list)


class RetrievedChunkOut(RetrievedChunkCreate):
    model_config = ConfigDict(from_attributes=True)


class StructuredRecordCreate(BaseModel):
    record_key: str
    category: str
    value: str
    metadata_json: dict[str, Any] = Field(default_factory=dict)


class StructuredRecordOut(StructuredRecordCreate):
    id: int

    model_config = ConfigDict(from_attributes=True)
