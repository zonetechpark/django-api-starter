# Pull official base image 
FROM python:3.8.2-alpine3.11

# Set working directory
WORKDIR /usr/src/app

# Set env variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Install psycopg2 dependencies
RUN apk update \ 
    && apk add postgresql-dev gcc python3-dev musl-dev jpeg-dev zlib-dev \
    && apk add --no-cache openssl-dev libffi-dev

# Install dependencies
RUN python -m pip install --upgrade pip
RUN python -m pip install --upgrade Pillow
COPY ./requirements.txt /usr/src/app/requirements.txt
RUN pip install -r requirements.txt 

# Copy entrypoint.sh
COPY ./entrypoint.sh /usr/src/app/entrypoint.sh

# Copy Project
COPY . /usr/src/app
RUN chmod +x /usr/src/app/entrypoint.sh

ENTRYPOINT [ "/usr/src/app/entrypoint.sh" ]