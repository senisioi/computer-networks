# 2018 computer networks lab

## Requirements
- [docker](https://docs.docker.com/install/linux/docker-ce/ubuntu/)
- [docker-compose](https://docs.docker.com/compose/install/) already in this repo

## Starting up
```bash
# build the docker image
docker build -t baseimage ./docker/
# start services defined in docker-compose.yml
docker-compose up -d
```

## Basic docker commands
```bash
# stop services
docker-compose down

# see the containers running
docker ps

# kill a container
docker kill $CONTAINER_ID

# see the containers not running
docker ps --filter "status=exited"

# remove the container
docker rm $CONTAINER_ID

# list available networks
docker network ls

# inspect network
docker network inspect $NETWORK_ID

# inspect container
docker inspect $CONTAINER_ID

# see container ip
docker inspect -f '{{range .NetworkSettings.Networks}}{{.IPAddress}}{{end}}' $CONTAINER_ID

# attach to a container
docker exec -it $CONTAINER_ID bash

# attach using docker-compose
docker-compose exec rt1 bash

# attach as root to a container
docker-compose exec --user root rt1 bash
```

## References
- [docker concepts](https://docs.docker.com/engine/docker-overview/#docker-engine)
- [docker-compose](http://docker-k8s-lab.readthedocs.io/en/latest/docker/docker-compose.html)
- [compose networking](https://runnable.com/docker/docker-compose-networking)
- [extra](https://success.docker.com/article/Docker_Reference_Architecture-_Designing_Scalable,_Portable_Docker_Container_Networks)
