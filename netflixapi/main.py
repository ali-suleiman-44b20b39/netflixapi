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

#loadData()
app = FastAPI()

# ORMs.loadData()

print("ALI CONSOLE LOADED! =)")
#SQLALCHEMY_DATABASE_URL = 'sqlite:///:memory:'
SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, echo=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

session = SessionLocal()




@app.get("/")
async def root():
    return {"message": "Hello World"}


# http://127.0.0.1:8000/search/
@app.post("/search/")
async def search(query: SearchQuery):
    q = session.query(Show)
    q = applyFilters(q, query.filters)
    q = applySearch(q, query.searchTerm)
    q = applySort(q, query.sortableFields)
    results = applyLimit(q, query.maxPerPage, query.page)
    summary = {}
    # summary = applyAggr(q)

    print(summary)

    return {"resr": results,
            "summary": summary}


@app.post("/Shows/")
async def addShow(show: ShowModel):
    print(show)
    row = show.toList()
    print(row)
    print(len(row))
    newShow = Show(*row)
    session.add(newShow)
    session.commit()
    return newShow.toJson()


@app.delete("/Shows/{show_id}/")
async def deleteShow(show_id):
    show = session.query(Show).filter(Show.show_id == show_id).first()
    session.delete(show)
    session.commit()
    return {"deleted": show_id}


@app.put("/Shows/{show_id}/")
async def updateShow(show_id: int, model: dict):
    show = session.query(Show).filter_by(show_id=show_id).first()
    for key in model:
        setattr(show, key, model[key])
    session.commit()
    return show.toJson()

@app.post("recommendations/{title}/")
async def getRecommendations(title):
    return {"title": title}


'''
search, filter, sorting, and pagination
Aggregate Summary Data

search:
list of k,vs field and terms 

filter
list of keys and terms (where like behavior)

sorting, sort by list of keys and direction
exmaple: &cast=asc&date_added=dec


Order of operations:
filter, search, sort

PArt2 Flex: 

'''
