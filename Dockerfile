FROM python:3.9-slim

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        build-essential \
        libpq-dev \
        curl \
    && rm -rf /var/lib/apt/lists/*

RUN curl -s https://get.prisma.io/cli/install.sh | bash

COPY requirements.txt /app/

RUN python -m pip install --upgrade pip \
    && python -m pip install --no-cache-dir -r requirements.txt

COPY . /app/

EXPOSE 80

# Command to run the application
CMD ["/bin/bash", "-c", "source .venv/Scripts/activate && uvicorn main:app --host 0.0.0.0 --port 80", "--env-file", ".env"]
