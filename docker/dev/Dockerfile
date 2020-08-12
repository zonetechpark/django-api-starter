# Pull official base image 
FROM python:3.8-slim

COPY ./app /app

# Set working directory
WORKDIR /app

# Set env variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update \ 
    && apt-get install -y gcc python3-dev musl-dev libmagic1 libffi-dev 

# Install dependencies
RUN python -m pip install --upgrade pip
RUN python -m pip install --upgrade Pillow
RUN pip install -r /app/requirements/dev.txt 

# Copy entrypoint.sh
COPY ./docker/dev/entrypoint.sh /entrypoint.sh

RUN chmod +x /entrypoint.sh

ENTRYPOINT [ "/entrypoint.sh" ]