# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## develop (unreleased) 2020-12-01

### Bug Fixes
- `fuel_used_gal` output for `Generator` was incorrect for scenarios with `time_steps_per_hour != 1`
- `check_common_outputs` was not testing that outputs of type `list` are both `list`s in the expected and calculated outputs

### Changes
- changed `test_flexible_time_steps` to include an outage
- changed check in `validators.py` from "outage_start_hour and outage_end_hour cannot be the same" to "outage_start_hour must be less than outage_end_hour"
- `outage_start_hour` and `outage_end_hour`  Started the deprecation of `outage_start_hour` and `outage_end_hour` with ...
- new inputs `outage_start_time_step` and `outage_end_time_step` to replace deprecated `outage_start_hour` and `outage_end_hour`. The latter are used as time step indices in the code, so for sub-hourly problems they do not have hourly units. For now `outage_start_hour` and `outage_end_hour` are kept in place to preserve backwards-compatibility. Also note that the new inputs are not zero-indexed.

## First Public Release [1.0.0] - 2020-02-28
### Added
- First release of the REopt API
