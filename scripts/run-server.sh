export $(cat .env | xargs)

if [ -z $API_SERVER_PORT ]; then
    printf "Provide a port for the api server"
    exit 77
fi

if [ -z $API_PROJECT_DIR ]; then
    printf "Provide a directory for the api project"
    exit 77
fi

# optionally activate the virtual environment for the api server
if [ -z $API_ENV_DIR ]; then
    printf "Provide a path to the api virtual env"
    exit 77
fi

source "${API_ENV_DIR}/bin/activate"

python $API_PROJECT_DIR/manage.py collectstatic --clear --noinput && \
python $API_PROJECT_DIR/manage.py makemigrations && \
python $API_PROJECT_DIR/manage.py migrate && \
python $API_PROJECT_DIR/manage.py runserver $API_SERVER_PORT --verbosity=3