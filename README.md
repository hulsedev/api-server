# Hulse API Server
Server handling authentication and cluster management for Hulse users.

## Getting Started

Clone the application:

```bash
git clone git@github.com:hulsedev/api-server.git
cd api-server
```

Next, create a virtual env & install dependencies:
```bash
python -m venv env
source env/bin/activate
pip install -r requirements.txt
```
*Note that these instructions on db setups are the same as for getting started with the stream-server, if you already completed those, feel free to skip these.*

You will then need to setup your local Postgres database:
```bash
sudo -u postgres psql
```

Once you're connected to the postgres shell, run the following commands:
```postgresql
CREATE DATABASE "hulse-api";
CREATE USER postgres WITH PASSWORD 'postgres';
ALTER ROLE postgres SET client_encoding TO 'utf8';
ALTER ROLE postgres SET default_transaction_isolation TO 'read committed';
ALTER ROLE postgres SET timezone TO 'UTC';
GRANT ALL PRIVILEGES ON DATABASE hulse-api TO postgres;
```
> Find more info about setting postgresql with django [here](https://www.digitalocean.com/community/tutorials/how-to-use-postgresql-with-your-django-application-on-ubuntu-20-04).

## Running locally

You can directly run the app using the following script:
```bash
bash scripts/create-superuser.sh
bash scripts/run-debug-server.sh
```

Note that you'll need to obtain the environment variables required to connect to Auth0 and then place them into a `.env` file.

## Deployment

The app is currently deployed on Heroku using free dynos (free credits). You can find the Heroku deployment instructions in the `Procfile`.

## References

Checkout the following sources for more info:
- [Integration of Auth0 with Django](https://auth0.com/blog/django-authentication/) 
