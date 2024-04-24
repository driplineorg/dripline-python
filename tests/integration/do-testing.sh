#! /bin/bash

# Runs the test suite using docker compose
#
# Usage:
#  do-testing.sh [image tag]

# source: https://blog.harrison.dev/2016/06/19/integration-testing-with-docker-compose.html

RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

cleanup () {
  docker compose -p integration kill
  docker compose -p integration rm -f
}
trap 'cleanup ; printf "${RED}Tests Failed For Unexpected Reasons${NC}\n"' HUP INT QUIT PIPE TERM

IMG_TAG=$1 docker compose -p integration -f docker-compose.yaml -f docker-compose-test.yaml build && IMG_TAG=$1 docker compose -p integration -f docker-compose.yaml -f docker-compose-test.yaml up -d

if [ $? -ne 0 ] ; then
  printf "${RED}Docker Compose Failed${NC}\n"
  exit -1
fi

TEST_EXIT_CODE=`docker wait integration-test-1`
docker logs integration-test-1
if [ -z ${TEST_EXIT_CODE+x} ] || [ "$TEST_EXIT_CODE" -ne 0 ] ; then
  docker logs integration-key-value-store-1
  printf "${RED}Tests Failed${NC} - Exit Code: $TEST_EXIT_CODE\n"
else
  printf "${GREEN}Tests Passed${NC}\n"
fi

cleanup

exit $TEST_EXIT_CODE
