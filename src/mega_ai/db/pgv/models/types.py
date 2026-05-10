from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.types import JSON


def json_type():
    return JSONB().with_variant(JSON(), "sqlite")
