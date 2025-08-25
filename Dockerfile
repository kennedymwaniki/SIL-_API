FROM python:3.13-slim AS builder

# Install system dependencies required for psycopg2
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir /app

WORKDIR /app

# set environment variables
# prevent python from writing pyc files to sdk
ENV PYTHONDONTWRITEBYTECODE 1

# prevent python from buffering stdout and stderr
ENV PYTHONUNBUFFERED 1

# upgrade pip and install dependencies
RUN pip install --upgrade pip 

# copy requirements
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt


# stage 2

FROM python:3.13-slim

# Install PostgreSQL client for health checking
RUN apt-get update && apt-get install -y \
    libpq5 \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -m -r appuser \
    && mkdir /app \
    && chown -R appuser /app

COPY --from=builder /usr/local/lib/python3.13/site-packages/ /usr/local/lib/python3.13/site-packages/
COPY --from=builder /usr/local/bin/ /usr/local/bin/

WORKDIR /app

COPY --chown=appuser:appuser . .


# Set environment variables to optimize Python
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1 

USER appuser

EXPOSE 8000

CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]

# script to wait for database and run migrations
# COPY --chown=appuser:appuser docker-entrypoint.sh /app/
# RUN chmod +x /app/docker-entrypoint.sh
# CMD ["/app/docker-entrypoint.sh"]
