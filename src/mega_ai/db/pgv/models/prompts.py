from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text

from mega_ai.db.pgv import db as pgv_db
from mega_ai.db.pgv.models.types import json_type

Base = pgv_db.Base


class PromptVersion(Base):
    __tablename__ = "prompt_versions"

    id = Column(String(80), primary_key=True)
    agent_id = Column(String(80), index=True)
    version = Column(Integer)
    prompt_text = Column(Text)
    is_active = Column(Boolean, default=True, index=True)
    created_at = Column(DateTime(timezone=True), index=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)


class PromptRewriteProposal(Base):
    __tablename__ = "prompt_rewrite_proposals"

    id = Column(String(80), primary_key=True)
    eval_run_id = Column(ForeignKey("eval_runs.id"), index=True)
    agent_id = Column(String(80), index=True)
    target_dimension = Column(String(120), index=True)
    old_prompt = Column(Text)
    new_prompt = Column(Text)
    structured_diff = Column(json_type(), default=dict)
    justification = Column(Text)
    status = Column(String(32), default="pending", index=True)
    reviewer_note = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), index=True)
    decided_at = Column(DateTime(timezone=True), nullable=True)
    approved_prompt_version_id = Column(String(80), nullable=True)


class PerformanceDelta(Base):
    __tablename__ = "performance_deltas"

    id = Column(Integer, primary_key=True, autoincrement=True)
    rewrite_id = Column(ForeignKey("prompt_rewrite_proposals.id"), index=True)
    before_eval_run_id = Column(String(80), index=True)
    after_eval_run_id = Column(String(80), index=True)
    delta_payload = Column(json_type(), default=dict)
    created_at = Column(DateTime(timezone=True), index=True)
