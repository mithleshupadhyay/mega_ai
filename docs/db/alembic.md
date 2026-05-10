# Alembic Notes

The app still creates tables on startup so `docker compose up` works with zero manual steps.
Alembic is included to mirror the production service structure and provide a migration path.

Local SQLite migration smoke test:

```bash
DATABASE_URL=sqlite:///./mega_ai.db poetry run alembic upgrade head
```

Docker/PostgreSQL migration path:

```bash
docker compose run --rm api alembic upgrade head
```
