export $(cat .env | xargs)

if [ -z $STREAM_PROJECT_DIR ]; then
    printf "Provide the directory of the api project"
    exit 77
fi

if [ -z $API_PROJECT_DIR ]; then
    printf "Provide the directory of the stream project"
    exit 77
fi

export MOCKUSERNAME="mockuser"
export MOCKEMAIL="mockemail@gmail.com"

python manage.py makemigrations && \
python manage.py migrate
python manage.py createsuperuser --noinput --username=$MOCKUSERNAME --email=$MOCKEMAIL
python manage.py drf_create_token $MOCKUSERNAME > ".tmp"
python $API_PROJECT_DIR/scripts/extract_token.py ".tmp" $STREAM_PROJECT_DIR/".env"
