# Integration Tests

## Docker Container

This directory contains a Dockerfile that adds a few utilities used in the integration testing to the dripline-python image.
We recommend you tag the image `ghcr.io/driplineorg/dripline-python:[version tag]-test`:

    > docker build --build-arg img_tag=[version tag]-dev -t ghcr.io/driplineorg/dripline-python:[version tag]-test .


## Run Tests

You can run the tests directly with `docker compose`:

    > IMG_TAG=[image tag] docker compose -f docker-compose.yaml -f docker-compose-test.yaml up

Or you can use the convenience script, `do-testing.sh`:

    > ./do-testing.sh [image tag]


## Notes

* Synchronizing containers
  * Anything using the broker needs to wait until the broker is ready; this is done by running the wait-for-broker.sh script, which sends HTTP requests to the broker to determine if it's running
  * Sending a request to a service requires that the service is running; so far we wait for 1 second after the broker is ready, and assume the service will be running.  This could be changed in the future to do something like wait-for-broker.sh except by sending pings to the relevant service.
* To include the test docker-compose extension, add a second -f argument:
    > docker compose -f docker-compose.yaml -f docker-compose-test.yaml up
* Specify the docker image tag by setting an environment variable when you run, e.g.
    > IMG_TAG=v4.7.0-dev docker compose -f docker-compose.yaml up
  * There's a default tag (latest-dev), so if this isn't specified, everything should still run.

