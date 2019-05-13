FROM python:3.7-alpine
MAINTAINER andersonRT

RUN apk update \
        && apk add --no-cache git openssh-client \
        && pip install pipenv \
        && addgroup -S -g 1001 app \
        && adduser -S -D -h /app -u 1001 -G app app

RUN mkdir /app/src
RUN mkdir /app/src/data
WORKDIR /app/src

COPY Pipfile.lock /app/src
COPY Pipfile /app/src
COPY scraper.py /app/src

RUN pipenv install --deploy --ignore-pipfile

CMD ["pipenv", "run", "python", "scraper.py"]
