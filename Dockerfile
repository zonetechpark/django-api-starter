# Pull official base image 
FROM python:3.8-slim

# Set working directory
WORKDIR /usr/src/app

# Set env variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

RUN apt-get update \ 
    && apt-get install -y gcc python3-dev musl-dev libmagic1 libffi-dev 

# Install dependencies
RUN python -m pip install --upgrade pip
RUN python -m pip install --upgrade Pillow
COPY ./requirements.txt /usr/src/app/requirements.txt
RUN pip install -r requirements.txt 
RUN python -m pip install --upgrade pip

# Copy entrypoint.sh
COPY ./entrypoint.sh /usr/src/app/entrypoint.sh

# Copy Project
COPY . /usr/src/app
RUN chmod +x /usr/src/app/entrypoint.sh

ENTRYPOINT [ "/usr/src/app/entrypoint.sh" ]