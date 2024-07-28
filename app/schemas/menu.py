from pydantic import BaseModel

from uuid import UUID

class Menu(BaseModel):
	id: int
	restaurant_id: str
	name: int
	category: str
	price: str

