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

| Name                | Stmts | Miss | Branch | BrPart | Cover |
| ------------------- | ----- | ---- | ------ | ------ | ----- |
| routers\auth.py     | 81    | 4    | 33     | 6      | 91%   |
| routers\bookings.py | 123   | 9    | 74     | 8      | 91%   |
| routers\fields.py   | 78    | 4    | 46     | 2      | 95%   |
| routers\owners.py   | 75    | 4    | 40     | 4      | 93%   |
| routers\users.py    | 60    | 2    | 32     | 2      | 96%   |
| TOTAL               | 417   | 23   | 225    | 22     | 93%   |
