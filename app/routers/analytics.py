import json 

from urllib.parse import unquote
from typing import Annotated

from ..database.models.restaurant import Restaurant
from ..database.models.menu import Menu

from fastapi import status, APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from ..database.engine import DbWrapper

router = APIRouter()

#async def main():
def get_db():
	db = DbWrapper().connect(reinitialize_objects = False)
	try:
		yield db
	finally:
		db.close()

@router.get("/data/best_cuisines", tags=["data"])
async def get_cuisines(database: DbWrapper= Depends(get_db)):
	'''
	We hold the cuisines as array in the db so, firstly we unnest them. Then, group by by the cuisine types to run avg aggregate 
	via using number of voters and rating.
	select distinct(unnest(string_to_array(regexp_replace(replace(replace("cuisineTypes",'[', ''), ']', ''), '^\s+|\s+$', ''), ','))) as ctype, 
	sum(r.rating::float * r.number_of_ratings::int) / (sum(r.number_of_ratings::int)) as avg_ratings 
	from restaurant r where number_of_ratings::int > 500 
	group by ctype order by avg_ratings DESC limit 5;
	'''
	try:
		res = []
		for r in database.execute_raw("""select distinct(unnest(string_to_array(regexp_replace(replace(replace("cuisineTypes",'[', ''), ']', ''), '^\s+|\s+$', ''), ','))) as ctype, sum(r.rating::float * r.number_of_ratings::int) / (sum(r.number_of_ratings::int)) as avg_ratings from restaurant r where number_of_ratings::int > 500 group by ctype order by avg_ratings DESC limit 5;"""):
			res.append({"cuisine": str(r[0]), "rating": str(r[1])})
		return JSONResponse(content = json.dumps({"result": res}), status_code=status.HTTP_200_OK)
	except Exception as err:
		raise HTTPException(status_code=400, detail=err.__repr__)

@router.get("/data/expensive_best_cuisine", tags=["data"])
async def get_expensive_cuisine(database: DbWrapper= Depends(get_db)):
	'''
	The same query as above, but also includes prices and orders by it.

	select distinct(unnest(string_to_array(regexp_replace(replace(replace("cuisineTypes",'[', ''), ']', ''), '^\s+|\s+$', ''), ','))) as ctype, 
	sum(r.rating::float * r.number_of_ratings::int) / (sum(r.number_of_ratings::int)) as avg_ratings, 
	avg("priceRange") / 100 as price 
	from restaurant r 
	where number_of_ratings::int > 500 
	group by ctype 
	order by price desc, avg_ratings DESC limit 1;
	'''
	try:
		res = []
		for r in database.execute_raw("""select distinct(unnest(string_to_array(regexp_replace(replace(replace("cuisineTypes",'[', ''), ']', ''), '^\s+|\s+$', ''), ','))) as ctype, sum(r.rating::float * r.number_of_ratings::int) / (sum(r.number_of_ratings::int)) as avg_ratings, avg("priceRange") / 100 as price from restaurant r where number_of_ratings::int > 500 group by ctype order by price desc, avg_ratings DESC limit 1;"""):
			res.append({"cuisine": str(r[0]), "rating": str(r[1]), "price": str(r[2])})
		return JSONResponse(content = json.dumps({"result": res}), status_code=status.HTTP_200_OK)
	except Exception as err:
		raise HTTPException(status_code=400, detail=err.__repr__)

@router.get("/data/search", tags=["data"])
async def get_expensive_cuisine(item: str, postal_code: str, time_t: str, database: DbWrapper= Depends(get_db)):
	'''
	We use location field which we use to retrive the postal code to match with the location we sent, which can be anywhere. 
	Then, we search for the product in the database and return the cheapest item.
	We also run query to check if the place that we have found is open, we use times column for it. The time is encoded as (hour)*60+minutes.

	select 	jsonb_build_object('id', r_id, 'name', r_name,'price', price, 'postalCode', postalCode)
	from (
		select distinct(r.id) as r_id,
				name as r_name, 
				item_price as price, 
				r."location"::jsonb->>'postalCode' as postalCode, 
				(jsonb_array_elements((r.times::jsonb->>'0')::jsonb)->>'start')::int as s_time,
				(jsonb_array_elements((r.times::jsonb->>'0')::jsonb)->> 'end')::int as e_time
		from menu 
		inner join restaurant r on r.id = menu.restaurant_id 
		where item_name like '%Coca-Cola 33%' or item_name like '%Coca Cola 33%'
	) as _c 
	where _c.postalCode like '%101%' and s_time < 1290 and e_time > 1290 order by price asc limit 1;
	'''
	try:
		res = []
		cmd = """select jsonb_build_object('id', r_id, 'name', r_name,'price', price, 'postalCode', postalCode)
from (
	select distinct(r.id) as r_id,
			name as r_name, 
			item_price as price, 
			r."location"::jsonb->>'postalCode' as postalCode, 
			(jsonb_array_elements((r.times::jsonb->>'0')::jsonb)->>'start')::int as s_time,
			(jsonb_array_elements((r.times::jsonb->>'0')::jsonb)->> 'end')::int as e_time
	from menu 
	inner join restaurant r on r.id = menu.restaurant_id 
	where item_name like '%{item}%'
) as _c 
where _c.postalCode like '%{postal_code}%' and s_time < {time_t} and e_time > {time_t} order by price asc limit 1;""".format(item = unquote(item), postal_code = postal_code[:-1], time_t = int(time_t.split(":")[0]) * 60 + int(time_t.split(":")[1]))
		result = None
		print(cmd)
		for res in database.execute_raw(cmd):
			result = res[0]
			print(res)
		return JSONResponse(content = json.dumps({"result": result}), status_code=status.HTTP_200_OK)
	except Exception as err:
		raise HTTPException(status_code=400, detail=err.__repr__)