#!/usr/bin/env python3
"""
Created on Wed Mar 28 11:28:47 2018

@author: base
"""

from sqlalchemy import Column, ForeignKey, Integer, String, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


# Define user class
class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250))


# Define category class
class Categories(Base):
    __tablename__ = 'categories'
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    # Set up relationship to the user class
    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    # Define property for JSON export
    @property
    def serialize(self):
        """Return category and item data in easily serializeable format"""
        items = session.query(Item).filter_by(cat_id=self.id).all()

        return {
            'name': self.name,
            'id': self.id,
            'items': [i.serialize for i in items]
        }


# Define item class
class Item(Base):
    __tablename__ = 'item'
    name = Column(String(80), nullable=False)
    id = Column(Integer, primary_key=True)
    cat_id = Column(Integer, ForeignKey('categories.id'))
    description = Column(String(250))
    time_updated = Column(TIMESTAMP)
    user_id = Column(Integer, ForeignKey('user.id'))
    # Define relationships to category and user classes
    category = relationship(Categories)
    user = relationship(User)

    @property
    def serialize(self):
        """Return item data in easily serializeable format"""
        return {
            'name': self.name,
            'description': self.description.replace("                         ", " "),
            'id': self.id,
            'category_id': self.cat_id,
            'last_update': self.time_updated,
            'user_id': self.user_id
        }


# Initialize db engine
engine = create_engine('sqlite:///catalogue.db')
Base.metadata.create_all(engine)

DBSession = sessionmaker(bind=engine)
session = DBSession()
