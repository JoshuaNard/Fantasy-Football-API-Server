# Fantasy Football API Server

Django + Django Shinobi API server for the `FantasyFootballDraftAssist` frontend in the sibling repository.

## Setup

```bash
uv sync
cp .env.example .env
uv run python manage.py migrate
uv run python manage.py runserver
```

Install [uv](https://docs.astral.sh/uv/getting-started/installation/) first if it is not already available. uv creates and manages the project virtual environment automatically.

The same commands are available through the Makefile:

```bash
make install
make migrate
make test
make start
```

API docs are available at:

```text
http://127.0.0.1:8000/api/docs
```

The default CORS configuration allows the Vite frontend at `http://localhost:5173` and `http://127.0.0.1:5173`.

## Endpoints

- `GET /api/health` - service health check
- `GET /api/integration/frontend` - reports whether the sibling frontend repo is reachable
