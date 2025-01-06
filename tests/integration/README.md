# Integration Tests

## Docker Container

This directory contains a Dockerfile that adds a few utilities used in the integration testing to the dripline-python image.
We recommend you tag the image with something like `ghcr.io/driplineorg/dripline-python:[version tag]-test`:

    > docker build --build-arg img_tag=[version tag]-dev -t ghcr.io/driplineorg/dripline-python:[version tag]-test .

## The Tests

The integration tests are specified in `run-tests.sh`.  They're run using the [bats framework](https://bats-core.readthedocs.io/en/stable/index.html). Currently the tests include:

* `dl-agent cmd ping -s simple`
* `dl-agent get simple`
* `dl-agent set simple 500
* `dl-agent cmd ping -s my_store`
* `dl-agent get peaches`
* `dl-agent set peaches 500`

## Run the Tests

You can run the tests directly with `docker compose`:

    > DLPY_IMG_TAG=[image tag] DLCPP_IMG_TAG=[image tag] docker compose -f docker-compose.yaml -f docker-compose-test.yaml -f docker-compose-services.yaml up

Or you can use the convenience script, `do-testing.sh`:

    > ./do-testing.sh [image tag]

Note that the terminal output is suppressed using the `do-testing.sh` script.  Output from the test container will be printed.  Output from the service(s) in use will be printed on error.


## Implementation Notes

* Synchronizing containers
  * Anything using the broker needs to wait until the broker is ready.  This is done using a (Docker) healthcheck.  The health status of the broker is determined by a curl request to the HTTP server that RabbitMQ comes with.  Once it has a healthy status, the DL services start.
  * Sending a request to a service requires that the service is running; so far we wait for one second after the broker is ready, and assume the service will be running.  This could be changed in the future to do something like wait-for-broker.sh except by sending pings to the relevant service.
* To include the test docker-compose extension, add a second -f argument:
    > docker compose -f docker-compose.yaml -f docker-compose-test.yaml up
* Specify the docker image tag by setting an environment variable when you run, e.g.
    > IMG_TAG=[version]-dev docker compose -f docker-compose.yaml up
  * There's a default tag (latest-dev), so if this isn't specified, everything should still run.

