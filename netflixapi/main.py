from fastapi import Body

from basemodels import *
from functions import *
from orms import *



tags_metadata = [
    {
        "name": "Search",
        "description": "Search",
    },
    {
        "name": "Shows",
        "description": "Add, Update, and Delete Shows",
    },
]


description = r"""

<a href='https://github.com/ali-suleiman-44b20b39/netflixapi'>https://github.com/ali-suleiman-44b20b39/netflixapi</a>

Welcome to netflixapi! This is a quick overview of what this API does from a high level. The detailed documentation can be found here:
[URL]

This is a simple API using the following data:
https://www.kaggle.com/shivamb/netflix-shows/data

## Search, Filter, Sort, Summarize, and Paginate

I wanted to allow the use of these functions in combination. To make the API as flexable as possible. All operations are optional, and are applied in the following order, a step will either be skipped, or defaults will be applied when not specified.

Filter -> Search -> Sort -> Summarize -> Paginate

### Filter
A filter is composed of a column name (key), and list of values. The filter will filter out all values that not in the list values. This API allows the use of multiple filters. 

Example: (k1, [k1v1,k1v2, ... k1vN]) , (k2, [k2v1, k2v2, ... k2vN]) , ... (kM, [kMv1, kMv2, ... kMvN])

Each filter is applied one after the other, if no filters are provided no filtering takes place. 

### Search
Search is applied after filtering, this is a basic like %searchterm% search. TODO: change this to apply multiple search terms.


### Sort
This function will sort the result based on column names (keys) provided, it accepts an ordered list of columns to sort by. So it will sort by A then B, then N.


### Summarize
This function will provide summary statistics on the output of search and filter for each column name provided. We can provide a list of column names, and create a summary for each.

Numerical Summary includes, Min, Max, Mean, Median, and Count.

String Summary includes count

### Paginate
Paginating accepts 2 values, the desired a page to return, and the maximum number of values to show per page. The client will basically increment the desired page or jump to the desired page of choice. 


By allowing the use of multiple functions together, we can answer a broad set of questions about our data. For example we could find out with the average length of a south Korean romance film by doing the following psuedo example:

[Filter(Type,Movie), Filter(,Country,(South Korea)), Filter(Genre, Romance)] -> Summarize(Duration)

Or maybe we want to find the top 10 American shows with most Season

Filter(Type, TV Show) -> Sort(Duration) -> MaxPage(10)


This solution provides allot of flexability to the client application, so that any number of questions can be asked against the data.


## Making Changes to Data
This application allows Adding (POST), Removing (DELETE) and Updating Shows (PUT). Using some HTTP Verb along with the provide show ID in the request URI.

* Adding a show, requires all fields to be provided in the request body except for the show_id.
* Deleting a show, requires the show Id to be provided in the URI.
* Updating a show, requires the fields to be overwritten in the request body. All excluded fields remain unchanged.

"""


app = FastAPI(docs_url="/", title="NetflixAPI", description=description, openapi_tags=tags_metadata)

#SQLALCHEMY_DATABASE_URL = 'sqlite:///:memory:'
SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, echo=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

session = SessionLocal()



# http://127.0.0.1:8000/search/
@app.post("/search/", tags=["Search"])
async def search(query: SearchQuery):
    q = session.query(Show)
    q = applyFilters(q, query.filters)
    q = applySearch(q, query.searchTerm)
    q = applySort(q, query.sortableFields)
    results, totalPages = applyLimit(q, query.maxPerPage, query.page)
    summary = applyAggr(q)
    return {"resr": results,
            "summary": summary}

@app.post("/Shows/", tags=["Shows"])
async def addShow(show: ShowModel):
    print(show)
    row = show.toList()
    print(row)
    print(len(row))
    newShow = Show(*row)
    session.add(newShow)
    session.commit()
    return newShow.toJson()


@app.delete("/Shows/{show_id}/", tags=["Shows"])
async def deleteShow(show_id):
    show = session.query(Show).filter(Show.show_id == show_id).first()
    session.delete(show)
    session.commit()
    return {"deleted": show_id}


@app.put("/Shows/{show_id}/", tags=["Shows"])
async def updateShow(show_id: int, model: dict = Body(..., example={"description": "Change the description, but leave everything else the same"}) ):
    show = session.query(Show).filter_by(show_id=show_id).first()
    for key in model:
        setattr(show, key, model[key])
    session.commit()
    return show.toJson()
