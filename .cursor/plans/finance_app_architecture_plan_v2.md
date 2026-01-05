---
name: Finance App Architecture Plan (v2)
overview: Updated plan including custom reports and transaction splits mapped to chart of accounts.
todos: []
---

## Database schema (delta from original plan)

- **BankAccount** (already implemented)
  - `id` (UUID, PK)
  - `account_id` (FK → Accounts, 1:1)
  - `bank_name`, `bank_account_type`, `account_number`, `routing_number`

- **TransactionLines** (new – transaction splits)
  - `id` (UUID, PK)
  - `transaction_id` (FK → Transactions)
  - `chart_of_account_id` (FK → ChartOfAccounts)
  - `amount` (decimal)
  - `memo` (string, nullable)
  - Relationship: Transactions → TransactionLines (1:N)

- **CustomReports** (new)
  - `id` (UUID, PK)
  - `user_id` (FK → Users)
  - `name` (string)
  - `description` (string, nullable)
  - `sql_query` (text, read-only SELECT queries only)

These tables are included in:
- `backend/src/utils/database.py:init_db()`
- `backend/src/migrations/0001_initial.py`

## API surface (additions/changes)

### Transactions (splits)

- **Schemas** (`schemas/transaction.py`, `schemas/transaction_split.py`)
  - `TransactionCreate` / `TransactionUpdate` now accept:
    - `splits: TransactionSplitCreate[] | null` where each split has:
      - `chart_of_account_id`, `amount`, `memo?`
  - `TransactionRead` includes:
    - `splits: TransactionSplitRead[] | null`

- **Behavior** (`api/transactions.py`)
  - On create/update:
    - Optionally validate and write `TransactionLine` rows via `_replace_transaction_splits`.
    - Each split is validated to belong to the current user’s `ChartOfAccount`.
  - On read/list:
    - Transactions are serialized via `_tx_to_read`, attaching current `splits` from `TransactionLine`.

This preserves `Transaction` as the bank-level record while allowing flexible allocation to multiple chart-of-accounts lines for reporting/accounting.

### Custom reports

- **Model / Schemas**
  - `models.CustomReport`: per-user saved report with `name`, `description`, `sql_query`.
  - `schemas.CustomReport*`: `CustomReportCreate/Update/Read`.

- **CRUD API** (`api/custom_reports.py`, mounted at `/api/custom-reports`)
  - `GET /api/custom-reports` – list user’s saved reports.
  - `POST /api/custom-reports` – create.
  - `GET /api/custom-reports/{id}` – get one (scoped to user).
  - `PUT /api/custom-reports/{id}` – update name/description/sql.
  - `DELETE /api/custom-reports/{id}` – delete.

- **Execution API** (`api/reports.py`)
  - `POST /api/reports/custom-sql`
    - Body: `{ "query": "SELECT ... " }`
    - Uses `report_service.run_custom_sql`:
      - Enforces query starts with `SELECT`.
      - Rejects queries containing write keywords: `insert`, `update`, `delete`, `drop`, `alter`, `truncate`.
      - Executes against the shared Peewee `db` and returns `{ columns: string[], rows: object[] }`.

### Reporting additions (Phase 5 extensions)

New report service functions in `services/report_service.py` and endpoints in `api/reports.py`:

- **Budget vs expense**: `/api/reports/budget-vs-expense`
  - For each `Budget`, returns limit vs actual expenses (with optional `start_date`/`end_date` window).

- **Expense breakdown by account**: `/api/reports/expense-by-account`
  - Sums expense transactions grouped by `Account`.

- **Recurring transactions report**: `/api/reports/recurring-transactions`
  - Summarizes all `RecurringTransaction` rows (subscriptions view).

These complement the existing:
- `/api/reports/income-expense`
- `/api/reports/category-breakdown`
- `/api/reports/account-balances`
- `/api/reports/budget-status`

## Frontend architecture & UX directives

1. **SPA structure**
   - The app is a single-page application (SPA) using vanilla JS + Rollup.
   - Navigation is handled client-side by swapping visible `section.view` panels.

2. **Layout**
   - Desktop/tablet: VS Code–style shell:
     - Left **sidebar** (`<aside id="sidebar">`) with icon-based navigation for
       dashboard, accounts, transactions, categories, reports, imports, custom reports/settings.
     - Main content on the right (`<main id="main-content">`) containing the current view.
   - Mobile:
     - Sidebar hidden by default.
     - A **hamburger button** in the header toggles the sidebar as an overlay.

3. **Visual style**
   - Overall style: **neumorphic**, light theme inspired by the reference UI kits:
     - Soft backgrounds, rounded surfaces, inner/outer shadows.
     - Buttons, cards, tiles all use a shared neumorphic surface style.
   - Colors:
     - All key colors defined via CSS custom properties (`--color-bg`, `--color-surface`, `--color-accent`, etc.) to allow theming.
     - Accent colors used sparingly for primary actions, focus states, and active nav items.

4. **Icons**
   - Use **Font Awesome Free** icons for navigation and key affordances:
     - Loaded via CDN in `frontend/src/index.html`.
     - Sidebar items show icon + optional label; on smaller screens, icons can be shown without labels.

5. **Responsiveness**
   - Layout is fully responsive:
     - Uses flexbox for sidebar/content layout and for form field rows.
     - Media queries collapse multi-column layouts into single-column on narrow screens.
   - All primary actions and navigation remain reachable and legible on mobile.

6. **Deployment (Docker + Render)**
   - Backend:
     - Deployed as a Docker web service on Render using `backend/Dockerfile`.
   - Frontend:
     - Deployed as a Render static site (Rollup build → `dist/`).
     - Optionally, a Docker-based deployment can be introduced later if needed, but is not required for MVP.

## Implementation plan updates

1. **Backend – Accounting & Reporting**
   - Use `Transaction` + `TransactionLine` for future CoA-based reporting instead of overloading `Transaction`.
   - All new reports should be built over `Transaction` / `TransactionLine` / `ChartOfAccount` where appropriate.

2. **Backend – Custom Reporting**
   - Encourage saving frequently used read-only SQL in `CustomReport` (per user).
   - UI can:
     - List user’s saved reports from `/api/custom-reports`.
     - Let user run ad-hoc SQL via `/api/reports/custom-sql`.
     - Optionally bind a saved report to a UI view (e.g., named custom dashboard widgets).

3. **Frontend – Future work**
   - Extend the current SPA to:
     - Fully use the VS Code–style sidebar + hamburger pattern with Font Awesome icons.
     - Apply neumorphic styling to key components (cards, buttons, tiles, nav).
     - Add UI for:
       - Managing custom reports (CRUD).
       - Viewing/creating transaction splits against chart-of-accounts in transaction forms.
       - Visualizing new reports (budget vs expenses, expense by account, recurring transactions, custom SQL results).


