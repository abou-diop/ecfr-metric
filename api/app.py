import json
import pprint
from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from fastapi.middleware.cors import CORSMiddleware
from httpx import Timeout
import pandas as pd
from metrics import getTable, gettable, METRICS_MAP, compute_metric
from sqlmodel import Field, Session, SQLModel, create_engine, select, insert, delete
from typing import List
from models import Agency
from datetime import datetime


BASE_URL = "https://www.ecfr.gov/api"
XML_Data_DIR = "./api/xml_data"
custom_timeout = Timeout(connect=15.0, read=120.0, write=5.0, pool=True)
sqlite_file_name = "./api/ecfr.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
connect_args = {"check_same_thread": False}
engine = create_engine(sqlite_url, echo=True, connect_args=connect_args)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

app = FastAPI()

# Allow cross-origin requests from local dev frontends
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()
    
 
@app.get("/metric/", response_class=HTMLResponse)
def get_metric_table(metric_name: str, level: int, start_dt: datetime, end_dt: datetime, agencies: str = "BIA"):
    """Return an HTML table for the named metric.

    Query params: `metric_name`, `level`, `start_dt`, `end_dt`, `agencies` (comma-separated slugs; default "BIA").
    """
    # validate metric name
    if metric_name not in METRICS_MAP:
        return HTMLResponse(content=f"Unknown metric: {metric_name}", status_code=400)

    agency_list = [a.strip() for a in agencies.split(",")]
    rows = gettable(engine, metric_name, agency_list, level, start_dt, end_dt)
    df = pd.DataFrame(rows)
    html_table = df.to_html(index=False, border=1)
    return f"""
    <html>
        <head><title>FastAPI HTML</title></head>
        <body>{html_table}</body>
    </html>
    """


@app.get("/metric_json/")
def get_metric_json(metric_name: str, level: int, start_dt: datetime, end_dt: datetime, agencies: str = "BIA"):
    """Return JSON list-of-dicts using `gettable` from `metrics.py`.

    Query params: `metric_name`, `level`, `start_dt`, `end_dt` (ISO dates), `agencies` (comma-separated slugs; default "BIA").
    """
    if metric_name not in METRICS_MAP:
        return {"error": f"Unknown metric: {metric_name}"}
    agency_list = [a.strip() for a in agencies.split(",")]
    rows = gettable(engine, metric_name, agency_list, level, start_dt, end_dt)
    return rows


@app.post("/compute_metrics/")
def compute_metrics(title_id: int, start_dt: datetime, end_dt: datetime):
    """Trigger metric computation for a title and date range.
    
    Query params: `title_id`, `start_dt`, `end_dt` (ISO dates).
    Computes all metrics for all sections in the date range and writes to DB.
    Returns status message upon completion.
    """
    try:
        compute_metric(engine, title_id, start_dt, end_dt)
        return {"status": "success", "message": f"Computed metrics for title {title_id} from {start_dt} to {end_dt}"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


