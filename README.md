# Foodgram Application

Foodgram is a publishing application that allows users to add, edit and save recipes to their favorites. It also includes a shopping cart function, which generates a shopping list for all selected recipes. The application is built using Django & React frameworks.

***Getting started***

1. Install Docker from the official website (https://docs.docker.com/engine/install/)
2. Clone the repository from GitHub using the command in the terminal: git clone https://github.com/garmagelm/foodgram-project-react
3. Create a virtual environment using the command: python3 -m venv venv
4. Create a .env file and enter the following secrets:
makefile
5. Copy code
```
DB_ENGINE=django.db.backends.postgresql
DB_NAME=<your_database_name>
POSTGRES_USER=<your_postgres_username>
POSTGRES_PASSWORD=<your_postgres_password>
DB_HOST=db
DB_PORT=5432
```

Note: You can use localhost instead of db if you're not using docker-compose.

6. Launch the container from the infra folder with the command: ```docker-compose up --build -d```
7. Perform the migration with the command: ```docker-compose exec backend python manage.py migrate --noinput```
8. Create a superuser using the command: ```docker-compose exec backend python manage.py createsuperuser```
9. Collect static files in one directory: ```docker-compose exec backend python manage.py collectstatic --no-input```
10. Create fixtures in the backend: ```docker-compose exec backend python manage.py loaddata ingredients.json```
11. To stop running docker containers and delete them, use the command: ```docker-compose down```

***Tech stack***

* Python 3
* Django
* Django REST Framework
* Docker Desktop
* PostgreSQL
* Deployment

The project is currently deployed on the server http://foodhelp.hopto.org.

Note: Replace <your_database_name>, <your_postgres_username> and <your_postgres_password> with your own values in the .env file.
