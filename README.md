# Finance App

A personal finance application for budgeting, expense tracking, and lightweight
accounting, with a FastAPI backend and a vanilla JS + Rollup frontend.

## Project Structure

- `backend/` – FastAPI + Peewee API service
- `frontend/` – Vanilla JS frontend bundled with Rollup
- `docs/` – Project documentation (plan, notes)

## Backend (FastAPI)

### Local setup

```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r requirements.txt
```

Create a `.env` file in `backend/` (see `.env.example` for keys) and set at least:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/finance_app
SECRET_KEY=change_me
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
```

Run the API in development:

```bash
uvicorn src.main:app --reload
```

### Render deployment (summary)

- Build command: `pip install -r requirements.txt`
- Start command: `uvicorn src.main:app --host 0.0.0.0 --port $PORT`
- Environment variables (in Render dashboard):
  - `DATABASE_URL` (from Render Postgres)
  - `SECRET_KEY`
  - `ALGORITHM` (e.g. `HS256`)
  - `ACCESS_TOKEN_EXPIRE_MINUTES`

## Frontend (Vanilla JS + Rollup)

### Local setup

```bash
cd frontend
npm install
```

Build (production bundle in `dist/`):

```bash
npm run build
```

Development (watch mode, you can serve `dist/` with any static HTTP server):

```bash
npm run dev
```

### Render static site

- Build command: `npm install && npm run build`
- Publish directory: `dist`
- Configure `window.API_URL` (e.g. via HTML injection or environment) to point at the
  backend Render service URL.

## Documentation

See `docs/PROJECT_PLAN.md` for a pointer to the detailed project plan.


