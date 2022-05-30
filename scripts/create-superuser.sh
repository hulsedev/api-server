export $(cat .env | xargs)

python manage.py createsuperuser