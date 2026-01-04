## Creating a Render PostgreSQL instance for this project

This guide walks through creating a Render PostgreSQL database suitable for the
`finance_app` backend in both development and production.

### 1. Sign in to Render

1. Go to `https://render.com` and sign in (or create an account).
2. Make sure you are in the correct team/personal account where the app will live.

### 2. Create a new PostgreSQL instance

1. From the Render dashboard, click **New +** → **PostgreSQL**.
2. Fill in the form:
   - **Name**: something like `finance-app-db`.
   - **Region**: choose the same region you plan to use for the backend service.
   - **Database**: keep the default name or set e.g. `finance_app`.
   - **User / Password**: Render will auto-generate; you can keep those.
   - **Plan**: choose the free or lowest-tier plan that fits your needs.
3. Click **Create Database** and wait for it to provision.

### 3. Get the `DATABASE_URL`

1. After the instance is created, open it from the Render dashboard.
2. In the **Connections** or **Info** tab, locate the **Internal Database URL**
   (or `DATABASE_URL` value).
3. Copy this URL. It will look like:

   ```text
   postgres://USER:PASSWORD@HOST:PORT/DB_NAME
   ```

4. Keep this URL handy; you will use it for:
   - Local development (`backend/.env`)
   - Backend Render service environment variables

### 4. Configure local development to use Render Postgres

1. In `backend/.env`, set:

   ```env
   DATABASE_URL=postgres://USER:PASSWORD@HOST:PORT/DB_NAME
   SECRET_KEY=change_me
   ALGORITHM=HS256
   ACCESS_TOKEN_EXPIRE_MINUTES=60
   ```

2. Ensure dependencies are installed:

   ```bash
   cd backend
   pip install -r requirements.txt
   ```

3. Run the initial migration to create tables in this database:

   ```bash
   cd backend
   python -m src.migrations.0001_initial
   ```

   This uses the `DATABASE_URL` from `.env` and creates the core tables
   (`users`, `accounts`, `categories`, `transactions`, `recurring_transactions`,
   `budgets`, `chart_of_accounts`, `transaction_imports`).

4. Start the API:

   ```bash
   uvicorn src.main:app --reload
   ```

### 5. Attach the database to the backend Render service (Docker)

When you create the backend web service on Render (for the FastAPI app), use a
**Docker** web service:

1. In Render, click **New +** → **Web Service** and connect your Git repo.
2. Choose **Docker** as the environment type.
3. In the service settings:
   - Set the repo root to the project root (Render will detect `backend/Dockerfile`).
   - Confirm that `backend/Dockerfile` is the Dockerfile to use.
4. Under **Environment Variables**:
   - Add `DATABASE_URL` and paste the value from the Postgres instance.
   - Add `SECRET_KEY`, `ALGORITHM`, `ACCESS_TOKEN_EXPIRE_MINUTES` as appropriate.
5. Deploy the service. Render will:
   - Build the image using `backend/Dockerfile`.
   - Start the container using the `CMD` defined there
     (`uvicorn src.main:app --host 0.0.0.0 --port 8000`).
   - Connect to the same Render Postgres instance that you used locally.

### 6. Future migrations

For schema changes:

1. Create a new migration file in `backend/src/migrations/`, e.g.
   `0002_add_something.py`, that uses Peewee/`db` to modify tables.
2. Run it manually against Render Postgres:

   ```bash
   cd backend
   python -m src.migrations.0002_add_something
   ```

3. Keep migrations ordered and idempotent where possible.


