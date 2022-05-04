python manage.py makemigrations
python manage.py migrate
echo "Running tests"
python manage.py test serverless.tests.test_manage_project
#echo "Assessing code coverage"
#coverage run --source='.' manage.py test serverless
#coverage report