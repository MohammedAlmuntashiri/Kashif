#!/bin/bash

# Wait for PostgreSQL to be ready (it takes a few seconds to boot)
echo "Waiting for PostgreSQL..."
while ! python -c "import psycopg2; psycopg2.connect('$DATABASE_URL')" 2>/dev/null; do
    sleep 1
done
echo "PostgreSQL is ready!"

# Run database migrations automatically
echo "Running migrations..."
flask db upgrade

# Hand off to whatever was passed as the container command. The backend
# service uses the default below (Flask dev server). Other services like
# the scheduler pass their own command in docker-compose (`python scheduler.py`)
# and skip Flask entirely.
if [ "$#" -eq 0 ]; then
    # --host=0.0.0.0 allows connections from outside the container (your browser)
    exec flask run --host=0.0.0.0
else
    exec "$@"
fi
