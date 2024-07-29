import os
import time
import json
import asyncio
import cloudscraper
import uuid

from cloudscraper import CloudScraper
from asyncio import Semaphore
from typing import Tuple
from bs4 import BeautifulSoup

from ..utils.apiwrapper import ApiWrapper
from ..utils.headers import generate_header

from ..database.models.restaurant import Restaurant
from ..database.models.menu import Menu
from ..database.engine import DbWrapper
from ..utils.apiwrapper import ApiWrapper


class Scraper(object):

	API_ENDPOINT = "https://cw-api.takeaway.com/api/v34"
	MAIN_URL = "https://www.thuisbezorgd.nl"


	_api_wrapper: ApiWrapper | None = None
	_database_wrapper: DbWrapper | None = None
	_cloud_wrapper: CloudScraper | None = None
	_semaphore = Semaphore = asyncio.Semaphore(10)


	def __init__(self, database_wrapper: DbWrapper, concurrent_scrapers = None):
		self._database_wrapper = database_wrapper
		self._cloud_scraper = cloudscraper.create_scraper(interpreter='nodejs', delay=1, browser={"browser": "chrome"})
		if concurrent_scrapers is not None:
			self._semaphore = asyncio.Semaphore(concurrent_scrapers)


	async def geo_locate(self, address: str) -> dict:
		'''
			Return locations to pass to the get restaurants api 
		'''	
		try:
			addresses = (await self._api_wrapper.get(f"location/geocoder?addressString={address}"))["addresses"]
			return addresses[0]["lat"], addresses[0]["lng"], addresses[0]["deliveryAreaId"], addresses[0]["takeawayPostalCode"]
		except:
			pass


	async def get_restaurants(self, deliveryAreaId: str, postal_code: str, lat: str, lng: str, limit: int) -> dict:
		'''
			Return the restaurants 
		'''	
		return await self._api_wrapper.get(f"restaurants?deliveryAreaId={deliveryAreaId}&postalCode={postal_code}&lat={lat}&lng={lng}&limit={limit}&isAccurate=True&filterShowTestRestaurants=False")

	async def get_restaurant(self, restaurant_slug: str) -> dict:
		'''
			Return information per restaurant by restaurants slug name
		'''	
		return await self._api_wrapper.get(f"restaurant?slug={restaurant_slug}")


	async def get_menu(self, menu: dict) -> dict:
		'''
			Create generator to iterate on the menu	
		'''	
		for item in menu["menu"]["products"]:
			yield menu["menu"]["products"][item]


	async def extract_load(self, obj: dict):
		'''
			Communicate with the database
			Insert on conflict update restaurant and menu tables.	
		'''	
		async with self._semaphore:
			resto = await self.get_restaurant(obj['primarySlug'])
			self._database_wrapper.upsert(Restaurant, 
															id = obj["id"], 
															primarySlug = obj["primarySlug"],
															name = obj["brand"]["name"],
															location = json.dumps(resto["location"]),
															logoUrl = obj["brand"]["logoUrl"],
															priceRange = obj["priceRange"],
															times = json.dumps(resto["delivery"]["times"]),
															rating = obj["rating"]["score"], 
															number_of_ratings = obj["rating"]["votes"], 
															shippingInfo = json.dumps(obj["shippingInfo"]),
															cuisineTypes = json.dumps(obj["cuisineTypes"]))
			async for item in self.get_menu(resto):
				self._database_wrapper.upsert(Menu, id = str(uuid.uuid4()),
										restaurant_id = obj["id"], 
										item_name = item["name"],
										item_category = item["variants"][0]["id"],
										item_price = item["variants"][0]["prices"]["delivery"] / resto["menu"]["currency"]["denominator"]
				)

	async def get(self, postcode: str|None = None, deleteold: bool=False, regions: int = 1, lat: str | None = None, lon: str | None = None, limit = 0):
		'''
			A main scraper logic
		'''	
		if deleteold:
			self._database_wrapper.delete_objects()
			self._database_wrapper.create_objects()
		self._api_wrapper = await ApiWrapper.create(url=self.API_ENDPOINT, headers=generate_header(), trace=False)

		# We retrieve pages for amsterdam from the html	and retrive geo location information
		postal_codes = []
		if postcode is not None and postcode != "":
			postal_codes.append(postcode)
		else:
			soup = BeautifulSoup(self._cloud_scraper.get("/".join([self.MAIN_URL, "eten-bestellen-amsterdam"])).text, features="html.parser")
			postal_codes = list(set([await self.geo_locate(s.find('a')['href'].split("/")[-1].replace("-", "+")) for s in soup.findAll("div", {"class": "delarea"})]))[:regions]

		# Iterate through the postal codes in Amsterdam and then dispatch async tasks to get 
		# restaurants per area.
		for post_code in list(set(postal_codes)):
			print(f"Getting area {post_code}")
			futures = []
			obj = await self.get_restaurants(post_code[2], post_code[3], post_code[0], post_code[1], limit)
			[futures.append(self.extract_load(obj["restaurants"][restaurant])) for restaurant in obj["restaurants"]]
			await asyncio.gather(*futures)	
