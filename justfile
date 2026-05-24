set dotenv-load := true

default:
    just --list

# Start the local Docker development stack.
up:
    docker compose up --build

# Start the local Docker development stack in the background.
up-detached:
    docker compose up --build -d

# Stop the local Docker development stack.
down:
    docker compose down

# Show logs for all local Docker services.
logs:
    docker compose logs -f

# Open a shell in the web container.
shell:
    docker compose exec web sh

# Run Django migrations in the web container.
migrate:
    docker compose exec web python manage.py migrate

# Create Django migrations in the web container.
makemigrations:
    docker compose exec web python manage.py makemigrations

# Create a Django superuser in the web container.
superuser:
    docker compose exec web python manage.py createsuperuser

# Run Django tests in the web container.
test:
    docker compose exec web python manage.py test

# Collect static files in the web container.
collectstatic:
    docker compose exec web python manage.py collectstatic --noinput

# Validate the local Docker Compose configuration.
config:
    docker compose config

# Build the local Docker web image.
build:
    docker compose build web

# Start the production-style Docker stack in the background.
prod-up:
    docker compose -f docker-compose.prod.yml up --build -d

# Stop the production-style Docker stack.
prod-down:
    docker compose -f docker-compose.prod.yml down

# Show logs for the production-style Docker stack.
prod-logs:
    docker compose -f docker-compose.prod.yml logs -f

# Validate the production-style Docker Compose configuration.
prod-config:
    docker compose -f docker-compose.prod.yml config

# Run the Django development server without Docker.
run:
    python manage.py runserver

# Run Django migrations without Docker.
local-migrate:
    python manage.py migrate

# Run Django tests without Docker.
local-test:
    python manage.py test
