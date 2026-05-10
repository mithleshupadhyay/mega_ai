from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint

from mega_ai.db.pgv import db as pgv_db
from mega_ai.db.pgv.models.types import json_type

Base = pgv_db.Base


class ToolCall(Base):
    __tablename__ = "tool_calls"
    __table_args__ = (UniqueConstraint("job_id", "tool_call_id", name="uq_tool_call_id"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(ForeignKey("jobs.id"), index=True)
    tool_call_id = Column(String(80))
    tool_name = Column(String(80), index=True)
    agent_id = Column(String(80), index=True)
    retry_number = Column(Integer, default=0)
    status = Column(String(32), index=True)
    failure_mode = Column(String(80), nullable=True, index=True)
    input_hash = Column(String(64))
    input_preview = Column(Text)
    output_hash = Column(String(64))
    output_payload = Column(json_type(), default=dict)
    accepted = Column(Boolean, default=False)
    rejection_reason = Column(Text, nullable=True)
    latency_ms = Column(Integer)
    created_at = Column(DateTime(timezone=True), index=True)
