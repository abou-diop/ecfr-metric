#!/usr/bin/env python
"""
Seed script: Download and populate DB with one title/date for demo purposes.

Usage:
  From repo root:
    python -m api.seed
  Or from api/ dir:
    python seed.py

This will:
  1. Create DB tables
  2. Download agencies and titles metadata
  3. Download one sample title XML (Title 1, 2022-01-01)
  4. Parse and populate CfrText/CfrDimension
  5. Compute all metrics for that data
  
The frontend can then immediately query /metric_json and display charts.
"""

import asyncio
from datetime import datetime
from pathlib import Path
from sqlmodel import create_engine

from fetch_data import (
    download_agencies,
    download_titles,
    download_tile_xml_async,
    process_title_xml,
)
from models import create_db_and_tables
from metrics import compute_metric

# DB config
sqlite_file_name = "./api/ecfr.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
connect_args = {"check_same_thread": False}


async def seed_db():
    """Download and seed DB with sample data."""
    print("🌱 Starting DB seed...\n")

    # Create engine and tables
    engine = create_engine(sqlite_url, echo=False, connect_args=connect_args)
    create_db_and_tables(engine)
    print("✅ Created DB tables\n")

    # Download agencies and titles metadata
    print("📥 Downloading agencies...")
    await download_agencies(engine)
    print("✅ Agencies loaded\n")

    print("📥 Downloading titles...")
    await download_titles(engine)
    print("✅ Titles loaded\n")

    # Download one sample title XML
    title_id = 1
    issue_date = datetime.fromisoformat("2022-01-01").date()
    
    print(f"📥 Downloading Title {title_id} ({issue_date})...")
    success = await download_tile_xml_async(title_id, issue_date)
    if not success:
        print(f"❌ Failed to download Title {title_id}")
        return

    # Check if file exists
    fmt_dt = issue_date.strftime("%Y-%m-%d")
    file_path = Path(f"./api/xml_data/title{title_id}/title-{title_id}_{fmt_dt}.xml")
    if not file_path.exists():
        print(f"❌ XML file not found: {file_path}")
        return
    print("✅ XML downloaded\n")

    # Parse and populate DB
    print(f"📝 Processing Title {title_id} XML...")
    process_title_xml(engine, title_id, issue_date)
    print("✅ XML parsed and loaded\n")

    # Compute metrics
    print(f"⚙️  Computing metrics for Title {title_id}...")
    compute_metric(engine, title_id, issue_date, issue_date)
    print("✅ Metrics computed\n")

    print("🎉 DB seed complete!")
    print("\nYou can now query the API:")
    print("  GET /metric_json/?metric_name=Word%20count&level=1&start_dt=2022-01-01&end_dt=2022-01-01")
    print("  GET /metric/?metric_name=Word%20count&level=1&start_dt=2022-01-01&end_dt=2022-01-01")


if __name__ == "__main__":
    asyncio.run(seed_db())
