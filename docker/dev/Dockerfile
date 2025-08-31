# Pull official base image 
FROM python:3.12-alpine

COPY ./app /app

# Set working directory
WORKDIR /app

# Set env variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apk update && apk add --no-cache \
    gcc \
    python3-dev \
    musl-dev \
    libmagic \
    libffi-dev \
    postgresql-dev

# Install dependencies
RUN python -m pip install --upgrade pip
RUN python -m pip install --upgrade Pillow
RUN pip install -r /app/requirements/dev.txt 

# Copy entrypoint.sh
COPY ./docker/dev/entrypoint.sh /entrypoint.sh

EXPOSE 8002

RUN chmod +x /entrypoint.sh

ENTRYPOINT [ "/entrypoint.sh" ]