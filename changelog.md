# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [5.1.0] - 2025-08-26

### Added

- Heartbeat Monitor (implementations.HeartbeatMonitor)
- New logic for how logging is handled by Entities
  - The `log_interval` is now the interval with which an entity's value is checked, not necessarily logged
  - Whether a value is logged at the `log_interval` is controlled by:
    - `max_interval`: if this time is exceeded since the last log entry, then it will be logged; if 0 (default), then logging occurs every `log_interval`
    - `max_absolute_change`: if the value changes by more than this since the last log entry, then it will be logged
    - `max_fractional_change`: if the value changes fractional change is more than this since the last log entry, then it will be logged
  - The field that's checked for the `max_fractional_change` and `max_absolute_change` is given by `check_field`

### Changed

- Methods for sending and receiving messages are moved to the mixin classes core.RequestHandler and core.RequestSender
  to capture how dl-py handles requests for both services and endpoints
- Upgrade dl-cpp to v2.10.6
- Docker build now separates the installation of dependencies into a separate stage

### Fixed

- Postgres syntax
- Application cancelation -- can use ctrl-c or other system signals to cancel an executable
- Alerts exchange not hard-coded in the alerts consumer

## [5.0.1] - 2023-03-05

### Incompatibility

Messages sent with this version of dl-py are not compatible with:
- dl-py v5.0.0 and earlier
- dl-py v5.1.0 and later
- dl-cpp v2.10.3 and earlier
- dl-cpp v2.10.6 and later.
