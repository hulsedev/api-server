export $(cat .dev.env | xargs)

python manage.py collectstatic --clear --noinput && \
    python manage.py makemigrations && \
    python manage.py migrate && \
    python manage.py runserver