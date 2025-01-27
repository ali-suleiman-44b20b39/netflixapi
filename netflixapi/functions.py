import time

from fastapi import FastAPI
from typing import Optional
from typing import Tuple, List

from fastapi import FastAPI
from pydantic import BaseModel
from sqlalchemy import create_engine, or_, func
from sqlalchemy.orm import sessionmaker, Query
from sqlalchemy.sql import Alias
import shlex

from basemodels import *
from functions import *
from orms import *
import math

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
    terms = shlex.split(text)
    for term in terms:
        q = q.filter(Show.title.like(f'%{term}%'))
    return q


def applySort(q: Query, sortableFields: List[SortableField]) -> Query:
    if sortableFields is None:
        return q
    for field in sortableFields:
        if field.direction == "desc":
            q = q.order_by(getattr(Show, field.key).desc())
        else:
            q = q.order_by(getattr(Show, field.key))
    return q


def applyLimit(q: Query, limit: int, page: int) -> Tuple[List[Show], int]:

    max = q.count()
    if limit is None:
        return q.all()
    if page is None:
        page = 1
    page = page - 1
    if limit >= max:
        limit = max
    if limit == 0:
        pagination = {"current_page": 0,
                      "max_page": 0,
                      "page_size": 0,
                      "showing_items": [0,0]}
        return q.all(), pagination
    totalPages = math.ceil(max/limit)

    if page * limit + limit >= max:
        upperLimit = max
    else:
        upperLimit = page * limit + limit

    if page*limit <= max:
        lowerLimit = page*limit
    else:
        lowerLimit = 0

    if page is None:
        page = 0
    q = q[lowerLimit:upperLimit]
    # print(len(q))

    pagination = {"current_page": page+1,
                  "max_page": totalPages,
                  "page_size": limit,
                  "showing_items": [lowerLimit+1,upperLimit]}

    return q, pagination


def breakDown(q: Query) -> dict:
    for attribute in ["type","rating"]:
        sub = q.order_by(getattr(Show, attribute)).subquery()
        q.group_by()
        total_count = q.count()
        pareto = session.query(attribute, func.count(getattr(sub.c, attribute)),func.count(getattr(sub.c, attribute))/float(total_count)).group_by(getattr(sub.c, attribute))
        # print(pareto.all())
        # print(total_count)


def applyAggr(q: Query) -> dict:
    summary = {}
    if q.count() == 0:
        return None
    for attribute in ["release_year", "duration"]:
        sub = q.order_by(getattr(Show, attribute)).subquery()
        count = session.query(func.count(sub.c.title)).first()[0]
        sum = session.query(func.sum(getattr(sub.c, attribute))).first()[0]
        min = session.query(func.min(getattr(sub.c, attribute))).first()[0]
        max = session.query(func.max(getattr(sub.c, attribute))).first()[0]
        middle = int(count / 2)
        if count % 2 == 0:
            offset = 2
        else:
            offset = 1
        median = session.query(getattr(sub.c, attribute))[middle:middle + offset]
        if len(median) == 2:
            med = (median[0][0] + median[1][0]) / 2
            # print(f"med/2 {med}")
        else:
            med = median[0][0]
            # print(f"med  {med}")

        average = sum / count
        breakDown(q)
        summary[attribute] = {"min": min, "max": max, "avg": int(average), "count": count, "median": med}

    return summary
