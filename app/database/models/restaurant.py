from sqlalchemy import UUID, Double, ARRAY, Integer, String, Column, create_engine, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import relationship, joinedload, subqueryload, Session
from .. import Base

from typing import Tuple


class Restaurant(Base):
	__tablename__ = 'restaurant'
	id = Column(String, primary_key=True)
	primarySlug = Column(String)
	name = Column(String)
	location = Column(String)
	logoUrl = Column(String)
	priceRange = Column(Integer)
	rating = Column(Double)
	times = Column(String)
	number_of_ratings = Column(Integer)
	shippingInfo = Column(String)
	cuisineTypes = Column(String)
	menu = relationship("Menu", backref="restaurant", cascade="all, delete", passive_deletes=True)
	
	def __repr__(self) -> str:
		return f"<TableName(id='{self.id}', name='{self.name}')>"