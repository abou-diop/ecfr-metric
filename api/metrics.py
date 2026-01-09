from datetime import datetime
from typing import List, Callable, Dict, Any
from sqlmodel import Session, select, text
from models import (
    CfrMetric,
    CfrText,
    Agency,
    Title,
    CFRReference,
    CfrDimension,
    TitleContent,
    create_db_and_tables,
)
import pandas as pd
import json

def compute_word_count(text: str) -> int:
    words = text.split()
    return len(words)

def keyword_count(text: str) -> int:    
    return text.count('the')

def cross_reference_count(text: str) -> int:
    return text.count('.')

def diversity(text: str) -> int:
    words = text.split()
    unique_words = set(words)
    return len(unique_words)

def citation_depth(text: str) -> int:
    return text.count('.')


METRICS = [
    ("Word count", compute_word_count),
    ("Keyword count", keyword_count),
    ("cross-references Average", cross_reference_count),
    ("Lexical diversity", diversity),
    ("Citation depth", citation_depth),
]

# Helper maps for name <-> id lookup
METRICS_MAP: Dict[str, int] = {name: idx for idx, (name, _) in enumerate(METRICS)}
METRICS_FUNCS: Dict[str, Callable[[str], Any]] = {name: func for name, func in METRICS}



XML_Data_DIR = "./xml_data"
sqlite_file_name = "./api/ecfr.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

LEVEL_NAMES = ["Title", "Chapter", "Subchapter", "Part", "Subpart", "Section"]

def getTable(engine, metric_id:int, agencies:List[str], level:int, start_dt:datetime, end_st:datetime):
    """Return raw rows from the DB for the given metric id.

    This function expects an integer `metric_id` (index into METRICS).
    Use `gettable` for JSON-serializable responses that accept metric names.
    
    Args:
        engine: SQLModel engine
        metric_id: index into METRICS list
        agencies: list of agency short names to filter by
        level: dimension level (0=title, 1=chapter, 2=subchapter, 3=part, 4=subpart, 5=section)
        start_dt: start datetime
        end_st: end datetime
    """
    agency_dict = _get_agency_dict(engine)
    Levels =[ CfrDimension.title,  CfrDimension.chapter,  CfrDimension.subchapter,  CfrDimension.part,  CfrDimension.subpart, CfrDimension.section]
    level_col = Levels[level]
    # Safely build agency slug list from known agencies
    try:
        agency_slugs = [agency_dict[short_name].slug for short_name in agencies]
    except KeyError as e:
        raise ValueError(f"Unknown agency: {e}. Available: {list(agency_dict.keys())}")
    agencies_set = ",".join([f"'{slug}'" for slug in agency_slugs])
    query = text(f"select cfrDimension.agency_slug, cfrDimension.title, {level_col},  cfrMetric.issue_date, sum(cfrmetric.value)  from cfrdimension, cfrmetric "
                    f"where  CfrMetric.metric_id == {metric_id} "
                    f"and cfrdimension.agency_slug in ({agencies_set}) "
                    "and cfrDimension.title_id == cfrMetric.title_id "
                    "and cfrDimension.issue_date == cfrMetric.issue_date "
                    "and cfrDimension.section_id == cfrMetric.section_id "
                    f"group by  cfrDimension.agency_slug, cfrDimension.title,  {level_col}, cfrMetric.issue_date")
    
    rows = []
    with Session(engine) as session:
        items = session.exec(query)
        for item in items:
            rows.append(item)
       
    return rows    


def gettable(engine, metric_name: str, agencies:List[str], level:int, start_dt:datetime, end_st:datetime):
    """Return JSON-serializable list-of-dicts for a table query.

    Matches the HTML table produced by `get_metric_table` in `app.py` but
    returns structured data suitable for API/JSON responses or page queries.
    """
    # Map metric name to id
    metric_id = METRICS_MAP.get(metric_name)
    if metric_id is None:
        raise ValueError(f"Unknown metric name: {metric_name}")
    rows = getTable(engine, metric_id, agencies, level, start_dt, end_st)
    headers = ["agency_slug", "Title", "Level_Name", "Level", "Date", "Value"]
    list_of_dicts = []
    for row in rows:
        row = list(row)
        # Insert level name before the level value
        row.insert(2, LEVEL_NAMES[level])
        # Normalize datetime to ISO format for JSON
        if isinstance(row[4], datetime):
            row[4] = row[4].isoformat()
        list_of_dicts.append(dict(zip(headers, row)))
    return list_of_dicts

    
def compute_metric(engine, title_id: int, start_dt: datetime, end_dt: datetime, batch_size = 10000):
    metrics = []
    with Session(engine) as session:
        # Generate a range of dates
        for issue_date in pd.date_range(start=start_dt, end=end_dt, freq='D'):
            texts = session.exec(select(CfrText).where(CfrText.issue_date == issue_date and CfrText.title_id == title_id))
            visited = _get_metric_set(engine, title_id, issue_date)
            for text in texts:
                for metric_id, m in enumerate(METRICS):
                    key = _get_metric_key(title_id, issue_date, text.section_id, metric_id)
                    if key in visited:
                        continue
                    visited.add(key)
                    _, compute_func = m
                    result = compute_func(text.content)
                    metric = CfrMetric(title_id= title_id, section_id=text.section_id, issue_date=text.issue_date, metric_id=metric_id, value=result)
                    metrics.append(metric)
                    if len(metrics) >= batch_size:
                        session.add_all(metrics)
                        session.commit()
                        metrics = []
        if metrics:
            session.add_all(metrics)
            session.commit()
            
def _get_agency_dict(engine) -> dict:
    with Session(engine) as session:
        return {f"{agency.short_name}": agency 
                    for agency in session.exec(select(Agency)).all()}  
 
def _get_metric_key(title_id, issue_date, section_id, metric_id):
     return f"{title_id}:{issue_date}:{section_id}:{metric_id}"
             
def _get_metric_set(engine, title_id, issue_date) -> set:
    with Session(engine) as session:
        return set([_get_metric_key(cfr.title_id, cfr.issue_date, cfr.section_id, cfr.metric_id)
                    for cfr in session.exec(select(CfrMetric).where(CfrMetric.title_id == title_id and CfrMetric.issue_date == issue_date)).all()])  

def main():
    connect_args = {"check_same_thread": False}
    engine = create_engine(sqlite_url, echo=True, connect_args=connect_args)
    create_db_and_tables(engine)
    title_id = 25
    start_date = datetime.fromisoformat("2022-01-01")
    end_date = datetime.fromisoformat("2022-02-01")

    #ompute_metric(engine, title_id, start_date, end_date)
    
    # getTable(engine, 0, ["ACUS", "BIA", "NSF", "DOI"], 5, start_date, end_date)
    rows = getTable(engine, 0, ["BIA"], 1, start_date, end_date)
    headers = ["agency_slug", "Title", "Level",  "Date", "Value" ]
    list_of_dicts = []
    for row in rows:
        list_of_dicts.append(dict(zip(headers, row)))
    # Serialize the list of dictionaries to a JSON string
    data = json.loads(json.dumps(list_of_dicts))
    print(data)
        # Convert the list of dictionaries to a Pandas DataFrame
    df = pd.DataFrame(data)

    # Convert the DataFrame to an HTML table string
    html_table = df.to_html(index=False, border=1)

    print(html_table)
    # print(json_output)
if __name__ == "__main__":    
    main()


  



  

