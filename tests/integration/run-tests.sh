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

@test "ping my_store" {
    dl-agent -vv -b rabbit-broker -u dripline --password-file /dl_pw.txt cmd my_store -s ping
}

@test "get peaches" {
    dl-agent -vv -b rabbit-broker -u dripline --password-file /dl_pw.txt get peaches
}

@test "set peaches" {
    dl-agent -vv -b rabbit-broker -u dripline --password-file /dl_pw.txt set peaches 500
}

@test "ping base" {
    dl-agent -vv -b rabbit-broker -u dripline --password-file /dl_pw.txt cmd dlpy_service -s ping
}