from datetime import datetime, date
from httpx import Timeout
import asyncio
import httpx
import os
from pathlib import Path
from sqlalchemy.orm import Session
from sqlmodel import Field, Session, SQLModel, create_engine, select, insert, delete
from parser import TitleXMLParser
from models import Agency, CFRReference, Title, CfrDimension, CfrMetric, CfrText,  create_db_and_tables
from sqlalchemy import create_engine

BASE_URL = "https://www.ecfr.gov/api"
XML_Data_DIR = "./api/xml_data"
custom_timeout = Timeout(connect=15.0, read=120.0, write=5.0, pool=True)
sqlite_file_name = "./api/ecfr.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

connect_args = {"check_same_thread": False}
# engine = create_engine(sqlite_url, echo=True, connect_args=connect_args)


async def download_tile_xml_async(title_id: int, issue_date: datetime.date) -> bool:
    """Download XML data for a specific title and date."""
    fmt_dt = issue_date.strftime('%Y-%m-%d')
    dir_path = Path(f"{XML_Data_DIR}/title{title_id}")
    dir_path.mkdir(parents=True, exist_ok=True)
    file_path = dir_path / f"title-{title_id}_{fmt_dt}.xml"

    if os.path.exists(file_path):
        print(f"File {file_path} already exists, skipping download.")
        return True

    url = f'{BASE_URL}/versioner/v1/full/{fmt_dt}/title-{title_id}.xml'

    async with httpx.AsyncClient(timeout=custom_timeout) as client:
        try:
            print(f"Downloading {file_path} from {url}")
            response = await client.get(url)
            response.raise_for_status()

            with open(file_path, 'wb') as f:
                f.write(response.content)

            size_kb = len(response.content) / 1_000
            print(f"Downloaded {file_path} with size {size_kb:.2f} KB")
            return True

        except httpx.ReadTimeout as exc:
            print(f"Read timeout: {exc}")
            return False
        except httpx.HTTPError as exc:
            print(f"HTTP error fetching {url}: {exc}")
            return False
        except IOError as e:
            print(f"Error writing to file {file_path}: {e}")
            return False


async def download_agencies(engine):
    """Download agencies and their CFR references."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/admin/v1/agencies.json")
        response.raise_for_status()
        payload = response.json()
        with Session(engine) as session:
            session.exec(delete(Agency))
            session.exec(delete(CFRReference))
            session.commit()
        
        process_agencies(engine, payload["agencies"])


async def download_titles(engine):
    """Download titles and their details."""
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/versioner/v1/titles.json")
        response.raise_for_status()
        payload = response.json()

        with Session(engine) as session:
            session.exec(delete(Title))
            session.commit()

        process_titles(engine, payload["titles"])


def _get_agency_lookup(engine, agencies: list) -> dict:
    """Create a lookup dictionary for agencies by slug."""
    with Session(engine) as session:
        created_agencies = session.exec(select(Agency)).all()
        return {agency.slug: agency for agency in created_agencies}


def _get_title_dict(engine) -> dict:
    """Create a lookup dictionary for titles by number."""
    with Session(engine) as session:
        return {title.number: title for title in session.exec(select(Title)).all()}


def process_agencies(engine, data, parent=None):
    """Process agencies and their CFR references, and save to the database."""
    agencies = [
        Agency(
            slug=agency_data["slug"],
            name=agency_data["name"],
            short_name=agency_data["short_name"] if "short_name" in agency_data else "",
            display_name=agency_data["display_name"],
            sortable_name=agency_data["sortable_name"],
            parent_id=parent,
        )
        for agency_data in data
    ]
    for agency in data:
        if agency["short_name"]  == "DOI":
            print(agency)
            input()
    with Session(engine) as session:
        session.add_all(agencies)
        session.commit()

    agency_lookup = _get_agency_lookup(engine, agencies)
    title_dict = _get_title_dict(engine)

    cfr_refs = [
        CFRReference(
            agency_slug=agency_lookup[agency_data["slug"]].slug,
            title_id=int(item["title"]),
            subtitle=item.get("subtitle", ""),
            chapter=item.get("chapter", ""),
            part=item.get("part", ""),
            subchapter=item.get("subchapter", ""),
        )
        for agency_data in data
        for item in agency_data["cfr_references"]
    ]

    with Session(engine) as session:
        session.add_all(cfr_refs)
        session.commit()

    for agency_data in data:
        if agency_data.get("children"):
            process_agencies(engine, agency_data["children"], parent=agency_lookup[agency_data["slug"]].slug)


def process_titles(engine, data):
    """Process titles and save to the database."""
    def parse_date(value: str) -> datetime:
        return datetime.strptime(value, '%Y-%m-%d') if isinstance(value, str) else None

    titles = [
        Title(
            number=title_data["number"],
            name=title_data["name"],
            latest_amended_on=parse_date(title_data["latest_amended_on"]),
            latest_issue_date=parse_date(title_data["latest_issue_date"]),
            up_to_date_as_of=parse_date(title_data["up_to_date_as_of"]),
            reserved=title_data["reserved"],
        )
        for title_data in data
    ]

    with Session(engine) as session:
        session.add_all(titles)
        session.commit()

def process_title_xml(engine, title_id: int, issue_date: datetime.date, batch_size=1000):
    """Process XML data for a specific title and date."""
    # get the XML file path
    fmt_dt = issue_date.strftime('%Y-%m-%d')
    file_path = Path(f"{XML_Data_DIR}/title{title_id}/title-{title_id}_{fmt_dt}.xml")
    if not file_path.exists():
        print(f"XML file {file_path} does not exist, skipping processing.")
        return
    items = TitleXMLParser(file_path)
    visited = _get_title_set(engine, issue_date)
    texts = []
    dims = []
    count = 0
    slug_dict = _get_slug_dict(engine)
    for item in items:
        # Process each item in the XML data
        labels, indices,  content = item["dims"], item["keys"], item["text"]
        key = _get_key(int(indices["title"]), issue_date, indices["section"])
        if key in visited:
            continue
        visited.add(key)
        text = CfrText(
            title_id= int(indices["title"]),
            issue_date=issue_date,
            section_id=indices["section"],
            content=content
        )
    
        texts.append(text)
        dim = CfrDimension(
            title_id= int(indices["title"]),
            issue_date=issue_date,
            section_id=indices["section"],
            chapter_id=indices["chapter"] if "chapter" in indices else "",
            subchapter_id=indices["subchapter"] if "subchapter" in indices else "",
            part_id = indices["part"] if "part" in indices else "",
            subpart_id= indices["subpart"] if "subpart" in indices else "",
            agency_slug=slug_dict[f"{indices["title"]}:{indices["chapter"]}"],
            title=labels["title"] if "title" in labels else None,
            chapter=labels["chapter"] if "chapter" in labels else None,
            part=labels["part"] if "part" in labels else None,
            subpart=labels["subpart"] if "subpart" in labels else None,
            section=labels["section"],
        )
        dims.append(dim)
        if len(texts) >= batch_size:
            with Session(engine) as session:
                try:
                    session.add_all(texts)
                    session.add_all(dims)
                    session.commit()
                except Exception as e:
                    print(f"Warning: Batch insert failed (likely duplicates): {e}")
                    session.rollback()
            texts = []
            dims = []
            count += batch_size
            print(f"Processed {count} items.")

    if len(texts) > 0:
        with Session(engine) as session:
            try:
                session.add_all(texts)
                session.add_all(dims)
                session.commit()
            except Exception as e:
                print(f"Warning: Final batch insert failed (likely duplicates): {e}")
                session.rollback()
        count += len(texts)
        print(f"Processed {count} items.")

def _get_slug_dict(engine) -> dict:
    with Session(engine) as session:
        return {f"{cfr.title_id}:{cfr.chapter}": f"{cfr.agency_slug}" 
                    for cfr in session.exec(select(CFRReference)).all()}
 
def _get_key(title_id, issue_date, section_id):
    return f"{title_id}:{issue_date}:{section_id}"

def _get_title_set(engine, issue_date) -> set:
    """Create a lookup dictionary for titles by number."""
    with Session(engine) as session:
        return set([_get_key(dim.title_id, dim.issue_date, dim.section_id) 
                    for dim in session.exec(select(CfrDimension).where(CfrDimension.issue_date == issue_date)).all()])
def main():
    """Example usage of download_tile_async."""
    title_id = 1
    issue_date = datetime.fromisoformat("2022-01-01")
    engine = create_engine(sqlite_url, echo=True, connect_args=connect_args)
    create_db_and_tables(engine)
    
    # Example usage of download_tile_xml_async
    # Uncomment to test download_tile_xml_async
    asyncio.run(download_tile_xml_async(title_id, issue_date))
    
    # Example usage of process_title_xml
    # Uncomment to test process_title_xml
    process_title_xml(engine, title_id, issue_date)

    # Example usage of download_agencies
    # Uncomment to test download_agencies
    #asyncio.run(download_agencies(engine))
    
    # Example usage of download_titles
    # Uncomment to test download_titles
    asyncio.run(download_titles(engine))  # Uncomment to test download_titles


if __name__ == "__main__":
    main()
