evocation
=========

A django app for bookmarking web pages.


## Setup and installation

Have postgres (on OSX, this is easiest with [postgresapp][pga]). Create a
database and user:

    create database evocation;
    create user evocation;
    grant all privileges on database evocation to evocation;

Using virtualenv, install the necessary software:

    mkvirtualenv evocation
    pip install -r requirements.txt

Setup the database tables:

    python manage.py migrate

Run the app:

    honcho start



[pga]: http://postgresapp.com
