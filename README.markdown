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

Search uses xapian, so that needs to be installed:

*   On ubuntu:

        sudo apt-get install python-xapian

*   On OSX:

    First install xapian.

        brew install xapian

    Then in the virtualenv, install the python xapian bindings for the 
    version of xapian you have installed.

        XAPIAN_VERSION=1.2.19
        wget http://oligarchy.co.uk/xapian/${XAPIAN_VERSION}/xapian-bindings-${XAPIAN_VERSION}.tar.xz
        tar xJf xapian-bindings-${XAPIAN_VERSION}.tar.xz
        cd xapian-bindings-${XAPIAN_VERSION}
        ./configure --with-python
        make 
        sudo make install

Run the app:

    honcho start



[pga]: http://postgresapp.com
