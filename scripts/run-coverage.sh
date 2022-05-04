export $(cat .dev.env | xargs)

python manage.py makemigrations
python manage.py migrate
echo "Assessing code coverage"
coverage run --source='.' manage.py test serverless
coverage report