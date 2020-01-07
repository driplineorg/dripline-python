#!/usr/bin/env bash

echo "docker status:"
systemctl status docker
echo "initial docker daemon config should be: `sudo cat /etc/docker/daemon.json || true`"

#echo '{"experimental": true}' | sudo tee -a /etc/docker/daemon.json > /dev/null
sudo cat /etc/docker/daemon.json | jq '. + {"experimental": true}' | sudo tee /etc/docker/daemon.json > /dev/null
echo "docker daemon config should be: `sudo cat /etc/docker/daemon.json || true`"

sudo service docker restart
sudo systemctl restart docker
systemctl status docker

echo 'checking for docker experimental...'
docker version -f '{{.Server.Experimental}}'

sudo docker run --rm --privileged multiarch/qemu-user-static:register --reset
