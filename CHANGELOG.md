# Changelog
Format updates according to [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
Update version according to [Calendar Versioning](https://calver.org/).

Always place latest update on top.

## [Unreleased]

## [2024.03.0] - 2024-03-07

### Fixed

- explicity convert Windows path separators to Unix, as the sftp-inbox no longer does it automatically

## [2024.02.3] - 2024-02-06

### Removed
- remove leading zero only from first instance, which is always the month number (merge commit)
- remove leading zero only from first instance, which is always the month number

## [2024.02.2] - 2024-02-06

### Removed
- remove leading zero from calver in windows build only (merge commit)
- remove leading zero from calver in windows build only

## [2024.02.1] - 2024-02-06

### Changed
- make it possible to trigger buils using calver (merge commit)
- make it possible to trigger buils using calver

## [2024.02.0] - 2024-02-06

### Changed
- codeql track main
- Update .gitlab-ci.yml file (merge commit)
- Update .gitlab-ci.yml file

## [v0.8.1] - 2024-02-05

### Changed
- bump version to 0.8.1
- bump python 3.10 to 3.11


## [v0.8.0] - 2024-01-22

### Changed
- allow inputting empty password in case ssh key is not encrypted

### Fixed
- fix directory path now takes absolute local path and uploads relative remote path


## [v0.7.3] - 2024-01-11

### Fixed
- fix cli builds for mac and windows

## [v0.7.2] - 2023-12-22

### Added
- add venv to gitignore


### Removed
- remove deprecated functions

## [v0.7.1] - 2023-12-08

### Changed
- Bump paramiko from 3.2.0 to 3.3.1

### Fixed
- fix bug with checking the header on very large files, read first bytes from file instead of reading first bytes from reader, which seemed to read the full file into memory


## [v0.7.0-rc.1] - 2023-07-04

### Changed
- bump to version v0.7.0
- Bump paramiko from 3.1.0 to 3.2.0
- switch to python 3.10

### Added
- sign window exec

## [v0.6.3] - 2023-05-03

### Fixed
- Fix style checks
- Fix windows noconsole bug
- Fix windows noconsole
- Fix release workflow

## [v0.6.2] - 2023-04-27

### Fixed
- Fix windows noconsole bug

## [v0.6.1] - 2023-04-27

### Changed
- Bump paramiko from 3.0.0 to 3.1.0

### Fixed
- compromise fix for windows build: display cmd behind gui app

## [v0.6.0] - 2023-03-03

### Added
- add password authentication back as an option

### Changed
- change gui to only take selected directory like cli, and not full path

## [v0.5.9] - 2023-02-07

### Fixed
- fix nested directory creation [#32](https://gitlab.ci.csc.fi:10022/sds-dev/sd-submit/sda-uploader/issues/32)

### Changed
- unify version across cli and gui for simplicity
- update gitignore for generated python directory

## [v0.5.8] - 2023-02-02

### Changed
- Bump paramiko from 2.12.0 to 3.0.0
- Bump paramiko from 2.11.0 to 2.12.0
- Bump crypt4gh from 1.5 to 1.6
- Bump paramiko from 2.10.4 to 2.11.0
- make some parameters of optional type

### Fixed
- fix deprecated syntax for set-output

## [v0.5.7] - 2022-05-03

### Changed
- bump version
- Bump paramiko from 2.10.3 to 2.10.4
- Bump paramiko from 2.10.1 to 2.10.3

### Fixed
- fix mypy from #bbe77c3

## [v0.5.6] - 2022-03-15

### Changed
- bump versions
- Bump paramiko from 2.9.2 to 2.10.1

### Fixed
- fix deprecation from crypt4gh params

## [v0.5.5] - 2022-02-02

### Changed
- Bump paramiko from 2.9.1 to 2.9.2
- file handling for windows to

### Fixed
- fix permissions logs

## [v0.5.4] - 2022-01-05

### Changed
- Bump paramiko from 2.8.1 to 2.9.1
- Bump paramiko from 2.8.0 to 2.8.1
- Bump paramiko from 2.7.2 to 2.8.0
- update build version
- update release action due to deprecation
- Update setup.py

### Fixed
- correct artifact name
- correct field name for release
- fail_on_unmatched_files to true

## [v0.5.3] - 2021-07-22

### Changed
- simplify ssh connection check with transport

## [v0.5.2] - 2021-07-22

### Changed
- bump patch version
- crypt4gh generate requires new parameter instead of callback
- load rsa key properly
- verify paramiko types with mypy

## [v0.5.1] - 2021-03-16

### Added
- Create dependabot.yml
- Create codeql-analysis.yml
- run style checks on schedule

### Fixed
- fix dependecies
- reject unknown hostname and key

## [v0.5.0] - 2021-03-03

### Added
- add new field for sftp username and make sftp port optional
- attempted fixes for mypy changes
- make the process work and remove some redundant functions

### Changed
- readjust row numbers
- update gui demo and texts

### Removed
- remove redundant password store
- remove password login sftp and user key need

## [v0.4.1] - 2021-01-07

### Added
- add tests for flake8, black formatting and mypy
- add typing to encrypt and sftp packages
- add typing to gui module
- add typing to cli tool
- add description for sda Uploader & upgrade to beta

### Fixed
- fix style formatting

### Changed
- increase patch number

## [v0.4.0] - 2020-12-23

### Changed
- bump feature version
- make private encryption key optional
- small gh actions version bumps
- smaller imports as suggested

## [v0.3.0] - 2020-10-30

### Changed
- adjust requirements text for linux build
- build linux with python
- confirm password on key generation by typing it twice
- disable console from gui
- pull from cscfi dockerhub

### Changed
- update version

## v0.2.0 - 2020-10-27

### Added
- add easier version tagging
- add cli release and refactor naming
- add command line tool
- add sftp key field
- add missing exception
- add os-dependent layout config
- add license

### Changed
- black format, flake8 ignore=E501,W503
- build binary one file
- display module errors in activity log 
- edit file label
- first version of sftp working, beware of spaghetti and unexpected behaviour
- flake8 and black formatting
- get tag in release notes
- make sftp key optional, add support for username+password auth
- make script installable
- make sender public key optional for file decryption
- one line mssage in release body
- rename window title
- return sftp key which worked on test connection instead of re-opening keyfile for actual upload
- split gui class unrelated modules
- test release build
- test if sftp key is rsa or ed25519

### Fixed
- bugfix some names + add more description to release
- fix setup path
- fix pathlib uploading
- fix directory upload
- fix sftp auth

### Removed
- remove console from gui and add linux disclaimer
- remove old commented code, implement config file for saving field values, implement remember password for session

[unreleased]: https://gitlab.ci.csc.fi:10022/sds-dev/sd-submit/sda-uploader/compare/2024.03.0...HEAD
[2024.03.0]: https://gitlab.ci.csc.fi:10022/sds-dev/sd-submit/sda-uploader/compare/2024.02.3...2024.03.0
[2024.02.3]: https://gitlab.ci.csc.fi:10022/sds-dev/sd-submit/sda-uploader/compare/2024.02.2...2024.02.3
[2024.02.2]: https://gitlab.ci.csc.fi:10022/sds-dev/sd-submit/sda-uploader/compare/2024.02.1...2024.02.2
[2024.02.1]: https://gitlab.ci.csc.fi:10022/sds-dev/sd-submit/sda-uploader/compare/2024.02.0...2024.02.1
[2024.02.0]: https://gitlab.ci.csc.fi:10022/sds-dev/sd-submit/sda-uploader/compare/v0.8.1...2024.02.0
[v0.8.1]: https://gitlab.ci.csc.fi:10022/sds-dev/sd-submit/sda-uploader/compare/v0.8.0...v0.8.1
[v0.8.0]: https://gitlab.ci.csc.fi:10022/sds-dev/sd-submit/sda-uploader/compare/v0.7.3...v0.8.0
[v0.7.3]: https://gitlab.ci.csc.fi:10022/sds-dev/sd-submit/sda-uploader/compare/v0.7.2...v0.7.3
[v0.7.2]: https://gitlab.ci.csc.fi:10022/sds-dev/sd-submit/sda-uploader/compare/v0.7.1...v0.7.2
[v0.7.1]: https://gitlab.ci.csc.fi:10022/sds-dev/sd-submit/sda-uploader/compare/v0.7.0...v0.7.1
[v0.7.0]: https://gitlab.ci.csc.fi:10022/sds-dev/sd-submit/sda-uploader/compare/v0.7.0-rc.1...v0.7.0
[v0.7.0-rc.1]: https://gitlab.ci.csc.fi:10022/sds-dev/sd-submit/sda-uploader/compare/v0.6.3...v0.7.0-rc.1
[v0.6.3]: https://gitlab.ci.csc.fi:10022/sds-dev/sd-submit/sda-uploader/compare/v0.6.2...v0.6.3
[v0.6.2]: https://gitlab.ci.csc.fi:10022/sds-dev/sd-submit/sda-uploader/compare/v0.6.1...v0.6.2
[v0.6.1]: https://gitlab.ci.csc.fi:10022/sds-dev/sd-submit/sda-uploader/compare/v0.6.0...v0.6.1
[v0.6.0]: https://gitlab.ci.csc.fi:10022/sds-dev/sd-submit/sda-uploader/compare/v0.5.9...v0.6.0
[v0.5.9]: https://gitlab.ci.csc.fi:10022/sds-dev/sd-submit/sda-uploader/compare/v0.5.8...v0.5.9
[v0.5.8]: https://gitlab.ci.csc.fi:10022/sds-dev/sd-submit/sda-uploader/compare/v0.5.7...v0.5.8
[v0.5.7]: https://gitlab.ci.csc.fi:10022/sds-dev/sd-submit/sda-uploader/compare/v0.5.6...v0.5.7
[v0.5.6]: https://gitlab.ci.csc.fi:10022/sds-dev/sd-submit/sda-uploader/compare/v0.5.5...v0.5.6
[v0.5.5]: https://gitlab.ci.csc.fi:10022/sds-dev/sd-submit/sda-uploader/compare/v0.5.4...v0.5.5
[v0.5.4]: https://gitlab.ci.csc.fi:10022/sds-dev/sd-submit/sda-uploader/compare/v0.5.3...v0.5.4
[v0.5.3]: https://gitlab.ci.csc.fi:10022/sds-dev/sd-submit/sda-uploader/compare/v0.5.2...v0.5.3
[v0.5.2]: https://gitlab.ci.csc.fi:10022/sds-dev/sd-submit/sda-uploader/compare/v0.5.1...v0.5.2
[v0.5.1]: https://gitlab.ci.csc.fi:10022/sds-dev/sd-submit/sda-uploader/compare/v0.5.0...v0.5.1
[v0.5.0]: https://gitlab.ci.csc.fi:10022/sds-dev/sd-submit/sda-uploader/compare/v0.4.1...v0.5.0
[v0.4.1]: https://gitlab.ci.csc.fi:10022/sds-dev/sd-submit/sda-uploader/compare/v0.4.0...v0.4.1
[v0.4.0]: https://gitlab.ci.csc.fi:10022/sds-dev/sd-submit/sda-uploader/compare/v0.3.0...v0.4.0
[v0.3.0]: https://gitlab.ci.csc.fi:10022/sds-dev/sd-submit/sda-uploader/compare/v0.2.0...v0.3.0
