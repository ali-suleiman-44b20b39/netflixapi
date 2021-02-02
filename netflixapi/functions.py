from fastapi import FastAPI
from typing import Optional
from typing import Tuple, List

from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy import create_engine, or_, func
from sqlalchemy.orm import sessionmaker, Query
from sqlalchemy.sql import Alias

from basemodels import *
from functions import *
from orms import *

def applyFilters(q: Query, filters: List[Filter]) -> Query:
    if filters is None:
        return q
    for _filter in filters:
        _filter.key
        filterExpressions = []
        for val in _filter.values:
            filterExpressions += [Show.__dict__[_filter.key] == val]
        q = q.filter(or_(*filterExpressions))
    return q


def applySearch(q: Query, text: str) -> Query:
    if text is None:
        return q
    q = q.filter(Show.title.like(f'%{text}%'))
    return q


def applySort(q: Query, sortableFields: List[SortableField]) -> Query:
    if sortableFields is None:
        return q
    for field in sortableFields:
        q = q.order_by(Show.__dict__[field.key])
    return q


def applyLimit(q: Query, limit: int, page: int) -> List[Show]:
    if limit is None:
        return q.all()
    if page is None:
        page = 0
    q = q[page * limit:page * limit + limit]
    print(len(q))
    return q


def applyAggr(q: Query) -> dict:
    sub = q.order_by(Show.release_year).subquery()
    count = session.query(func.count(sub.c.title)).first()[0]
    sum = session.query(func.sum(sub.c.release_year)).first()[0]
    min = session.query(func.min(sub.c.release_year)).first()[0]
    max = session.query(func.max(sub.c.release_year)).first()[0]
    middle = int(count / 2)
    if count % 2 == 0:
        offset = 2
    else:
        offset = 1
    median = session.query(sub.c.release_year)[middle:middle + offset]
    if len(median) == 2:
        med = (median[0][0] + median[1][0]) / 2
        print(f"med/2 {med}")
    else:
        med = median[0][0]
        print(f"med  {med}")

    average = sum / count
    summary = {"min": min, "max": max, "avg": average, "count": count, "median": med}

    return summary