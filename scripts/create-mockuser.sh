export $(cat .env | xargs)

if [ -z $STREAM_PROJECT_DIR ]; then
    printf "Provide the directory of the api project"
    exit 77
fi

if [ -z $API_PROJECT_DIR ]; then
    printf "Provide the directory of the stream project"
    exit 77
fi

if [ -z $API_ENV_DIR ]; then
    printf "Provide a path to the api virtual env"
    exit 77
fi

source "${API_ENV_DIR}/bin/activate"

python $API_PROJECT_DIR/manage.py makemigrations && \
python $API_PROJECT_DIR/manage.py migrate
python $API_PROJECT_DIR/manage.py createsuperuser --noinput --username=$MOCKUSERNAME --email=$MOCKEMAIL
python $API_PROJECT_DIR/manage.py drf_create_token $MOCKUSERNAME >> ".tmp"
python $API_PROJECT_DIR/scripts/extract_token.py ".tmp" $STREAM_PROJECT_DIR/".env"
