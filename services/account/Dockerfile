FROM python:3.12.5

WORKDIR /account-service

COPY src/ /account-service/src/
COPY alembic.ini /account-service/alembic.ini
COPY pyproject.toml /account-service/

RUN pip install -U pip
RUN pip install --no-cache-dir --upgrade -e .
