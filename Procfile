web: gunicorn feed.wsgi
web: daphne feed.asgi:application
release: python manage.py makemigrations && python manage.py migrate