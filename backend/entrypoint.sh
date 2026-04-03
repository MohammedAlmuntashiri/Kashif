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

# Start Flask server
# --host=0.0.0.0 allows connections from outside the container (your browser)
flask run --host=0.0.0.0
