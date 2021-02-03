from sqlalchemy import Column, Integer, String, DateTime, Boolean, Enum, Date, Sequence, create_engine, ForeignKey, \
    MetaData
from sqlalchemy.ext.declarative import declarative_base
import csv

from sqlalchemy.orm import sessionmaker, relationship

# SQLALCHEMY_DATABASE_URL = 'sqlite:///:memory:'
SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"
# SQLALCHEMY_DATABASE_URL = "postgresql://user:password@postgresserver/db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, echo=True
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
session = SessionLocal()

Base = declarative_base()


class Show(Base):
    __tablename__ = 'showData'
    show_id = Column(Integer, Sequence('show_id_seq'), primary_key=True)
    type = Column(String)
    title = Column(String)
    director = Column(String)
    cast = Column(String)
    country = Column(String)
    date_added = Column(String)
    release_year = Column(Integer)
    rating = Column(String)
    duration = Column(Integer)
    listed_in = Column(String)
    description = Column(String)

    def __init__(self, _type, title, director, cast, country, date_added, release_year, rating, duration,
                 listed_in, description):
        self.type = _type
        self.title = title
        self.director = director
        self.cast = cast
        self.country = country
        self.date_added = date_added
        self.release_year = release_year
        self.rating = rating
        self.duration = self.parseDuration(duration)
        self.duration_unit = self.getDurationUnit(_type)
        self.listed_in = listed_in
        self.description = description

    def parseDuration(self, val):
        res = ""
        for c in val:
            if c not in "0123456789":
                continue
            else:
                res += c
        if res == "":
            res = 1
        return int(res)

    def getDurationUnit(self,type):
        if type == "Movie":
            return "Minutes"
        elif type == "TV Show":
            return "Seasons"

    def toJson(self):
        return {
            "show_id": self.show_id,
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


def loadData():
    lineCount = 0
    m = 4
    with open("data/netflix_titles.csv", newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for index, row in enumerate(spamreader):
            lineCount += 1
            s = Show(*row[1:])
            session.add(s)


if __name__ == '__main__':
    loadData()
    Base.metadata.create_all(engine)
    session.commit()
