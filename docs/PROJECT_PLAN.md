# Project Plan

The canonical, detailed project plan for this application is maintained by
Cursor in the `.cursor/plans/` directory.

For the full specification of goals, architecture, database schema, API
endpoints, and task list, refer to the current plan file there. This document
acts as a lightweight pointer so the repo layout matches the plan.

## Implementation addenda

Since the original plan, the implementation has introduced a few additional
concepts that will be reflected in future iterations of the plan:

- **Custom reports**: a `custom_reports` table and `/api/custom-reports` CRUD
  endpoints allow users to save named, per-user SQL queries, which can be
  executed via the `/api/reports/custom-sql` endpoint (read-only `SELECT`
  queries only).
- **Transaction splits**: a `transaction_lines` table and nested
  `splits` field on transaction schemas link `Transaction` rows to one or more
  `ChartOfAccount` entries, enabling allocation of a single bank transaction
  across multiple chart of accounts for reporting and lightweight accounting.


