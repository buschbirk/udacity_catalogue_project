# -*- coding: utf-8 -*-
"""
Created on Wed Mar 28 11:26:14 2018

@author: base
"""

from flask import Flask, render_template, request, redirect,jsonify, url_for, flash
app = Flask(__name__)

from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from create_database import Base, Categories, Item, User

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
from datetime import datetime as dt


CLIENT_ID = json.loads(
        open('client_secrets.json', 'r').read())['web']['client_id']


#Connect to Database and create database session
engine = create_engine('sqlite:///item_catalogue.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/')
@app.route('/catalog')
def frontPage():
    
    categories = session.query(Categories).all()
    items = session.query(Item).order_by("time_updated DESC").limit(len(categories))
    
    if 'access_token' in login_session:
        flash("You are logged in as: " +login_session['username'])
        return render_template('frontpageuser.html', 
                               categories = categories,
                               latest_items = items,
                               getCatName=lambda x: getCatName(x))
    else:
        return render_template('frontpage.html', 
                               categories = categories, 
                               latest_items = items,
                               getCatName=lambda x: getCatName(x),
                               session = login_session)


@app.route('/catalog/<category>/items')
def itemsPage(category):
    
    all_categories = session.query(Categories).all()
    cat = session.query(Categories).filter_by(name = category.replace("-", " ")).first()
    items = session.query(Item).filter_by(cat_id = cat.id).all()
    
    if 'access_token' in login_session:
        return render_template('itemspageuser.html',
                               categories = all_categories,
                               items = items,
                               category = cat,
                               len_items = str(len(items)))
    else:
        return render_template('itemspage.html',
                               categories = all_categories,
                               items = items,
                               category = cat,
                               len_items = str(len(items)))
        #return render_template('itemspage.html')




@app.route('/catalog/<category>/items/add', methods=['GET', 'POST'])
def addItem(category):
    
    if request.method == 'GET':
        
        if 'access_token' in login_session:
            categories = session.query(Categories).all()
            return render_template('addItem.html',
                                   categories = categories,
                                   category_name = category)
        elif category == 'none':
            flash("Please log in to add and edit items")
            return redirect(url_for('frontPage'))
        else:
            flash("Please log in to add and edit items")
            return redirect(url_for('itemsPage', category = category))
    
    if request.method == 'POST':
        if not request.form['name']:
            flash("Please fill out the name field")
            return redirect(url_for('itemsPage', category = category))
        else:
            name = request.form['name']
            description = request.form['description']
            cat_id = request.form['category']
            print("Category name is " +cat_id)
            cat_ = session.query(Categories).filter_by(id = cat_id).one()
            timestamp = dt.now()
            user = getUserInfo(login_session['user_id'])
            
            new_item = Item(name = name, 
                            description = description,
                            time_updated = timestamp,
                            user = user,
                            category = cat_)
            
            session.add(new_item)
            session.commit()
            flash("Successfully added item: " +new_item.name)
            
            return redirect(url_for('frontPage'))
            

        
        
        
@app.route('/catalog/<category>/<item_name>/')
def itemPage(category, item_name):
    
    cat = session.query(Categories).filter_by(name = category.replace("-"," ")).first()
    item = session.query(Item).filter_by(name = item_name.replace("-", " "), 
                                         cat_id = cat.id).first()
    
    if 'access_token' in login_session:
        return render_template('itempageuser.html',
                               item = item,
                               category = category)
    else:
        return render_template('itempage.html',
                               item = item)


@app.route('/catalog/<category>/<item_name>/edit', methods=['GET', 'POST'])
def editItem(category, item_name):
    
    cat = session.query(Categories).filter_by(name = category.replace("-", " ")).one()
    item = session.query(Item).filter_by(name = item_name.replace("-", " "), cat_id = cat.id).one()
    
    if request.method == 'GET':        
        if 'access_token' in login_session:
            categories = session.query(Categories).all()
            return render_template('editItem.html',
                                   categories = categories,
                                   item = item)
        else:
            flash("Please log in to add and edit items")
            return redirect(url_for('itemsPage', category = category))
        
    elif request.method == 'POST':
        if request.form['name']:
            item.name = request.form['name']
        if request.form['description']:
            item.description = request.form['description']
        if request.form['category']:
            item.cat_id = int(request.form['category'])
        
        item.time_updated = dt.now()
        session.add(item)
        session.commit()
        
        return redirect(url_for('itemPage', 
                                category = category, 
                                item_name = item_name))


@app.route('/catalog/<category>/<item_name>/delete', methods=['GET', 'POST'])
def deleteItem(category, item_name):
    
    cat = session.query(Categories).filter_by(name = category.replace("-", " ")).one()
    item = session.query(Item).filter_by(name = item_name.replace("-", " "), cat_id = cat.id).one()    
    
    if request.method == 'GET':        
        return render_template('deleteitem.html',
                               category = category,
                               item_name = item_name)
    elif request.method == 'POST':        

        session.delete(item)
        session.commit()
        flash("Successfully deleted item: " +item.name)
        
        return redirect(url_for('itemsPage', 
                                category = category,))


@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) \
                    for x in range(32))
    login_session['state'] = state
    
    return render_template('login.html', STATE = state)      


@app.route('/logout')
def logout():
    if 'access_token' in login_session:
        access_token = login_session['access_token']
        
        url = 'https://accounts.google.com/o/oauth2/revoke'
        
        r = requests.post(url, params={'token': access_token},
                          headers = {'content-type': 'application/x-www-form-urlencoded'})
        
        if r.status_code == 200:
            # Reset the user's session
            del login_session['access_token']
            del login_session['username']
            del login_session['email']
            del login_session['user_id']
            flash("You have been successfully logged out")
            return redirect(url_for('frontPage'))
        else:
            flash("It looks like you were not logged in")
            print("Unsuccessful login. Status code: " +str(r.status_code))
            print("response content: " + r.content)
            return redirect(url_for('frontPage'))            
        
        
@app.route('/gconnect', methods=['POST'])
def gconnect():
    # VAlidate state token

    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    
    code = request.data
    
    try:
        # Upgrade authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(json.dumps('Failed to upgrade the authorization\
                                            code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    
    # Check that access token is valid
    access_token = credentials.access_token
    print(str(access_token))

    url = ('https://www.googleapis.com/oauth2/v3/tokeninfo?' +
           "access_token=%s" % access_token)
    
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])

    print(result)
    
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:

        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response
    

    
    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    print(gplus_id)
    
    if result['sub'] != gplus_id:
        response = make_response(
                json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        print("Token's client ID does not match app's.")
        return response
    
    # Verify that the access token is valid for this app.
    if result['aud'] != CLIENT_ID:
        response = make_response(
                json.dumps("Token's client ID does not match app's"), 401)
        print("Token's client ID does not match app's.")
        response.headers['Content-Type'] = 'application/json'
        return response
    
    # Check to see if user is already logged in
    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('Current user is already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    
    #Store the access token in the session for later use
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id
    
    #get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    
    data = answer.json()
    
    login_session['username'] = data['name']
    login_session['email'] = data['email']
    
    login_session['user_id'] = getUserId(login_session['email'])
    if not login_session['user_id']:
        login_session['user_id'] = createUser(login_session)
    
    
    flash("you are now logged in as %s" % login_session['username'])
    print("Finished Oauth flow")
    
    return redirect(url_for('frontPage'))


@app.context_processor
# inject login_session to header for all templates
def inject_session():
    return dict(session=login_session)



def createUser(login_session):
    newUser = User(name = login_session['username'], 
                   email = login_session['email'])
    
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email = login_session['email']).one()
    
    return user.id

def getUserInfo(user_id):
    user = session.query(User).filter_by(id = user_id).one()
    return user

def getUserId(email):
    try:
        user = session.query(User).filter_by(email = email).one()
        return user.id
    except:
        return None

def getCatName(catId):
    category = session.query(Categories).filter_by(id = catId).one()
    return category.name



if __name__ == '__main__':
  app.secret_key = 'super_secret_key'
  app.debug = True
  app.run(host = '0.0.0.0', port = 5000)

#DISCONNECT current session. Revoke a users token and reset login session
#@app.route('/gdisconnect')
#def gdisconnect():
#    access_token = login_session.get('access_token')
#    if access_token is None:
#        response = make_response(json.dumps('Current user not connected.'), 401)
#        response.headers['Content-Type'] = 'application/json'
#        return response
#    
#    url = 'https://accounts.google.com/o/oauth2/revoke'
#    
#    result = requests.post(url, params={'token': access_token},
#                           headers = {'content-type': 
#                                      'application/x-www-form-urlencoded'})
#  
#    
#    if result.status_code == '200':
#        # Reset the user's session
#        del login_session['credentials']
#        del login_session['gplus_id']
#        del login_session['username']
#        del login_session['email']
#        del login_session['picture']
#        
#        response = make_response(json.dumps('Successfully disconnected.'), 200)
#        response.headers['Content-Type'] = 'application/json'
#        return response
#    else:
#        response = make_response(json.dumps('Failed to revoke token for \
#                                            given user.'), 400)
#        response.headers['Content-Type'] = 'application/json'
#        return response