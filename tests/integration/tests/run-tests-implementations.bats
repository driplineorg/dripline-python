#! /usr/bin/env bats

@test "ping my_device" {
    dl-agent -vv cmd my_device -s ping
}

@test "get idn" {
    dl-agent -vv get idn
}

@test "get voltage" {
    dl-agent -vv get voltage
}

@test "set voltage" {
    dl-agent -vv set voltage 10.1
}
