FROM python:3-slim

RUN apt-get update && \
    apt-get install -y locales locales-all
RUN locale-gen fr_FR.UTF-8


WORKDIR /usr/src/app
ENV IN_DOCKER_CONTAINER=Yes

COPY requirements.txt .
COPY .env .

# Installation des dépendances

RUN pip install --no-cache-dir -r requirements.txt

# Copie du script Python et fichiers necessaires
COPY flaskServer.py .
ADD static ./static
ADD templates ./templates

EXPOSE 5000

CMD ["flask", "--app", "flaskServer.py", "run", "--host=0.0.0.0", "--debug"]
