export $(cat .env | xargs)

docker-compose up -d