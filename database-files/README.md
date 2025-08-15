# `database-files` Folder

TODO: Put some notes here about how this works.  include how to re-bootstrap the db. 


This folder has all the SQL files that create and fill our project’s database.

## What’s inside

- `000_BachEndDatabase.sql` — makes the database and its tables.  
- `001_...sql`, `002_...sql`, etc. — put starting data into the tables.  
- The numbers at the start of each file name are the order they should run in.

## How it works

When the MySQL servers start up and the docker containers spin up, the files run in order
which creates the database and inserts the data.

## Starting the database (with Docker)

1. From the project’s main folder:

   docker compose up -d

2. MySQL will start and load all the `.sql` files into a new database and the docker containers will spin up.

## Resetting the database

If you want to start fresh and load the scripts again:

docker compose down -v   # stop and delete database files
docker compose up -d     # start again and reload scripts
