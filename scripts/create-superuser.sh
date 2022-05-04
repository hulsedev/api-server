export $(cat .dev.env | xargs)

python manage.py createsuperuser