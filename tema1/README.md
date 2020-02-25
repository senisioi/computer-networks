# Tema 1

## Informații temă
Tema valoarează 10% din punctajul de la laborator. 
Pentru a obtine punctajul, trebuie rezolvata in curs de o saptamana.

## Cerință
1. Instalați [docker](https://docs.docker.com/install/) și [docker-compose](https://docs.docker.com/compose/install/) pe calculatoarele voastre acasă, fie pe windows, linux, dual boot, linux mașină virtuală etc.
2. Rulați în linia de comandă:
```bash
docker ps
docker-compose version
# git clone la repository
cd computer-networks
docker build -t baseimage -f ./docker/Dockerfile-small .
# pe linux folositi ./docker-compose
docker-compose up -d
docker-compose ps
docker-compose down
```

Salvați un print screen cu rezultatul obținut.
