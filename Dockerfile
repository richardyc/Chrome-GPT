#syntax=docker/dockerfile:1

FROM debian:latest as base
WORKDIR /usr/src/app
ARG PY_VERSION="3.11.0"

# setting the enviroment 
RUN apt-get update -y && \
    apt-get install python3-pip -y && \
    apt-get install dieharder -y && \
    apt-get install wget -y && \
    apt-get clean && \
    apt-get autoremove

# setup python
ENV HOME="/root"
WORKDIR ${HOME}
RUN apt-get install -y git libbz2-dev libncurses-dev  libreadline-dev libffi-dev libssl-dev
RUN git clone --depth=1 https://github.com/pyenv/pyenv.git .pyenv
ENV PYENV_ROOT="${HOME}/.pyenv"
ENV PATH="${PYENV_ROOT}/shims:${PYENV_ROOT}/bin:${PATH}"

RUN pyenv install $PY_VERSION
RUN pyenv global $PY_VERSION

# setup code
COPY . .
RUN pip install poetry==1.4.2
RUN poetry install