FROM python:3.8 as base
RUN echo "building base."

WORKDIR /app

# setup code
COPY . .
RUN pip install poetry==1.4.2

# Install dependencies using Poetry
RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi

FROM base as dev
RUN echo "building dev."
CMD sh -c "while sleep 1000; do :; done"

# run test
FROM base as test
# Set the environment variable
ARG MAKE="tests"
CMD make $MAKE
