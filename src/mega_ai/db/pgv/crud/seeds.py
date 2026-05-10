from __future__ import annotations

from sqlalchemy.orm import Session

from mega_ai.agents.prompts import DEFAULT_PROMPTS, prompt_id
from mega_ai.core.logging.structured import utc_now
from mega_ai.db.pgv.crud.knowledge import (
    create_retrieved_chunk,
    create_structured_record,
    get_retrieved_chunk,
    get_structured_record,
)
from mega_ai.db.pgv.crud.prompts import create_prompt_version
from mega_ai.db.pgv.models import PromptVersion
from mega_ai.db.pgv.schemas.knowledge import RetrievedChunkCreate, StructuredRecordCreate
from mega_ai.db.pgv.schemas.prompts import PromptVersionCreate
from mega_ai.rag.corpus import LOCAL_CHUNKS, STRUCTURED_RECORDS


def _string_list(value: object) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value]
    return []


def _string_object_dict(value: object) -> dict[str, object]:
    if isinstance(value, dict):
        return {str(key): item for key, item in value.items()}
    return {}


def seed_static_data(db: Session) -> None:
    for item in LOCAL_CHUNKS:
        existing_chunk = get_retrieved_chunk(db, str(item["chunk_id"]))
        if existing_chunk is None:
            create_retrieved_chunk(
                db,
                RetrievedChunkCreate(
                    chunk_id=str(item["chunk_id"]),
                    title=str(item["title"]),
                    content=str(item["content"]),
                    source_url=str(item["source_url"]),
                    tags=_string_list(item["tags"]),
                )
            )
        else:
            existing_chunk.title = str(item["title"])
            existing_chunk.content = str(item["content"])
            existing_chunk.source_url = str(item["source_url"])
            existing_chunk.tags = _string_list(item["tags"])

    for item in STRUCTURED_RECORDS:
        existing_record = get_structured_record(db, str(item["record_key"]))
        if existing_record is None:
            create_structured_record(
                db,
                StructuredRecordCreate(
                    record_key=str(item["record_key"]),
                    category=str(item["category"]),
                    value=str(item["value"]),
                    metadata_json=_string_object_dict(item["metadata_json"]),
                )
            )
        else:
            existing_record.category = str(item["category"])
            existing_record.value = str(item["value"])
            existing_record.metadata_json = _string_object_dict(item["metadata_json"])

    for agent_id, prompt_text in DEFAULT_PROMPTS.items():
        version_id = prompt_id(agent_id)
        existing_prompt = db.get(PromptVersion, version_id)
        if existing_prompt is None:
            create_prompt_version(
                db,
                PromptVersionCreate(
                    id=version_id,
                    agent_id=agent_id,
                    version=1,
                    prompt_text=prompt_text,
                    is_active=True,
                    created_at=utc_now(),
                    approved_at=utc_now(),
                )
            )
    db.commit()
