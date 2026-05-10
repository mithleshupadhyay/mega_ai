from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String

from mega_ai.db.pgv import db as pgv_db
from mega_ai.db.pgv.models.types import json_type

Base = pgv_db.Base


class EvalRun(Base):
    __tablename__ = "eval_runs"

    id = Column(String(80), primary_key=True)
    status = Column(String(32), index=True)
    run_type = Column(String(32), index=True)
    started_at = Column(DateTime(timezone=True), index=True)
    finished_at = Column(DateTime(timezone=True), nullable=True)
    summary = Column(json_type(), default=dict)
    prompt_version_ids = Column(json_type(), default=dict)


class EvalCaseResult(Base):
    __tablename__ = "eval_case_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    eval_run_id = Column(ForeignKey("eval_runs.id"), index=True)
    test_case_id = Column(String(80), index=True)
    category = Column(String(80), index=True)
    job_id = Column(String(80), index=True)
    prompt_snapshots = Column(json_type(), default=dict)
    tool_calls = Column(json_type(), default=list)
    outputs = Column(json_type(), default=dict)
    scores = Column(json_type(), default=dict)
    total_score = Column(Float, index=True)
    passed = Column(Boolean, default=False, index=True)
    diffable_snapshot = Column(json_type(), default=dict)
    created_at = Column(DateTime(timezone=True), index=True)
