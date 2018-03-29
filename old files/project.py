# -*- coding: utf-8 -*-

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
engine = create_engine('sqlite:///restaurantmenuwithusers.db')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


#JSON APIs to view Restaurant Information
@app.route('/restaurant/<int:restaurant_id>/menu/JSON')
def restaurantMenuJSON(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    items = session.query(MenuItem).filter_by(restaurant_id = restaurant_id).all()
    return jsonify(MenuItems=[i.serialize for i in items])


@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/JSON')
def menuItemJSON(restaurant_id, menu_id):
    Menu_Item = session.query(MenuItem).filter_by(id = menu_id).one()
    return jsonify(Menu_Item = Menu_Item.serialize)

@app.route('/restaurant/JSON')
def restaurantsJSON():
    restaurants = session.query(Restaurant).all()
    return jsonify(restaurants= [r.serialize for r in restaurants])


#Show all restaurants
@app.route('/')
@app.route('/restaurant/')
def showRestaurants():
  restaurants = session.query(Restaurant).order_by(asc(Restaurant.name))
  if 'username' not in login_session:
      return render_template('publicrestaurants.html', restaurants = restaurants)
  else:
      return render_template('restaurants.html', restaurants = restaurants)

#Create a new restaurant
@app.route('/restaurant/new/', methods=['GET','POST'])
def newRestaurant():
  if 'username' not in login_session:
    return redirect('/login')
    
  if request.method == 'POST':
      newRestaurant = Restaurant(name = request.form['name'],
                                 user_id = login_session['user_id'])
      session.add(newRestaurant)
      flash('New Restaurant %s Successfully Created' % newRestaurant.name)
      session.commit()
      return redirect(url_for('showRestaurants'))
  else:
      return render_template('newRestaurant.html')

#Edit a restaurant
@app.route('/restaurant/<int:restaurant_id>/edit/', methods = ['GET', 'POST'])
def editRestaurant(restaurant_id):
  editedRestaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    
  if 'username' not in login_session:
      return redirect('/login')
  if editedRestaurant.user_id != login_session['user_id']:
        return """<script>function myFunction() 
                {alert('You are not authorized to edit this restaurant. 
                Please create your own restaurant in order to edit.');}
                </script><body onload='myFunction()''>"""
  if request.method == 'POST':
      if request.form['name']:
        editedRestaurant.name = request.form['name']
        flash('Restaurant Successfully Edited %s' % editedRestaurant.name)
        return redirect(url_for('showRestaurants'))
  else:
    return render_template('editRestaurant.html', restaurant = editedRestaurant)


#Delete a restaurant
@app.route('/restaurant/<int:restaurant_id>/delete/', methods = ['GET','POST'])
def deleteRestaurant(restaurant_id):
  
  if 'username' not in login_session:
    return redirect('/login')
    
  restaurantToDelete = session.query(Restaurant).filter_by(id = restaurant_id).one()
  
  if restaurantToDelete.user_id != login_session['user_id']:
        return """<script>function myFunction() 
                {alert('You are not authorized to delete this restaurant. 
                Please create your own restaurant in order to edit.');}
                </script><body onload='myFunction()''>"""      
  
  if request.method == 'POST':
    session.delete(restaurantToDelete)
    flash('%s Successfully Deleted' % restaurantToDelete.name)
    session.commit()
    return redirect(url_for('showRestaurants', restaurant_id = restaurant_id))
  else:
    return render_template('deleteRestaurant.html',restaurant = restaurantToDelete)

#Show a restaurant menu
@app.route('/restaurant/<int:restaurant_id>/')
@app.route('/restaurant/<int:restaurant_id>/menu/')
def showMenu(restaurant_id):
    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    creator = getUserInfo(restaurant.user_id)
    items = session.query(MenuItem).filter_by(restaurant_id = restaurant_id).all()
    
    if 'user_id' in login_session and login_session['user_id'] == creator.id:
        return render_template('menu.html', items = items, 
                               restaurant = restaurant, creator = creator)
    else:
        return render_template('publicmenu.html', items = items, 
                               restaurant = restaurant, 
                               creator= creator)


#Create a new menu item
@app.route('/restaurant/<int:restaurant_id>/menu/new/',methods=['GET','POST'])
def newMenuItem(restaurant_id):
  if 'username' not in login_session:
    return redirect('/login')
  restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
  
  if login_session['user_id'] != restaurant.user_id:
      return """<script>function myFunction() 
                {alert('You are not authorized to delete this restaurant. 
                Please create your own restaurant in order to edit.');}
                </script><body onload='myFunction()''>""" 
  
  if request.method == 'POST':
      newItem = MenuItem(name = request.form['name'], 
                         description = request.form['description'], 
                         price = request.form['price'], 
                         course = request.form['course'], 
                         restaurant_id = restaurant_id,
                         user_id = restaurant.user_id)
      session.add(newItem)
      session.commit()
      flash('New Menu %s Item Successfully Created' % (newItem.name))
      return redirect(url_for('showMenu', restaurant_id = restaurant_id))
  else:
      return render_template('newmenuitem.html', restaurant_id = restaurant_id)

#Edit a menu item
@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/edit', methods=['GET','POST'])
def editMenuItem(restaurant_id, menu_id):
    if 'username' not in login_session:
      return redirect('/login')
    editedItem = session.query(MenuItem).filter_by(id = menu_id).one()
    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    
    if login_session['user_id'] != restaurant.user_id:
        return """<script>function myFunction() 
                {alert('You are not authorized to edit this menu item. 
                Please create your own restaurant in order to edit.');}
                </script><body onload='myFunction()''>"""         
    
    if request.method == 'POST':
        if request.form['name']:
            editedItem.name = request.form['name']
        if request.form['description']:
            editedItem.description = request.form['description']
        if request.form['price']:
            editedItem.price = request.form['price']
        if request.form['course']:
            editedItem.course = request.form['course']
        session.add(editedItem)
        session.commit() 
        flash('Menu Item Successfully Edited')
        return redirect(url_for('showMenu', restaurant_id = restaurant_id))
    else:
        return render_template('editmenuitem.html', restaurant_id = restaurant_id, menu_id = menu_id, item = editedItem)


#Delete a menu item
@app.route('/restaurant/<int:restaurant_id>/menu/<int:menu_id>/delete', methods = ['GET','POST'])
def deleteMenuItem(restaurant_id,menu_id):
    if 'username' not in login_session:
      return redirect('/login')
    restaurant = session.query(Restaurant).filter_by(id = restaurant_id).one()
    itemToDelete = session.query(MenuItem).filter_by(id = menu_id).one()
    if login_session['user_id'] != restaurant.user_id:
        return """<script>function myFunction() 
                {alert('You are not authorized to delete this menu item. 
                Please create your own restaurant in order to edit.');}
                </script><body onload='myFunction()''>"""        
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash('Menu Item Successfully Deleted')
        return redirect(url_for('showMenu', restaurant_id = restaurant_id))
    else:
        return render_template('deleteMenuItem.html', item = itemToDelete)


@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits) \
                    for x in range(32))
    login_session['state'] = state
    return render_template('login.html', STATE = state)


@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['access_token']
        if login_session['provider'] == 'facebook':
            fbdisconnect()
            del login_session['facebook_id']
            
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        del login_session['user_id']
        del login_session['provider']
        flash("you have been successfully logged out")
        return redirect(url_for('showRestaurants'))
    else:
        flash("you were not even logged in my dude")
        return redirect(url_for('showRestaurants'))



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

    url = ('https://www.googleapis.com/oauth2/v3/tokeninfo?access_token=%s'% access_token)
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
    login_session['provider'] = 'google'
    
    #get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)
    
    data = answer.json()
    
    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    
    login_session['user_id'] = getUserId(login_session['email'])
    if not login_session['user_id']:
        login_session['user_id'] = createUser(login_session)
    

    
    
    
    output = ''
    output += '<h1>Welcome, ' + login_session['username'] + '!</h1>'
    output += '<img src="' + login_session['picture'] 
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;\
                -webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print("Finished Oauth flow")
    
    return output
    
#DISCONNECT current session. Revoke a users token and reset login session
@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    
    url = 'https://accounts.google.com/o/oauth2/revoke'
    
    result = requests.post(url, params={'token': access_token},
                           headers = {'content-type': 'application/x-www-form-urlencoded'})
  
    
    if result.status_code == '200':
        # Reset the user's session
        del login_session['credentials']
        del login_session['gplus_id']
        del login_session['username']
        del login_session['email']
        del login_session['picture']
        
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        response = make_response(json.dumps('Failed to revoke token for \
                                            given user.'), 400)
        response.headers['Content-Type'] = 'application/json'
        return response


@app.route('/fbconnect', methods=['POST'])
def fbconnect():
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    access_token = request.data
    
    
    #Exhcange client token for long-lived server-side token
    app_id = json.loads(open('fb_client_secrets.json', 'r').read())['web']['app_id']
    app_secret = json.loads(open('fb_client_secrets.json', 'r').read())['web']['app_secret']
    
    url = 'https://graph.facebook.com/oauth/access_token?grant_type=fb_exchange_token'
    url += '&client_id=%s&client_secret=%s&\
    fb_exchange_token=%s' % (app_id,app_secret,access_token)

    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    
    #Use token to get user info from API
    userinfo_url = 'https://graph.facebook.com/v2.12/me'
    # strip expire tag from access_token
    token = result.split("&")[0]
    
    url = 'https://graph.facebook.com/v2.12/me?access_token=%s&fields=name,id,email' % token
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    
    data = json.loads(result)
    
    login_session['username'] = data["name"]
    login_session['email'] = data['email']
    login_session['facebook_id'] = data['id']
    login_session['provider'] = 'facebook'
    
    # Get user picture
    url = 'https://graph.facebook.com/v2.12/me/picture?%s' % token
    url += '&redirect=0&height=200&width=200'
    h = httplib2.Http()
    result = h.request(url, 'GET')[1]
    data = json.loads(result)
    
    login_session['picture'] = data['data']['url']
    
    # see if user exists
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, ' + login_session['username'] + '!</h1>'
    output += '<img src="' + login_session['picture'] 
    output += ' " style = "width: 300px; height: 300px;border-radius: 150px;\
                -webkit-border-radius: 150px;-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print("Finished Oauth flow")


@app.route('/fbdisconnect')
def fbdisconnect():
    facebook_id = login_session['facebook_id']
    url = 'https://graph.facebook.com/%s/permissions' & facebook_id
    h = httplib2.Http()
    result = h.request(url, 'DELETE')[1]
    del login_session['username']
    del login_session['email']
    del login_session['picture']
    del login_session['user_id']
    del login_session['facebook_id']
    return "You have been logged out"








def createUser(login_session):
    newUser = User(name = login_session['username'], 
                   email = login_session['email'],
                   picture = login_session['picture'])
    
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



if __name__ == '__main__':
  app.secret_key = 'super_secret_key'
  app.debug = True
  app.run(host = '0.0.0.0', port = 5000)
