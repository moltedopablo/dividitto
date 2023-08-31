FROM python:3.11.5-alpine3.18
COPY Pipfile.lock Pipfile.lock
COPY Pipfile Pipfile


RUN apk update && apk add --no-cache --virtual .build-deps \
    gcc \
    musl-dev \
    postgresql-dev \
    python3-dev \
    libffi-dev \
    openssl-dev \
    cargo \
    && pip install --upgrade pip \
    && pip install pipenv \
    && pip install uwsgi \
    && pipenv install --system --deploy \
    && apk del .build-deps

COPY ./app /app
WORKDIR /app
RUN python manage.py collectstatic --no-input

EXPOSE 80
CMD uwsgi --http "0.0.0.0:80" --module app.wsgi:application --master --processes 4 --threads 2 --static-map /static=/app/staticfiles
