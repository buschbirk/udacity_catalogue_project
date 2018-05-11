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

## Built With

* [Vagrant](https://www.vagrantup.com/)
* [VirtualBox](https://www.virtualbox.org/wiki/Downloads)

## Author

* Lasse Alsbirk
