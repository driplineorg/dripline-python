#!/usr/bin/env bash

docker_daemon_conf_file=/etc/docker/daemon.json

set -ex

## initial check of docker config
echo "docker status:"
echo "initial docker daemon config should be: `sudo cat $docker_daemon_conf_file || true`"
docker version -f '{{.Server.Experimental}}'

## update docker config
sudo cat $docker_daemon_conf_file | jq '. + {"experimental": true}' | sudo tee $docker_daemon_conf_file > /dev/null
echo "docker daemon config should be: `sudo cat $docker_daemon_conf_file || true`"

## apply new docker config and check
echo 'restarting docker'
sudo service docker restart
systemctl status docker
docker version -f '{{.Server.Experimental}}'
echo "docker daemon config should now be: `sudo cat $docker_daemon_conf_file || true`"

## register qemu in kernel
sudo docker run --rm --privileged multiarch/qemu-user-static:register --reset

set +ex
