from sqlalchemy import UUID, Double, ARRAY, Integer, String, Column, create_engine, ForeignKey, PrimaryKeyConstraint
from sqlalchemy.orm import relationship, joinedload, subqueryload, Session
from .. import Base
import uuid
from uuid import UUID


class Menu(Base):
	__tablename__ = 'menu'
	id = Column(String, primary_key=True, default=uuid.uuid4)
	restaurant_id = Column(String, ForeignKey('restaurant.id'))
	item_name = Column(String)
	item_category = Column(String)
	item_price = Column(Double)
