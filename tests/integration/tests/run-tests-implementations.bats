#! /usr/bin/env bats

@test "ping my_device" {
    dl-agent -vv -b rabbit-broker -u dripline --password-file /dl_pw.txt cmd my_device -s ping
}

@test "get idn" {
    dl-agent -vv -b rabbit-broker -u dripline --password-file /dl_pw.txt get idn
}

@test "get voltage" {
    dl-agent -vv -b rabbit-broker -u dripline --password-file /dl_pw.txt get voltage
}

@test "get idn" {
    dl-agent -vv -b rabbit-broker -u dripline --password-file /dl_pw.txt set voltage 10.1
}
