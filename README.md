# Fantasy Football API Server

Django + Django Shinobi API server for the `FantasyFootballDraftAssist` frontend in the sibling repository.

## Setup

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python manage.py migrate
python manage.py runserver
```

API docs are available at:

```text
http://127.0.0.1:8000/api/docs
```

The default CORS configuration allows the Vite frontend at `http://localhost:5173` and `http://127.0.0.1:5173`.

## Endpoints

- `GET /api/health` - service health check
- `GET /api/integration/frontend` - reports whether the sibling frontend repo is reachable
