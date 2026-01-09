# ECFR Metrics Dashboard

A full-stack application for analyzing and visualizing metrics from Electronic Code of Federal Regulations (ECFR) XML data. Features a FastAPI backend for data processing and metric computation, paired with a Next.js frontend dashboard for interactive exploration.

## Architecture

- **Frontend**: Next.js 16 + React 19 + TypeScript + Tailwind CSS
- **Backend**: FastAPI + SQLModel + SQLite
- **Data Source**: ECFR XML files from [ecfr.gov API](https://www.ecfr.gov/api)

### Data Flow

```
ECFR XML → Parser → SQLite (Text + Dimensions) → Metrics Engine → API → Dashboard
```

1. Download XML files via `fetch_data.py`
2. Parse sections with `parser.py` (yields text + hierarchical dimensions)
3. Store in SQLite: `CfrText`, `CfrDimension`, `Agency`, `Title`
4. Compute metrics via `metrics.py` (word count, diversity, cross-references, etc.)
5. Serve via FastAPI endpoints (`/metric_json`, `/metric`)
6. Visualize in Next.js dashboard with tables and charts

## Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+ (LTS recommended)
- npm or yarn

### Installation

1. **Clone the repository**
```bash
git clone <repo-url>
cd ecfr-metrics
```

2. **Install frontend dependencies**
```bash
npm install
```

3. **Install backend dependencies**
```bash
pip install -r api/requirements.txt
```

### Seed the Database

Run the seed script to download sample data and populate the database:

```bash
python -m api.seed
```

This will:
- Create database tables
- Download agencies and titles metadata
- Download Title 1 XML for 2022-01-01
- Parse and populate `CfrText`/`CfrDimension` tables
- Compute all metrics for the sample data

### Run the Application

**Terminal 1: Start the backend**
```bash
uvicorn --app-dir api app:app --reload --port 8000
```

**Terminal 2: Start the frontend**
```bash
npm run dev
```

Visit **http://localhost:3000** and navigate to the ECFR metrics page.

## API Endpoints

### GET `/metric_json/`
Returns metric data as JSON array.

**Query Parameters:**
- `metric_name` (string): Metric name (e.g., "Word count")
- `level` (int): Aggregation level (0=title, 1=chapter, 2=subchapter, 3=part, 4=subpart, 5=section)
- `start_dt` (ISO date): Start date
- `end_dt` (ISO date): End date
- `agencies` (string, optional): Comma-separated agency slugs (default: "BIA")

**Example:**
```bash
curl "http://localhost:8000/metric_json?metric_name=Word%20count&level=1&start_dt=2022-01-01&end_dt=2022-02-01&agencies=BIA,NSF"
```

### GET `/metric/`
Returns metric data as HTML table (same parameters as above).

### POST `/compute_metrics/`
Trigger metric computation for a title and date range.

**Query Parameters:**
- `title_id` (int): CFR title number
- `start_dt` (ISO date): Start date
- `end_dt` (ISO date): End date

**Example:**
```bash
curl -X POST "http://localhost:8000/compute_metrics?title_id=1&start_dt=2022-01-01&end_dt=2022-01-01"
```

## Available Metrics

1. **Word count** - Total words per section
2. **Keyword count** - Occurrences of "the"
3. **Cross-references Average** - Period count (proxy for citations)
4. **Lexical diversity** - Unique word count
5. **Citation depth** - Period count

*To add a metric:* Append `(name, function)` to `METRICS` list in `api/metrics.py`.

## Project Structure

```
ecfr-metrics/
├── api/
│   ├── app.py              # FastAPI application & endpoints
│   ├── models.py           # SQLModel ORM schemas
│   ├── metrics.py          # Metric definitions & query logic
│   ├── parser.py           # XML parser (TitleXMLParser)
│   ├── fetch_data.py       # Download utilities
│   ├── seed.py             # Database seed script
│   ├── ecfr.db             # SQLite database (generated)
│   └── xml_data/           # Downloaded XML files by title
├── src/
│   ├── app/                # Next.js app router pages
│   ├── components/         # React components
│   │   └── Tables/
│   │       └── ecfr-metrics-client.tsx  # Main metrics UI
│   └── ...
├── package.json
├── requirements.txt
└── README.md
```

## Development

### Backend Development

The backend uses relative imports, so run `uvicorn` from the repo root:

```bash
uvicorn --app-dir api app:app --reload --port 8000
```

Or from the `api/` directory:

```bash
cd api && uvicorn app:app --reload --port 8000
```

**Database inspection:**
```bash
sqlite3 ./api/ecfr.db
# or
sqlitebrowser ./api/ecfr.db
```

### Frontend Development

```bash
npm run dev     # Development server on port 3000
npm run build   # Production build
npm run start   # Production server
```

### Data Ingestion

Download additional titles:

```python
from api.fetch_data import download_tile_xml_async, process_title_xml
from datetime import datetime
import asyncio

# Download XML
title_id = 2
issue_date = datetime(2022, 1, 1).date()
asyncio.run(download_tile_xml_async(title_id, issue_date))

# Parse and populate DB
from sqlmodel import create_engine
engine = create_engine("sqlite:///./api/ecfr.db")
process_title_xml(engine, title_id, issue_date)
```

Then compute metrics via the `/compute_metrics/` endpoint or directly:

```python
from api.metrics import compute_metric
compute_metric(engine, title_id, start_date, end_date)
```

## Tech Stack

**Frontend:**
- Next.js 16 (React 19)
- TypeScript
- Tailwind CSS
- ApexCharts (for visualizations)

**Backend:**
- FastAPI
- SQLModel (SQLAlchemy + Pydantic)
- SQLite
- httpx (async HTTP client)
- pandas (data manipulation)

## Configuration

**CORS:** Configured in `api/app.py` for `localhost:3000` and `localhost:8000`.

**Database:** SQLite at `./api/ecfr.db`. Delete to reset.

**XML Storage:** `./api/xml_data/title{N}/` - organized by title number.

## License

This project uses the NextAdmin template for the frontend UI. See original template documentation for licensing details.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

For questions or issues, please open a GitHub issue.
