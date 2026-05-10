import hashlib

SECRET_MARKERS = ("api_key", "authorization", "bearer ", "password", "secret", "token")


def stable_hash(value: str | bytes | None) -> str:
    if value is None:
        return ""
    raw = value if isinstance(value, bytes) else value.encode("utf-8")
    return hashlib.sha256(raw).hexdigest()[:16]


def safe_preview(value: str, max_chars: int = 160) -> str:
    lowered = value.lower()
    if any(marker in lowered for marker in SECRET_MARKERS):
        return "[redacted]"
    if len(value) <= max_chars:
        return value
    return f"{value[:max_chars]}..."
