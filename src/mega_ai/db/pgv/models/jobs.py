from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import relationship

from mega_ai.db.pgv import db as pgv_db
from mega_ai.db.pgv.models.types import json_type

Base = pgv_db.Base


class Job(Base):
    __tablename__ = "jobs"

    id = Column(String(64), primary_key=True)
    status = Column(String(32), index=True)
    query = Column(Text)
    final_answer = Column(Text, nullable=True)
    provenance_map = Column(json_type(), default=dict)
    error_code = Column(String(80), nullable=True)
    created_at = Column(DateTime(timezone=True), index=True)
    updated_at = Column(DateTime(timezone=True), index=True)

    traces = relationship(
        "TraceEvent",
        back_populates="job",
        cascade="all, delete-orphan",
        order_by="TraceEvent.event_order",
    )


class TraceEvent(Base):
    __tablename__ = "trace_events"
    __table_args__ = (UniqueConstraint("job_id", "event_order", name="uq_trace_job_order"),)

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(ForeignKey("jobs.id"), index=True)
    event_order = Column(Integer)
    timestamp = Column(DateTime(timezone=True), index=True)
    agent_id = Column(String(80), nullable=True, index=True)
    event_type = Column(String(80), index=True)
    input_hash = Column(String(64), default="")
    output_hash = Column(String(64), default="")
    latency_ms = Column(Integer, nullable=True)
    token_count = Column(Integer, nullable=True)
    policy_violations = Column(json_type(), default=list)
    payload = Column(json_type(), default=dict)

    job = relationship("Job", back_populates="traces")


class AgentExecution(Base):
    __tablename__ = "agent_executions"

    id = Column(Integer, primary_key=True, autoincrement=True)
    job_id = Column(ForeignKey("jobs.id"), index=True)
    agent_id = Column(String(80), index=True)
    prompt_version_id = Column(String(80), index=True)
    prompt_text = Column(Text)
    input_payload = Column(json_type(), default=dict)
    output_payload = Column(json_type(), default=dict)
    started_at = Column(DateTime(timezone=True))
    finished_at = Column(DateTime(timezone=True))
    latency_ms = Column(Integer)
    token_count = Column(Integer)
