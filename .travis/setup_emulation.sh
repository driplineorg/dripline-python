#!/usr/bin/env bash

echo '{"experimental": true}' | sudo tee -a /etc/docker/daemon.json
echo "docker daemon config should be: `cat /etc/dockerr/daemon.json`"

sudo service docker restart
sudo systemctl restart docker

echo 'checking for docker experimental...'
docker version -f '{{.Server.Experimental}}'

sudo docker run --rm --privileged multiarch/qemu-user-static:register --reset
