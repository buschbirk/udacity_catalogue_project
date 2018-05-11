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

# Add categories
soccer = category(name="Soccer", user = user1)
basketball = category(name="Basketball", user = user1)
snowboarding = category(name="Snowboarding", user = user1)
skating = category(name="Skating", user = user1)
hockey = category(name="Hockey", user = user1)

session.add_all([soccer, basketball, snowboarding, skating, hockey])
session.commit()

# Add soccer items
soccer_ball = Item(name="Soccer ball", 
            description="An ideal ball for players taking their first steps \
                        onto the pitch, the Soccer Ball is a solid, durable \
                        go-to that handles the rigors of tough shooting and \
                        skill drills while celebrating the sport's iconic \
                        tournament.",
            time_updated = dt.now(),
            category=soccer,
            user = user1)
goalie_shoes = Item(name="Goalkeeper Gloves", 
            description="Equipped with a smooth latex foam palm, the Nike \
                        Adult Match Goalkeeper Soccer Goalie Gloves offer \
                        reliable impact protection and consistent grip so \
                        you can block the hardest shots in any weather \
                        conditions.",
            time_updated = dt.now(),
            category=soccer,
            user = user1)

session.add_all([soccer_ball, goalie_shoes])
session.commit()

# Add basketball items
basket_ball = Item(name="A pretty good basketball", 
            description="An all-in-one package that includes an easy-to-use \
                        air pump to maintain the perfect inflation",
            time_updated = dt.now(),
            category=basketball,
            user = user1)
hoop = Item(name="Very fragile basketball hoop", 
            description="Don't dunk on this one. It is going to break",
            time_updated = dt.now(),
            category=basketball,
            user = user1)

session.add_all([basket_ball, hoop])
session.commit()

# Add snowboarding items
snowboard = Item(name="Concrete snowboard", 
            description="An excessively heavy snowboard. Easy to stand on, \
                        not very useful in any other situation",
            time_updated = dt.now(),
            category=snowboarding,
            user = user1)
gopro = Item(name="GoPro camera", 
            description="Because it didn't happen if you don't have the video.\
                        All your friends LOVE to watch the tip of your snowboard\
                        for three hours"
            time_updated = dt.now(),
            category=snowboarding,
            user = user1)

session.add_all([snowboard, gopro])
session.commit()

# Add skating items
skates = Item(name="Ice skates", 
            description="Extremely sharp. Use them as skates or a perfectly \
                        good murder weapon",
            time_updated = dt.now(),
            category=skating,
            user = user1)
bandaid = Item(name="Band-aid", 
            description="Nice to have when you cut yourself of your skates"
            time_updated = dt.now(),
            category=skating,
            user = user1)

session.add_all([skates, bandaid])
session.commit()

# Add Hockey items
hockey_stick = Item(name="Hockey stick", 
            description="Perfect for pushing around a puck and fighting.",
            time_updated = dt.now(),
            category=hockey,
            user = user1)

puck = Item(name="Hockey Puck", 
             description="It's a puck. No further explanation needed",
             time_updated = dt.now(),
             category=hockey,
             user = user1)

session.add_all([hockey_stick, puck])
session.commit()

print("Sample data succesfully added to database")