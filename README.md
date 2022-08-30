# Project: Foodgram
A publishing application, editing and adding recipes to favorites with the "shopping cart" function, which provides a shopping list for all selected recipes.

It works on the basis of Django & React.

***Setting:***
1. Install [Docker](https://docs.docker.com/engine/install /).
2. Clone the repository from GitHub with the command in the terminal
```bash
git clone https://github.com/garmagelm/foodgram-project-react
```

***Setting up a variable environment .env:***

* Creating a virtual environment with the command
```bash
python3 -m venv venv
```
* Creating a file .env
* Enter the values of the secrets: 
```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=<название вашей базы данных>
POSTGRES_USER=<имя пользователя в postgres>
POSTGRES_PASSWORD=<пароль пользователя>
DB_HOST=db  # Сюда можете прописать localhost, либо оставить, если будете использовать docker-compose
DB_PORT=5432
```

***Commands for Docker***
1. Launch the container from the infra folder with the command
```bash
docker-compose up --build -d
```
2. Perform the migration with the command
```bash
docker-compose exec backend python manage.py migrate --noinput
```
3. Creating a superuser
```bash
docker-compose exec backend python manage.py createsuperuser
```
4. Collect static files in one directory:
```bash
docker-compose exec backend python manage.py collectstatic --no-input
```
5. In the backend, we create fixtures 
```bash
docker-compose exec backend python manage.py loaddata ingredients.json
```
6. Command to stop running docker containers and delete them:
```bash
docker-compose down
```

***Tech systems used:***

* Python3
* Django
* Django REST Framework
* Docker Desktop
* Posgresql


![workflow](https://github.com/garmagelm/foodgram-project-react/actions/workflows/foodgram_project.yml/badge.svg)

The project deployed on the server http://foodhelp.hopto.org