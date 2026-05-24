# FRAMS

FRAMS is a Django-based face recognition attendance management system. It
contains separate office and teacher modules, uses PostgreSQL for persistence,
stores uploaded images under `media/`, and uses OpenCV plus `face-recognition`
for image processing.

## Stack

- Python 3.9
- Django 4.2
- PostgreSQL
- OpenCV
- face-recognition / dlib
- Gunicorn and WhiteNoise for production container runs

## Project Layout

- `frams/` - Django project settings, URLs, ASGI/WSGI entrypoints
- `progoffice/` - office/admin attendance workflows
- `teacher/` - teacher-facing workflows
- `templates/` - Django templates
- `static/` - source static assets
- `media/` - uploaded files, ignored by git

## Environment

Copy the example file and adjust values as needed:

```sh
cp .env.example .env
```

Important variables:

```env
SECRET_KEY=change-me
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=http://localhost:8000

POSTGRES_HOST=db
POSTGRES_DB=frams
POSTGRES_USER=bloggenius
POSTGRES_PASSWORD=bloggenius
POSTGRES_PORT=5432
```

## Run With Docker

Start the development stack:

```sh
docker compose up --build
```

Open:

```text
http://localhost:8000
```

The Docker development service runs migrations automatically and starts Django's
development server. PostgreSQL data and uploaded media are stored in Docker
volumes.

## Production-Style Docker Run

Set production values in `.env` or the shell:

```env
SECRET_KEY=replace-me
DEBUG=False
ALLOWED_HOSTS=your-domain.com,www.your-domain.com
CSRF_TRUSTED_ORIGINS=https://your-domain.com,https://www.your-domain.com
POSTGRES_PASSWORD=replace-me
```

Start the production compose stack:

```sh
docker compose -f docker-compose.prod.yml up --build -d
```

The production image runs migrations, collects static files, and serves the app
with Gunicorn on port `8000`. Use a reverse proxy or platform load balancer in
front of it for TLS and public traffic.

## Run Without Docker

Install system packages required by OpenCV, dlib, and PostgreSQL client builds,
then create a virtual environment:

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Run migrations and start Django:

```sh
python manage.py migrate
python manage.py runserver
```

The app will be available at:

```text
http://127.0.0.1:8000
```
