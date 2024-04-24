#! /usr/bin/env bats

@test "ping my_store" {
    dl-agent -vv --auth-file /auths.json cmd my_store -s ping
}

@test "get peaches" {
    dl-agent -vv --auth-file /auths.json get peaches
}

@test "set peaches" {
    dl-agent -vv --auth-file /auths.json set peaches 500
}