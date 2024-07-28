from .database.engine import DbWrapper

from .ingest.scraper import Scraper

from fastapi import Depends, FastAPI

from .routers import scrape
from .routers import analytics


def get_db():
	db = DbWrapper().connect(reinitialize_objects = False)
	try:
		yield db
	finally:
		db.close()

def get_scraper():
	db = DbWrapper().connect(reinitialize_objects = False)
	scraper = Scraper(db)
	try:
		yield scraper
	finally:
		db.close()


app = FastAPI(dependencies=[Depends(get_db), Depends(get_scraper)])

app.include_router(scrape.router)
app.include_router(analytics.router)


@app.get("/")
async def root():
    return {"message": "Welcome to scraper"}
