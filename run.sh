#! /bin/bash

docker swarm init --advertise-addr 127.0.0.1

docker service create --name registry --publish published=5000,target=5000 registry:2

docker-compose -f stack.yml build

docker stack deploy -c stack.yml sprc3