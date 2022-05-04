export $(cat .dev.env | xargs)

python manage.py makemigrations
python manage.py migrate
echo "Running tests"
python manage.py test serverless.tests.test_orchestrate_deployments --failfast