FROM python:3.8 as base

WORKDIR /app

# setup code
COPY . .
RUN pip install poetry==1.4.2

# Install dependencies using Poetry
RUN poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi


# run test
FROM base as test
# Set the environment variable
ENV MAKE="test"
CMD make $MAKE