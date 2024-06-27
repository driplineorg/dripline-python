#! /usr/bin/env bats

@test "ping simple" {
    dl-agent -vv --auth-file /auths.json cmd simple -s ping
}

@test "get simple" {
    dl-agent -vv --auth-file /auths.json get simple
}

@test "set simple" {
    dl-agent -vv --auth-file /auths.json set simple 500
}

@test "ping my_store" {
    dl-agent -vv --auth-file /auths.json cmd my_store -s ping
}

@test "get peaches" {
    dl-agent -vv --auth-file /auths.json get peaches
}

@test "set peaches" {
    dl-agent -vv --auth-file /auths.json set peaches 500
}