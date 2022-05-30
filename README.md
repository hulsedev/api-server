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
