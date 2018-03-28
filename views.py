# -*- coding: utf-8 -*-
"""
Created on Wed Mar 28 11:26:14 2018

@author: base
"""

from flask import Flask, render_template, request, redirect,jsonify, url_for, flash
app = Flask(__name__)

from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Restaurant, MenuItem, User

#new imports
from flask import session as login_session
import random, string

# OAUTH imports
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
from flask import make_response
import requests

CLIENT_ID = json.loads(
        open('client_secrets.json', 'r').read())['web']['client_id']


#Connect to Database and create database session
engine = create_engine('sqlite:///item_catalogue.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

