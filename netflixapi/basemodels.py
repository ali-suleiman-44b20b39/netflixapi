from fastapi import FastAPI
from typing import Optional
from typing import Tuple, List

from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy import create_engine, or_, func
from sqlalchemy.orm import sessionmaker, Query
from sqlalchemy.sql import Alias

class Filter(BaseModel):
    key: str
    values: List[str]


class SortableField(BaseModel):
    key: str
    direction: str = None


class SearchQuery(BaseModel):
    search_term: Optional[str] = None
    filters: Optional[List[Filter]] = None
    sort_by_fields: Optional[List[SortableField]] = None
    summaryFields: Optional[List[str]] = None
    page_size: Optional[int] = 25
    page_selected: Optional[int] = None


class UpdateShowModel(BaseModel):
    type: str = None
    title: str = None
    director: str = None
    cast: str = None
    country: str = None
    date_added: str = None
    release_year: int = None
    rating: str = None
    duration: int = None
    listed_in: str = None
    description: str = None


class ShowModel(BaseModel):
    type: str
    title: str
    director: str
    cast: str
    country: str
    date_added: str
    release_year: int
    rating: str
    duration: str
    listed_in: str
    description: str

    def toList(self):
        return [self.type, self.title, self.director, self.cast, self.country, self.date_added, self.release_year,
                self.rating, self.duration, self.listed_in, self.description]

    def toJson(self):
        return {
            "type": self.type,
            "title": self.title,
            "director": self.director,
            "cast": self.cast,
            "country": self.country,
            "date_added": self.date_added,
            "release_year": self.release_year,
            "rating": self.rating,
            "duration": self.duration,
            "listed_in": self.listed_in,
            "description": self.description
        }
