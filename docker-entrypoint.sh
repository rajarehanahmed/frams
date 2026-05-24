#!/bin/sh
set -e

if [ -n "$POSTGRES_HOST" ]; then
  echo "Waiting for PostgreSQL at ${POSTGRES_HOST}:${POSTGRES_PORT:-5432}..."
  until nc -z "$POSTGRES_HOST" "${POSTGRES_PORT:-5432}"; do
    sleep 1
  done
fi

if [ "${DJANGO_MIGRATE:-1}" = "1" ]; then
  python manage.py migrate --noinput
fi

if [ "${DJANGO_COLLECTSTATIC:-0}" = "1" ]; then
  python manage.py collectstatic --noinput
fi

exec "$@"
