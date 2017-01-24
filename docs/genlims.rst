.. _genlims-page:

*******
GenLIMS
*******

.. _genlims-infra:

Infrastructure & Setup
======================

Servers
-------

(srvtg03, etc.)

Setting up TG3
--------------

The steps below assume that you already have **MongoDB** installed on your machine. If not, you can find download and install instructions `here <https://www.mongodb.com/download-center#community>`_. Note: ``bripipetools`` has been tested with version ``3.2`` of MongoDB.

Note: user and password information are stored in private INI config files on Box.

Setup ``data/db`` directory::

    cd /
    sudo mkdir data
    sudo chmod a+rwx data
    cd data
    mkdir db
    mongod

Connect to ``admin``::

    mongo admin

Set up ``tg3``::

    use tg3
    switched to db tg3
    db.createUser({user:"<user>",pwd:"<password>",roles:["readWrite","dbAdmin"]})
    Successfully added user: { "user" : "<user>", "roles" : [ "readWrite", "dbAdmin" ] }
    quit()

Connect to ``tg3``::

    mongo -u <user> -p <password> tg3


Test ``tg3``::

    show collections;
    quit()


Set up ``jnk/dump``::

    cd
    mkdir jnk
    cd jnk
    mongodump -u <user> -p <password> --host srvtg301 -d tg3
    cd dump
    mongorestore -u <user> -p <password> --drop -d tg3 tg3


Perform mongo 'pull' (dump + restore)::

    cd $HOME
    rm -rf dump/dc
    mongodump -u browser -p bibliome --host srvtg301 -d tg3
    cd dump/tg3
    rm logging*
    rm system.*
    cd ..
    mongorestore --drop -d tg3 tg3


-----

.. _genlims-architect:

Architecture
============



Documentation coming soon...
