#!/bin/bash

# Wait for database to be ready
until pg_isready -h $DB_HOST -p $DB_PORT -U $DB_USER
do
  echo "Waiting for database connection..."
  sleep 2
done

# Run migrations
python manage.py migrate

# Start the Django development server
python manage.py runserver 0.0.0.0:8000