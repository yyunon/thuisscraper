import os
from typing import TypeVar

from sqlalchemy import create_engine
from sqlalchemy import select, func, Integer, Table, Column, MetaData, text

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.engine import Engine

from . import Base
from .models.restaurant import Restaurant
from .models.menu import Menu

from sqlalchemy.dialects.postgresql import insert

class DbWrapper(object):
	_engine: Engine | None = None

	_session: Session | None = None

	_T = TypeVar('_T', Restaurant, Menu)

	def connect(self, reinitialize_objects: bool = False) -> 'DbWrapper':
		self._engine = create_engine(os.environ["postgres_conn"])

		self._connection = self._engine.connect()
		
		self._session = sessionmaker(bind=self._engine)()

		if reinitialize_objects:
			self.delete_objects()

			self.create_objects()

		return self
	

	def delete_objects(self):
		Base.metadata.drop_all(self._engine)


	def create_objects(self):
		Base.metadata.create_all(self._engine)


	def get(self, types: _T):
		return self._session.query(types).all()


	def count(self, table: Restaurant | Menu):
		try:
			count_query = (self._session.query(func.count(table.id)))
			res = self._session.execute(count_query).scalar()
			return res
		except SQLAlchemyError as err:
			raise Exception(err.__repr__)

	def execute_raw(self, query: str):
		for r in self._session.execute(text(query)).fetchall():
			yield r


	def insert(self, item: Restaurant | Menu):
		self._session.add(item)
		self._session.commit()
		self._session.refresh(item)

	def upsert(self, table: Restaurant | Menu, **kwargs):
		stmt = insert(table).values(**kwargs)
		if isinstance(table(), Restaurant):
			stmt = stmt.on_conflict_do_update(
					index_elements= ["id"],
					set_=dict(location=stmt.excluded.location,
							 			logoUrl =stmt.excluded.logoUrl,
										priceRange = stmt.excluded.priceRange,
										rating = stmt.excluded.rating,
										number_of_ratings = stmt.excluded.number_of_ratings,
										shippingInfo = stmt.excluded.shippingInfo,
										cuisineTypes = stmt.excluded.cuisineTypes,
										)
			)
		elif isinstance(table(), Menu):
			stmt = stmt.on_conflict_do_update(
					index_elements= ["id"],
					set_=dict(item_name=stmt.excluded.item_name,
										item_category=stmt.excluded.item_category,
										item_price=stmt.excluded.item_price,
										)
			)
		self._session.execute(stmt)		
		self._session.commit()



	def delete_from_table(self, table: Restaurant | Menu, by: str):
		table.delete().where(table.id == by).execute()

	
	def close(self):
		self._connection.close()

