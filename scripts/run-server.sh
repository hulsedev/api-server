export $(cat .env | xargs)

# optionally activate the virtual environment for the api server
if [ ! -z $API_ENV_DIR ]; then
    printf "Activating virtual environment for api server...\n"
    source "${API_ENV_DIR}/bin/activate"
fi

python manage.py collectstatic --clear --noinput && \
    python manage.py makemigrations && \
    python manage.py migrate && \
    python manage.py runserver $API_SERVER_PORT --verbosity=3