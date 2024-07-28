import json 

from typing import Annotated

from ..database.models.restaurant import Restaurant
from ..database.models.menu import Menu

from fastapi import status, APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from ..ingest.scraper import Scraper
from ..database.engine import DbWrapper

router = APIRouter()

#async def main():
def get_db():
	db = DbWrapper().connect(reinitialize_objects = False)
	try:
		yield db
	finally:
		db.close()

#async def main():
def get_scraper():
	db = DbWrapper().connect(reinitialize_objects = False)
	scraper = Scraper(db)
	try:
		yield scraper
	finally:
		db.close()

@router.post("/scrape/start", tags=["scrape"])
async def start_scrape(postcode: str|None = None, deleteold: bool=False, regions: int = 1, lat: str | None = None, lon: str | None = None , limit = 0, scraper: Scraper= Depends(get_scraper)):
	try:
		await scraper.get(postcode, deleteold, regions, lat, lon, limit)
	except Exception as err:
		raise HTTPException(status_code=400, detail=json.dumps(err.__repr__))
	return JSONResponse(content = json.dumps({"status": "OK"}), status_code=status.HTTP_201_CREATED)

@router.get("/scrape/restaurant_count", tags=["scrape"])
async def get_restaurant_count(database: DbWrapper= Depends(get_db)):
	try:
		result = database.count(Restaurant)
	except Exception as err:
		raise HTTPException(status_code=400, detail=err.__repr__)
	return JSONResponse(content = json.dumps({"count": result}), status_code=status.HTTP_201_CREATED)
