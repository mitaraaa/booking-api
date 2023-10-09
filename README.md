# Football Fields Booking API

## About

This is a API for booking football fields. It is written in Python using FastAPI framework and PostgreSQL database.

## Requirements

-   Python 3.11
-   PostgreSQL

## Usage

To run the API, you need to have Python 3.11 and PostgreSQL installed. You also need to create a database and set the environment variables. You can do it by creating a `.env` file in the root directory of the project. The file should look like this:

```
POSTGRESQL_URL=postgresql+psycopg2://<name>:<password>@<host>:<port>/<database>
ADMINS=<admin1>,<admin2>,...
```

Then you can run the API using the following commands:

```sh
pip install -r requirements.txt
uvicorn main:app --reload
```

## Tests

```sh
Name                  Stmts   Miss Branch BrPart  Cover
-------------------------------------------------------
routers\auth.py          79      5     33      7    89%
routers\bookings.py     108     71     56      0    32%
routers\fields.py        73     32     44      0    50%
routers\owners.py        72     26     36      1    58%
routers\users.py         60      2     32      2    96%
-------------------------------------------------------
TOTAL                   392    136    201     10    61%
```
