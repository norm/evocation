evocation
=========

A django app for bookmarking web pages.

![evocation preview](https://raw.github.com/norm/evocation/master/evocation.png)

Currently depends on command line tools only available for OS X.


## Setup and installation

Have postgres (on OSX, this is easiest with [postgresapp][pga]). Create a
database and user:

    create database evocation;
    create user evocation;
    grant all privileges on database evocation to evocation;

Have redis (evocation uses database 1 to keep celery information in):

    brew install redis
    # follow the instructions for starting redis

Install pre-requisite OS X software with homebrew:

    brew install libjpeg libtiff little-cms2 webarchiver webkit2png webp xapian

Create a virtualenv and install the required python libraries:

    mkvirtualenv evocation
    pip install -r requirements.txt

Then in the virtualenv, install the python xapian bindings for the 
version of xapian you have installed (`brew info xapian`).

    XAPIAN_VERSION=1.2.19
    wget http://oligarchy.co.uk/xapian/${XAPIAN_VERSION}/xapian-bindings-${XAPIAN_VERSION}.tar.xz
    tar xJf xapian-bindings-${XAPIAN_VERSION}.tar.xz
    cd xapian-bindings-${XAPIAN_VERSION}
    ./configure --with-python
    make 
    sudo make install

Setup the database tables:

    python manage.py migrate

Run the app:

    # in production
    honcho start

    # whilst developing
    honcho -e env -f Procfile.dev start

If you use it, export [your bookmarks][pinboard] from Pinboard as JSON and
then import them:

    python manage.py import_pinboard format-json.json

[pga]: http://postgresapp.com
[wa]: http://www.chainsawonatireswing.com/2013/11/17/how-to-save-a-perfectly-scraped-webpage-into-devonthink/#needed-command-line-software
[pinboard]: https://pinboard.in/export/
