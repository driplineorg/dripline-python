#! /usr/bin/env bats

#setup() {
#    load 'test_helper/bats-support/load'
#    load 'test_helper/bats-assert/load'
#}

@test "ping base" {
    dl-agent -vv cmd dlpy_service -s ping
}

@test "ping my_store" {
    dl-agent -vv cmd my_store -s ping
}

@test "get peaches" {
    dl-agent -vv get peaches
}

@test "set peaches" {
    dl-agent -vv set peaches 500
}

@test "ping alert_consumer" {
    dl-agent -vv cmd alert_consumer -s ping
}

# We don't have a great test available to see that the alert_consumer saw the alert
# For now we'll just test that it's still running with a ping
@test "alert alert_consumer" {
    dl-agent -vv alert an_alert
    dl-agent -vv cmd alert_consumer -s ping
}
