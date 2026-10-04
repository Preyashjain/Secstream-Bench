FROM python:3.11.10-slim-bookworm

RUN apt-get update \
    && apt-get install --no-install-recommends -y build-essential clang make git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /workspace
COPY requirements.txt pyproject.toml ./
RUN python -m pip install --no-cache-dir -r requirements.txt
ENV PYTHONPATH=/workspace/src

COPY . .