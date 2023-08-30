FROM python:3.8 as base

WORKDIR /app

# setup code
COPY . .
RUN pip install poetry==1.4.2

# Install dependencies using Poetry
RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi

# image to dev
FROM base as dev
CMD sh -c "while sleep 1000; do :; done"

# image to run tests
FROM base as test
ARG MAKE="tests"
CMD make $MAKE
