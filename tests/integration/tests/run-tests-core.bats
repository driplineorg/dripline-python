#! /usr/bin/env bats

#setup() {
#    load 'test_helper/bats-support/load'
#    load 'test_helper/bats-assert/load'
#}

#disabled() {
@test "ping base" {
    dl-agent -vv -b rabbit-broker -u dripline --password-file /dl_pw.txt cmd dlpy_service -s ping
}

#disabled() { 
@test "ping my_store" {
    dl-agent -vv -b rabbit-broker -u dripline --password-file /dl_pw.txt cmd my_store -s ping
}

#disabled() {
@test "get peaches" {
    dl-agent -vv -b rabbit-broker -u dripline --password-file /dl_pw.txt get peaches
}

#disabled() {
@test "set peaches" {
    dl-agent -vv -b rabbit-broker -u dripline --password-file /dl_pw.txt set peaches 500
}

@test "ping alert_consumer" {
    dl-agent -vv -b rabbit-broker -u dripline --password-file /dl_pw.txt cmd alert_consumer -s ping
}

@test "alert alert_consumer" {
    dl-agent -vv -b rabbit-broker -u dripline --password-file /dl_pw.txt alert an_alert
}
