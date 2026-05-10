from __future__ import annotations

import time

from mega_ai.core.config import get_settings
from mega_ai.db.pgv.crud.seeds import seed_static_data
from mega_ai.db.pgv.db import SessionLocal, init_db


def main() -> None:
    settings = get_settings()
    init_db()
    while True:
        db = SessionLocal()
        try:
            seed_static_data(db)
        finally:
            db.close()
        time.sleep(settings.job_worker_poll_seconds)


if __name__ == "__main__":
    main()
