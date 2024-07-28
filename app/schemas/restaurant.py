from pydantic import BaseModel

from uuid import UUID

class Restaurant(BaseModel):
	name : str
	address : str
	logo : str
	price : str
	rating : str
	duration : int
	category : str
	minOrderValue : str
	delivery_area : list[str]
