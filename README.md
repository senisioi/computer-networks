# 2019-2020 computer networks lab

## Things to Checkout
- [DefCamp](https://def.camp/) the most important annual conference on Hacking & Information Security in Central Eastern Europe
- [Defcon](https://www.defcon.org/) hacker comunity conference
- [ODD](oddweb.org) a space for theoretical discussion and social gatherings of all kinds

## Curs
- [Materiale de curs](http://nlp.unibuc.ro/people/liviu.html#Courses)
- Cursul de [Computer Networks](https://www.youtube.com/watch?v=xKNPTYtTnAo&list=PLfgkuLYEOvGMWvHRgFAcjN_p3Nzbs1t1C), University of Washington

## Înainte de a începe
Pentru acest laborator, vom avea nevoie de:
- [docker](https://docs.docker.com/install/linux/docker-ce/ubuntu/) sau urmați pașii de [aici](https://gist.github.com/senisioi/0d4326775cade99ce2dec41b8d716b04)
- [docker-compose](https://docs.docker.com/compose/install/) - este deja adăugat în acest repository
- după instalarea docker, trebuie să adăugați userul cu care lucrăm în grupul de docker `sudo usermod -aG docker $USER`

## Concepte de bază
Un container (sau serviciu) docker poate fi pornit (în mod asemănător cu o mașină virtuală) cu o imagine cu un sistem de operare. Pentru a construi imaginea explicit, putem folosi [docker build](https://docs.docker.com/engine/reference/commandline/build/). Comanda build utilizează fișierul [./docker/Dockerfile](https://github.com/senisioi/computer-networks/blob/2020/docker/Dockerfile) care definește ce sistem de operare va fi utilizat de container, ce aplicații vor fi pre-instalate și ce useri vor exista pe containerele care rulează acea imagine. 

Comanda [docker-compose up -d](https://docs.docker.com/compose/reference/up/), va citi fișierul [docker-compose.yml](https://github.com/senisioi/computer-networks/blob/2020/docker-compose.yml) din path-ul de unde rulăm comanda și va lansa containere după cum sunt definite în fișier în secțiunea *services*: rt1, rt2, etc..
Containere care sunt configurate să ruleze o imagine dată (în cazul nostru *baseimage*, imaginea construită la pasul anterior) sunt conectate la o rețea (în cazul nostru rețeaua *dmz*) sau și au definite [un mount point](https://unix.stackexchange.com/questions/3192/what-is-meant-by-mounting-a-device-in-linux) local.
Comanda docker-compose pe linux nu se instalează default cu docker, ci trebuie [să o instalăm separat](https://docs.docker.com/compose/install/). În cazul nostru, comanda se găsește chiar în directorul computer-networks, în acest repository. Așa că dacă nu aveți comanda instalată, o puteți rula din acest director folosind calea relativă `./docker-compose`.


## Starting up
```bash
# build the docker image
docker build -t baseimage ./docker/
# start services defined in docker-compose.yml
docker-compose up -d
```


## Comenzi de bază de docker
```bash
# list your images
docker image ls

# stop services
docker-compose down

# see the containers running
docker ps
docker-compose ps

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
- [Compose Networking](https://runnable.com/docker/docker-compose-networking)
- [Designing Scalable, Portable Docker Container Networks](https://success.docker.com/article/Docker_Reference_Architecture-_Designing_Scalable,_Portable_Docker_Container_Networks)
- [Docker Networking Cookbook](https://github.com/TechBookHunter/Free-Docker-Books/blob/2020/book/Docker%20Networking%20Cookbook.pdf)
