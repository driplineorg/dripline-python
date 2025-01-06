#! /usr/bin/env bats

@test "ping simple" {
    dl-agent -vv cmd simple -s ping
}

@test "get simple" {
    dl-agent -vv get simple
}

@test "set simple" {
    dl-agent -vv set simple 500
}
