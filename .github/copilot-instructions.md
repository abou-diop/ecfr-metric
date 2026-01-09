Project-specific instructions for AI coding agents

This repo pairs a Next.js frontend (NextAdmin template) with a FastAPI backend that parses ECFR XML, stores section text + dimensions in SQLite, computes metrics, and serves them via simple endpoints.

**Architecture**
- **Frontend**: Next.js under [src](../src) with scripts in [package.json](../package.json). Dev via `npm run dev` on 3000.
- **Backend**: FastAPI app in [api/app.py](../api/app.py) using `sqlmodel` and SQLite at `./api/ecfr.db`.
- **Data Flow**: XML files → parsed by [api/parser.py](../api/parser.py) → stored via models in [api/models.py](../api/models.py) → metrics computed in [api/metrics.py](../api/metrics.py) → served by endpoints in [api/app.py](../api/app.py).

**Key Files**
- **api/app.py**: CORS, engine, startup `create_db_and_tables()`, endpoints `/metric` (HTML) and `/metric_json` (JSON).
- **api/metrics.py**: `METRICS` list [(name, func)], `METRICS_MAP`, `compute_metric()`, `getTable()` (raw SQL), `gettable()` (JSON shaping).
- **api/models.py**: Tables `CfrText`, `CfrDimension`, `CfrMetric`, `Agency`, `Title`, `CFRReference` with composite keys aligning text/dim/metric.
- **api/fetch_data.py**: Utilities to download agencies, titles, and XML; `process_title_xml()` populates `CfrText`/`CfrDimension` from XML.
- **api/xml_data/**: Staged XML files by title (e.g., `title1/title-1_2015-12-18.xml`).

**Run / Build**
- **Frontend**: `npm install` then `npm run dev` (port 3000). Build: `npm run build && npm run start`.
- **Backend (dev)**: From repo root, either:
  - `uvicorn --app-dir api app:app --reload --port 8000` (recommended), or
  - `cd api && uvicorn app:app --reload --port 8000`.
  The code uses relative imports (`from metrics import ...`), so `--app-dir api` (or `cd api`) is required.
- **DB**: Created automatically on startup at `./api/ecfr.db`.

**Data Ingestion**
- Download a title XML: use `download_tile_xml_async(title_id, date)` in [api/fetch_data.py](../api/fetch_data.py).
- Populate DB from XML: call `process_title_xml(engine, title_id, issue_date)` to write `CfrText` and `CfrDimension` rows.
- Load reference data: `download_agencies(engine)` and `download_titles(engine)` populate `Agency` and `Title`.
  Note: `fetch_data.py` includes a `main()` with example calls—toggle/comment as needed before running.

**Metrics Conventions**
- **Index-based registry**: `METRICS` is the single source of truth. Names are mapped to integer IDs via `METRICS_MAP`. Queries use the ID.
- **Adding a metric**: Append `(name, func)` to `METRICS`. The `METRICS_MAP`/`METRICS_FUNCS` are derived automatically.
- **Computation**: `compute_metric(engine, title_id, start_dt, end_dt)` iterates `CfrText` rows and writes `CfrMetric` in batches.

**API Endpoints**
- `/metric_json?metric_name=Word%20count&level=1&start_dt=2022-01-01&end_dt=2022-02-01` → list of dicts.
- `/metric?metric_name=Word%20count&level=1&start_dt=2022-01-01&end_dt=2022-02-01` → small HTML table.
  Notes:
  - `level` selects a dimensional column (title/chapter/subchapter/part/subpart/section); see `Levels` in `getTable()`.
  - Current implementation hardcodes `agencies=["BIA"]` in `app.py`. Adjust to query multiple agencies.

**Conventions & Gotchas**
- **Raw SQL**: `getTable()` builds a `text(...)` query. If you expand inputs (e.g., agencies), prefer parameterized SQL to avoid injection and ensure proper comma separation.
- **Relative paths**: Backend assumes repo-root CWD for DB path `./api/ecfr.db` and XML under `./api/xml_data`. Keep CWD consistent with run command above.
- **Duped constants**: A `METRICS` list also appears in `models.py` but is not used by the query/compute path; treat `metrics.py` as authoritative.
- **CORS**: Allows `http://localhost:3000` and `http://localhost:8000` for local dev.

**First Steps for AI Agents**
- Skim [api/app.py](../api/app.py), [api/metrics.py](../api/metrics.py), and [api/models.py](../api/models.py) to align on schema and metric lookup.
- If testing end-to-end, run the backend with `--app-dir api`, load agencies/titles, parse at least one XML via `process_title_xml()`, then hit `/metric_json`.
- When modifying SQL in `getTable()`, add a quick local call through a `Session(engine)` to validate the result shape before wiring UI.

If anything here is unclear or incomplete, ask which file/endpoint to surface and I’ll link exact lines to guide edits.
