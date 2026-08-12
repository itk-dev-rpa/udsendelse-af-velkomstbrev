# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.5.0] - 2026-08-11

### Changed

- The SQL query now finds the latest move into the city from outside Denmark anywhere in a person's
  move history, instead of only comparing their two latest moves. Moves within the city no longer
  hide the arrival, so the waiting period is determined entirely by the query.
- The queue is now only used to avoid sending a letter twice. Queue elements no longer carry state
  the process depends on, and can be deleted once they are older than `MAX_DAYS_SINCE_ARRIVAL`.
- Merged `sql_query` and `read_data` into a single `get_letter_receivers`, which calculates the date
  range and runs the query.

### Fixed

- Recipients are no longer skipped on the first run where they are found, so a letter can be sent
  the first time the robot sees a person whose waiting period has already passed.
- The previous commune code was read from the current address, which is always Aarhus, so every
  newly found recipient was skipped.

### Removed

- `LOCAL_KOM_KODE`, which is no longer needed now that the query handles moves within the city.

## [1.4.0] - 2026-04-28

### Changed

- Bumped OpenOrchestrator to 3.*
- Switched main.py bootstrap to uv

## [1.3.0] - 26-08-2025

### Added

- Event log sending event on new moves and sent letters.

## [1.2.0]

### Added

- Robot will send a welcome letter even if subject moved again since first move to the city.

## [1.1.1]

### Fixed

- Updated serviceplatformen to v3.

## [1.1.0]

### Added

- Name of recipient is now added to PDF attachment.
- Earliest and latest date of move.
- Check on registration status for Digital Post.

## [1.0.0]

- Initial release

[1.1.1]: https://github.com/itk-dev-rpa/udsendelse-af-velkomstbrev/releases/tag/1.1.1
[1.1.0]: https://github.com/itk-dev-rpa/udsendelse-af-velkomstbrev/releases/tag/1.1.0
[1.0.0]: https://github.com/itk-dev-rpa/udsendelse-af-velkomstbrev/releases/tag/1.0.0
