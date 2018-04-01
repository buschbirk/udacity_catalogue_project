# -*- coding: utf-8 -*-
"""
Created on Tue Mar 13 21:07:32 2018

@author: base
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime as dt
from create_database import Categories as category, Base, Item, User

engine = create_engine('sqlite:///item_catalogue.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine



DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

# Create a user
user1 = User(name = 'lasse', email = 'lasse@alsbirk.com')
session.add(user1)
session.commit()


# Menu for UrbanBurger
category1 = category(name="Urban Burger", user = user1)

session.add(category1)
session.commit()

Item1 = Item(name="Veggie Burger", 
             description="Juicy grilled veggie patty with tomato mayo and lettuce",
             time_updated = dt.now(),
             category=category1,
             user = user1)

session.add(Item1)
session.commit()


# Menu for Super Stir Fry
category2 = category(name="Super Stir Fry", user = user1)

session.add(category2)
session.commit()

Item2 = Item(name="Veggie Burger", 
             description="Juicy grilled veggie patty with tomato mayo and lettuce",
             time_updated = dt.now(),
             category=category2, 
             user = user1)

session.add(Item2)
session.commit()


# Menu for Panda Garden
category3 = category(name="Panda Garden", user = user1)

session.add(category3)
session.commit()

Item3 = Item(name="Veggie Burger", 
             description="Juicy grilled veggie patty with tomato mayo and lettuce",
             time_updated = dt.now(),
             category=category3, 
             user = user1)

session.add(Item3)
session.commit()

# Menu for Tony's Bistro
category4 = category(name="Tony\'s Bistro ", user = user1)

session.add(category4)
session.commit()

Item4 = Item(name="Veggie Burger", 
             description="Juicy grilled veggie patty with tomato mayo and lettuce",
             time_updated = dt.now(),
             category=category4, 
             user = user1)

session.add(Item4)
session.commit()


# Menu for Andala's
category5 = category(name="Andala\'s", user = user1)

session.add(category5)
session.commit()

Item5 = Item(name="Veggie Burger", 
             description="Juicy grilled veggie patty with tomato mayo and lettuce",
             time_updated = dt.now(),
             category=category5, 
             user = user1)

session.add(Item5)
session.commit()


# Menu for Auntie Ann's
category6 = category(name="Auntie Ann\'s Diner ", user = user1)

session.add(category6)
session.commit()

Item6 = Item(name="Veggie Burger", 
             description="Juicy grilled veggie patty with tomato mayo and lettuce",
             time_updated = dt.now(),
             category=category6, 
             user = user1)

session.add(Item6)
session.commit()


print("added menu items!")
