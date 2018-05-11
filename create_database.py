# -*- coding: utf-8 -*-
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

class User(Base):
    __tablename__ = 'user'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250))


class Categories(Base):
    __tablename__ = 'categories'
   
    id = Column(Integer, primary_key=True)
    name = Column(String(250), nullable=False)

    user_id = Column(Integer, ForeignKey('user.id'))
    user = relationship(User)

    @property
    def serialize(self):
       """Return object data in easily serializeable format"""
       items = session.query(Item).filter_by(cat_id = self.id).all()
       
       return {
           'name'         : self.name,
           'id'           : self.id,
           'items'        : [i.serialize for i in items]
       }
 
class Item(Base):
    __tablename__ = 'item'


    name =Column(String(80), nullable = False)
    id = Column(Integer, primary_key = True)
    cat_id =  Column(Integer, ForeignKey('categories.id'))
    # cat_name = Column(Integer, ForeignKey('categories.name'))
    description = Column(String(250))
    time_updated = Column(TIMESTAMP)
    user_id = Column(Integer, ForeignKey('user.id'))    
    category = relationship(Categories)
    user = relationship(User)

    @property
    def serialize(self):
       """Return object data in easily serializeable format"""
       return {
           'name'         : self.name,
           'description'  : self.description,
           'id'           : self.id,
           'category_id'  : self.cat_id,
           'last_update'  : self.time_updated,
           'user_id'      : self.user_id
       }



    
    
engine = create_engine('sqlite:///catalogue.db')
 

Base.metadata.create_all(engine)

DBSession = sessionmaker(bind=engine)
session = DBSession()
