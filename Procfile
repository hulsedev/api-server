web: gunicorn feed.wsgi
web2: daphne feed.agsi:application --port $PORT --bind 0.0.0.0 -v2
release: python manage.py makemigrations && python manage.py migrate
