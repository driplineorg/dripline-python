#! /bin/bash

# TODO: remove this install of curl when the dl-py image has curl
#apt-get update && apt-get install -y curl

until curl -u dripline:dripline http://rabbit-broker:15672/api/overview &> /dev/null
do
    echo "Broker is not ready"
    sleep 1
done
echo "############## BROKER IS READY ################"
