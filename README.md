# Item catalogue project - Udacity

This project creates a locally hosted website with sports items. Users logged in with Google will be able to edit and add items.

## Getting Started

These instructions will get you a copy of the project up and running on in a virtual environment.

### Prerequisites

* Python 3.6
* Vagrant
* VirtualBox

Installation instructions for Vagrant and VirtualBox can be found in the Built With section below

### Installing

Install required python modules
```
pip install -r requirements.txt
```

Initialise virtual environment

From your terminal, type:
```
vagrant up
```
When finished, ssh into your virtual environment:

```
vagrant ssh
cd /vagrant
```

Initialise database and populate it with sample data
```
python create_database.py
python populate_item_catalogue.py
```

## Launch the site

In your virtual environment:
```
python views.py
```
You can now access your site at http://localhost:5000/

## Examples

### Front page
Located at http://localhost:5000/
![Screenshot of the front page](https://i.gyazo.com/5050a7363dd2725873df16190f9e5c9c.jpg)

### Item page for the author of an item
Example url: http://localhost:5000/catalog/Hockey/items/Hockey-Puck/
![Screenshot of item page for logged in user](https://i.gyazo.com/ac566abce102bf7f07a1aeca0f982f49.jpg)

### JSON exports
Export all categories and items:
http://localhost:8000/catalog.json/
Response:
```
{
  "Categories": [
    {
      "id": 1,
      "items": [
        {
          "category_id": 1,
          "description": "An ideal ball for players taking their first steps                         onto the pitch, the Soccer Ball is a solid, durable                         go-to that handles the rigors of tough shooting and                         skill drills while celebrating the sport's iconic                         tournament.",
          "id": 1,
          "last_update": "Fri, 11 May 2018 14:08:53 GMT",
          "name": "Soccer ball",
          "user_id": 1
        },
        {
          "category_id": 1,
          "description": "Equipped with a smooth latex foam palm, the Nike                         Adult Match Goalkeeper Soccer Goalie Gloves offer                         reliable impact protection and consistent grip so                         you can block the hardest shots in any weather                         conditions.",
          "id": 2,
          "last_update": "Fri, 11 May 2018 14:08:53 GMT",
          "name": "Goalkeeper Gloves",
          "user_id": 1
        }
      ],
      "name": "Soccer"
    },
    {
      "id": 2,
      "items": [
        {
          "category_id": 2,
          "description": "An all-in-one package that includes an easy-to-use                         air pump to maintain the perfect inflation",
          "id": 3,
          "last_update": "Fri, 11 May 2018 14:08:53 GMT",
          "name": "A pretty good basketball",
          "user_id": 1
        },
        {
          "category_id": 2,
          "description": "Don't dunk on this one. It is going to break",
          "id": 4,
          "last_update": "Fri, 11 May 2018 14:08:53 GMT",
          "name": "Very fragile basketball hoop",
          "user_id": 1
        }
      ],
      "name": "Basketball"
    },
```

Export items in one category:
http://localhost:8000/catalog/<CATEGORY_NAME>.json
Response will be similar to the above

Export one item:
http://localhost:8000/catalog/<CATEGORY_NAME>/<ITEM_NAME>.json
Response:
```
{
    "category_id": 5,
    "description": "It's a puck. No further explanation needed",
    "id": 10,
    "last_update": "Fri, 11 May 2018 14:08:54 GMT",
    "name": "Hockey Puck",
    "user_id": 1
}
```

## Built With

* [Vagrant](https://www.vagrantup.com/)
* [VirtualBox](https://www.virtualbox.org/wiki/Downloads)

## Author

* Lasse Alsbirk
