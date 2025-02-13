FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -U uv pip
RUN uv pip install --system -r requirements.txt --verbose