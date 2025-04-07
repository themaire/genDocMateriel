#! /bin/bash

docker container stop gen-documents-materiel
docker container rm gen-documents-materiel
docker image rm gendocs:v1.0

docker build -t gendocs:v1.0 .
docker images

#docker run -d --name gen-documents-materiel -p 85:5000 gendocs:v1.0
#docker run -d --name gen-documents-materiel -p 85:5000 --restart always gendocs:v1.0
docker run -d --name gen-documents-materiel -p 85:5000 --restart unless-stopped gendocs:v1.0
