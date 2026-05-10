import time
from collections.abc import Iterator

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session, declarative_base, sessionmaker

from mega_ai.core.config import get_settings


class _Base:
    __allow_unmapped__ = True


Base = declarative_base(cls=_Base)


def _connect_args(database_url: str) -> dict[str, object]:
    if database_url.startswith("sqlite"):
        return {"check_same_thread": False}
    return {}


settings = get_settings()
engine = create_engine(
    settings.database_url,
    connect_args=_connect_args(settings.database_url),
    pool_pre_ping=True,
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, expire_on_commit=False)


def init_db(retries: int = 20, delay_seconds: float = 0.5) -> None:
    import mega_ai.db.pgv.models  # noqa: F401

    last_error: OperationalError | None = None
    for _attempt in range(retries):
        try:
            Base.metadata.create_all(bind=engine)
            _ensure_schema_compatibility()
            return
        except OperationalError as exc:
            last_error = exc
            time.sleep(delay_seconds)
    if last_error is not None:
        raise last_error


def _ensure_schema_compatibility() -> None:
    inspector = inspect(engine)
    if "tool_calls" not in inspector.get_table_names():
        return
    columns = {column["name"] for column in inspector.get_columns("tool_calls")}
    if "failure_mode" in columns:
        return

    with engine.begin() as connection:
        connection.execute(text("ALTER TABLE tool_calls ADD COLUMN failure_mode VARCHAR(80)"))
        if not settings.database_url.startswith("sqlite"):
            connection.execute(
                text("CREATE INDEX IF NOT EXISTS ix_tool_calls_failure_mode ON tool_calls (failure_mode)")
            )


def get_db() -> Iterator[Session]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
