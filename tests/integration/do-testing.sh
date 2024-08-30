#! /bin/bash

# Runs the test suite using docker compose
#
# Usage:
#  do-testing.sh [dl-py image tag] [dl-cpp image tag]

# source: https://blog.harrison.dev/2016/06/19/integration-testing-with-docker-compose.html

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

cleanup () {
  docker compose -p integration kill
  docker compose -p integration rm -f
}
trap 'cleanup ; printf "${RED}Tests Failed For Unexpected Reasons${NC}\n"' HUP INT QUIT PIPE TERM

export DLPY_IMG_TAG=$1 
export DLCPP_IMG_TAG=$2 
docker compose -p integration -f docker-compose.yaml -f docker-compose-test.yaml build
docker compose -p integration -f docker-compose.yaml -f docker-compose-test.yaml up -d

if [ $? -ne 0 ] ; then
  printf "${RED}Docker Compose Failed${NC}\n"
  exit -1
fi

TEST_BASIC_EXIT_CODE=`docker wait integration-test-basic-1`
TEST_CORE_EXIT_CODE=`docker wait integration-test-core-1`

docker logs integration-test-basic-1
docker logs integration-test-core-1

A_TEST_FAILED=0
if [ -z ${TEST_BASIC_EXIT_CODE+x} ] || [ "$TEST_BASIC_EXIT_CODE" -ne 0 ] ; then
  docker logs integration-simple-service-1
  docker logs integration-test-basic-1
  A_TEST_FAILED=1
fi
if [ -z ${TEST_CORE_EXIT_CODE+x} ] || [ "$TEST_CORE_EXIT_CODE" -ne 0 ] ; then
  docker logs integration-test-core-1
  docker logs integration-key-value-store-1
  docker logs integration-alert_consumer-1
  A_TEST_FAILED=1
fi

if [ "$A_TEST_FAILED" -ne 0 ] ; then
  docker logs integration-rabbit-broker-1
  printf "${RED}Tests Failed${NC} - Exit Code: $TEST_EXIT_CODE\n"
else
  printf "${GREEN}Tests Passed${NC}\n"
fi

cleanup

exit $TEST_EXIT_CODE
