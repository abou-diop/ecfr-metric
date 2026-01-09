from pathlib import Path
from fastapi import FastAPI
import httpx
from sqlmodel import Field, Session, SQLModel, create_engine, select, insert, delete
from datetime import datetime, date
from pydantic import field_validator
from sqlalchemy.dialects import sqlite
from sqlalchemy import text
from fastapi.responses import Response
from httpx import Timeout
import asyncio
import os

METRICS = ['Average words per group',
           'Keyword count per group',
           'Lexical diversity',
           'Average cross-references per group',
           'Lexical similarity',
           'Citation depth']

class CfrDimension(SQLModel, table=True):
    title_id: int = Field(primary_key=True)
    section_id: str = Field(primary_key=True, max_length=128)
    issue_date: datetime = Field(primary_key=True)
    chapter_id: str
    subchapter_id: str
    part_id : int
    subpart_id: str
    agency_slug:str = Field(index = True)
    title: str | None = Field(default=None, index=True)
    chapter: str | None = Field(default=None, index=True)
    subchapter: str | None = Field(default=None, index=True)
    part: int | None = Field(default=None, index=True)
    subpart: str | None = Field(default=None, index=True)
    section: str | None = Field(default=None, index=True)

    
class CfrText(SQLModel, table=True):
    title_id: int = Field(primary_key=True)
    section_id: str = Field(primary_key=True)
    issue_date: datetime = Field(primary_key=True)
    content : str
    
class CfrMetric(SQLModel, table=True):
    title_id: int = Field(primary_key=True)
    section_id: str = Field(primary_key=True)
    issue_date: datetime = Field(primary_key=True)
    metric_id: int = Field(primary_key=True)
    value: float
    
class Agency(SQLModel, table=True):
    slug: str = Field(primary_key=True, max_length=255)  # Assuming slug is unique and has a max length of 255 characters
    name: str
    short_name: str  | None = Field(default=None)
    display_name: str
    sortable_name: str
    parent_id: int | None = Field(default=None, foreign_key="agency.slug")
 
class CFRReference(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    agency_slug: str = Field(foreign_key="agency.slug")
    title_id: int = Field(foreign_key="title.number")
    chapter: str | None = Field(default=None, index=True)
    subtitle: str | None = Field(default=None, index=True)
    part: str | None = Field(default=None, index=True)
    subchapter: str | None = Field(default=None, index=True)   

class Title(SQLModel, table=True): 
    number: int = Field(primary_key=True)
    name: str
    latest_amended_on: datetime | None = Field(default=None)
    latest_issue_date: datetime | None = Field(default=None)
    up_to_date_as_of: datetime | None = Field(default=None)
    reserved: bool | None = Field(default=False)

    @field_validator("latest_amended_on", "latest_issue_date", "up_to_date_as_of")
    def parse_date(cls, value: str) -> datetime:
        print(value, datetime.strptime(value, '%Y-%m-%d'))
        if isinstance(value, str):
            # Example for a custom format: "DD-MM-YYYY"
            print(value, datetime.strptime(value, '%Y-%m-%d'))
            return datetime.strptime(value, '%Y-%m-%d')
        
        raise None 
  
    
class TitleContent(SQLModel, table=True):
    amendment_date: datetime = Field(primary_key=True)
    issue_date: datetime = Field(primary_key=True)
    identifier: str = Field(primary_key=True)
    name: str
    part: int
    substantive: bool = Field(primary_key=True)
    removed: bool = Field(primary_key=True)
    subpart: str | None
    title: int = Field(primary_key=True)
    content_type: str
    

def create_db_and_tables(engine):
    SQLModel.metadata.create_all(engine)