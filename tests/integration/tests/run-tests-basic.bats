#! /usr/bin/env bats

@test "ping simple" {
    dl-agent -vv -b rabbit-broker -u dripline --password-file /dl_pw.txt cmd simple -s ping
}

@test "get simple" {
    dl-agent -vv -b rabbit-broker -u dripline --password-file /dl_pw.txt get simple
}

@test "set simple" {
    dl-agent -vv -b rabbit-broker -u dripline --password-file /dl_pw.txt set simple 500
}
