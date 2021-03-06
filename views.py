#!/usr/bin/env python3
"""
Created on Wed Mar 28 11:26:14 2018

@author: base
"""

from flask import Flask, render_template, request, redirect, jsonify, url_for
from flask import flash, make_response
from flask import session as login_session
from functools import wraps

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from create_database import Base, Categories, Item, User

import random
import string
import requests
import json
from datetime import datetime as dt

# OAUTH imports for Google authentication
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2

# Initialize Flask app
app = Flask(__name__)
CLIENT_ID = json.loads(open('client_secrets.json', 'r')
                       .read())['web']['client_id']

# Connect to database and create db session
engine = create_engine('postgresql://catalog:catalogPass@localhost:5432/itemcatalog')
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create a decorator for pages with required login
def login_required(function):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if 'access_token' in login_session:
            return function(*args, **kwargs)
        else:
            flash('A user must be logged to add a new item.')
            return redirect(url_for('frontPage'))
    return wrapper


@app.route('/')
@app.route('/catalog/')
def frontPage():
    """ Renders the front page """
    categories = session.query(Categories).all()
    items = session.query(Item).order_by(
            "time_updated DESC").limit(len(categories))

    # Check if user is logged in and serve appropriate html page
    if 'access_token' in login_session:
        return render_template('frontpageuser.html',
                               categories=categories,
                               latest_items=items,
                               getCatName=lambda x: getCatName(x))
    else:
        return render_template('frontpage.html',
                               categories=categories,
                               latest_items=items,
                               getCatName=lambda x: getCatName(x),
                               session=login_session)


@app.route('/catalog/auth_completed/')
def authFinished():
    """ Flashes login message and redirects to front page """

    flash("You are logged in as: " + login_session['username'])
    return redirect(url_for('frontPage'))


@app.route('/catalog.json/')
def catalogJson():
    """ Export JSON data for all categories """

    categories = session.query(Categories).all()
    return jsonify(Categories=[i.serialize for i in categories])


@app.route('/catalog/<category>/items/')
def itemsPage(category):
    """ Serves the page for a category """

    all_categories = session.query(Categories).all()
    cat = session.query(Categories).filter_by(
          name=category.replace("-", " ")).one()
    items = session.query(Item).filter_by(cat_id=cat.id).all()

    if 'access_token' in login_session:
        return render_template('itemspageuser.html',
                               categories=all_categories,
                               items=items,
                               category=cat,
                               len_items=str(len(items)),
                               user_id=login_session['user_id'])
    else:
        return render_template('itemspage.html',
                               categories=all_categories,
                               items=items,
                               category=cat,
                               len_items=str(len(items)))


@app.route('/catalog/<category>/items.json/')
def categoryJson(category):
    """ Export JSON for a single category """

    cat = session.query(Categories).filter_by(
          name=category.replace("-", " ")).one()
    return jsonify(cat.serialize)


@app.route('/catalog/category/add/', methods=['GET', 'POST'])
@login_required
def addCategory():
    """ Handles requests for adding a category """

    if request.method == 'GET':
        return render_template('addcategory.html')

    if request.method == 'POST':
        if request.form['name']:
            user = getUserInfo(login_session['user_id'])
            new_cat = Categories(name=request.form['name'],
                                 user=user)
            session.add(new_cat)
            session.commit()
            flash("New category added: " + new_cat.name)
            return redirect(url_for('frontPage'))
        else:
            flash("The 'name' field is required")
            return redirect(url_for('addCategory'))


@app.route('/catalog/<category>/edit/', methods=['GET', 'POST'])
@login_required
def editCategory(category):
    """ Handles requests for editing a category """

    cat = session.query(Categories).filter_by(
          name=category.replace("-", " ")).one()

    if request.method == 'GET':
        if login_session['user_id'] == cat.user_id:
            return render_template('editcategory.html',
                                   category=cat)
        else:
            flash("You are not the author of this category")
            return redirect(url_for('frontPage'))

    if request.method == 'POST':
        if request.form['name']:
            cat.name = request.form['name']
            session.add(cat)
            session.commit()
            flash("Category edit finished for: " + cat.name)
            return redirect(url_for('frontPage'))
        else:
            flash("The name field is required")
            return redirect(url_for('editCategory', category=category))


@app.route('/catalog/<category>/delete/', methods=['GET', 'POST'])
@login_required
def deleteCategory(category):
    """ Handles requests for deleting a category """

    cat = session.query(Categories).filter_by(
          name=category.replace("-", " ")).one()

    if request.method == 'GET':
        if login_session['user_id'] == cat.user_id:
            return render_template('deletecategory.html',
                                   category=cat)
        else:
            flash("You are not the author of this category")
            return redirect(url_for('itemsPage', category=category))
    if request.method == 'POST':
        items = session.query(Item).filter_by(cat_id=cat.id).all()
        for item in items:
            session.delete(item)

        session.delete(cat)
        session.commit()
        return redirect(url_for('frontPage'))


@app.route('/catalog/<category>/items/<item_name>/')
def itemPage(category, item_name):
    """ Serves the page for an item or exports JSON if requested """

    cat = session.query(Categories).filter_by(
          name=category.replace("-", " ")).one()
    item = session.query(Item).filter_by(name=item_name.replace("-", " "),
                                         cat_id=cat.id).first()

    if item_name.endswith('.json'):
        item = session.query(Item).filter_by(name=item_name.split(".")[0]
                                             .replace("-", " "),
                                             cat_id=cat.id).first()
        return jsonify(item.serialize)
    elif 'access_token' in login_session\
            and login_session['user_id'] == cat.user_id:
        return render_template('itempageuser.html',
                               item=item,
                               category=category)
    else:
        return render_template('itempage.html',
                               item=item)


@app.route('/catalog/<category>/items/add/', methods=['GET', 'POST'])
@login_required
def addItem(category):
    """ Handles requests for adding an item """

    user_categories = session.query(Categories).filter_by(
                      user_id=login_session['user_id']).all()

    if request.method == 'GET':
        if len(user_categories) == 0:
            flash('You need to be the author of a category to add items')
            if category == 'none':
                return redirect(url_for('frontPage'))
            else:
                return redirect(url_for('itemsPage', category=category))
        else:
            return render_template('addItem.html',
                                   categories=user_categories,
                                   category_name=category)

    if request.method == 'POST':
        if not request.form['name']:
            flash("Please fill out the name field")
            return redirect(url_for('itemsPage', category=category))
        else:
            name = request.form['name']
            description = request.form['description']
            cat_id = request.form['category']
            cat_ = session.query(Categories).filter_by(id=cat_id).one()
            timestamp = dt.now()
            user = getUserInfo(login_session['user_id'])

            # Add new item to database
            new_item = Item(name=name,
                            description=description,
                            time_updated=timestamp,
                            user=user,
                            category=cat_)

            session.add(new_item)
            session.commit()
            flash("Successfully added item: " + new_item.name)

            return redirect(url_for('frontPage'))


@app.route('/catalog/<category>/items/<item_name>/edit/',
           methods=['GET', 'POST'])
@login_required
def editItem(category, item_name):
    """ Handles requests for editing an item """

    cat = session.query(Categories).filter_by(
          name=category.replace("-", " ")).first()
    item = session.query(Item).filter_by(
           name=item_name.replace("-", " "), cat_id=cat.id).one()
    user_categories = session.query(Categories).filter_by(
                      user_id=login_session['user_id']).all()

    if request.method == 'GET':
        if len(user_categories) == 0:
            flash('You need to be the author of a category to edit items')
            return redirect(url_for('itemsPage', category=category))
        elif login_session['user_id'] != item.user_id:
            flash("You don't have permission to edit this item")
            return redirect(url_for('itemsPage', category=category))
        else:
            return render_template('edititem.html',
                                   categories=user_categories,
                                   item=item,
                                   category=category)

    elif request.method == 'POST':
        if request.form['name']:
            item.name = request.form['name']
        if request.form['description']:
            item.description = request.form['description']
        if request.form['category']:
            item.cat_id = int(request.form['category'])
            category = session.query(Categories).filter_by(
                       id=item.cat_id).first().name.replace(" ", "-")
        item.time_updated = dt.now()
        session.add(item)
        session.commit()

        flash("Edit of '%s' completed" % item.name)
        return redirect(url_for('itemPage',
                                category=category,
                                item_name=item.name.replace(" ", "-")))


@app.route('/catalog/<category>/items/<item_name>/delete/',
           methods=['GET', 'POST'])
@login_required
def deleteItem(category, item_name):
    """ Handles requests for deleting an item """

    cat = session.query(Categories).filter_by(
          name=category.replace("-", " ")).first()
    item = session.query(Item).filter_by(name=item_name.replace("-", " "),
                                         cat_id=cat.id).first()

    if request.method == 'GET':
        if login_session['user_id'] == item.user_id:
            return render_template('deleteitem.html',
                                   category=category,
                                   item_name=item_name)
        else:
            flash("You don't have permission to delete this item")
            return redirect(url_for('itemsPage',
                                    category=category))

    elif request.method == 'POST':
        session.delete(item)
        session.commit()
        flash("Successfully deleted item: " + item.name)
        return redirect(url_for('itemsPage',
                                category=category))


@app.route('/login')
def showLogin():
    """ Serves the login page """

    # Create a state token for the user session
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


@app.route('/logout')
def logout():
    """ Clears the login session and returns the user to the front page """

    if 'access_token' in login_session:
        access_token = login_session['access_token']
        url = 'https://accounts.google.com/o/oauth2/revoke'
        # Revoke the user's auth credentials
        r = requests.post(url,
                          params={'token': access_token},
                          headers={'content-type':
                                   'application/x-www-form-urlencoded'})
        # Handle succesful revoke
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
            print("Unsuccessful login. Status code: " + str(r.status_code))
            print("Response content: " + r.content)
            return redirect(url_for('frontPage'))


@app.route('/gconnect', methods=['POST'])
def gconnect():
    """ Handles the Google authentication """

    # Validate the state token
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
        response = make_response(json.dumps('Failed to upgrade the\
                                            authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that access token is valid
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v3/tokeninfo?' +
           "access_token=%s" % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])

    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['sub'] != gplus_id:
        response = make_response(
                   json.dumps("Token's user ID doesn't match given user ID."),
                   401)
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
        response = make_response(json.dumps('Current user is ' +
                                            'already connected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
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

    return redirect(url_for('frontPage'))


@app.context_processor
def inject_session():
    """ Inject login_session to header for all templates """

    return dict(session=login_session)


def createUser(login_session):
    """ Creates a new user from the login_session data """

    newUser = User(name=login_session['username'],
                   email=login_session['email'])

    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()

    return user.id


def getUserInfo(user_id):
    """ Takes in a user id and returns a user object """

    user = session.query(User).filter_by(id=user_id).one()
    return user


def getUserId(email):
    """  Takes in an email address and returns the user id if it exists """

    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except:
        return None


def getCatName(catId):
    """ Takes in a category id and returns the category name """

    category = session.query(Categories).filter_by(id=catId).one()
    return category.name


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
