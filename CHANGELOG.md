# Changelog
***
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/)

## [3.4.2] - 2024-08-05

### Fixed
- Adding logic to check when the token is about to expire to re-connect. This fix cases for services that are running longer that token's ttl without restarting. Causing requests to get a Permission denied error.  


## [3.4.1] - 2024-07-12

### Fixed
- Returning Raw string instead of parsing. This fixes the case where secret has \\$ in - Python would return \$ - therefore we are calling repr 

## [3.4.0] - 2024-03-04

### Added
- Lazily authenticates to vault upon first vault request, instead of authentication on object creation.

## [3.3.6] - 2023-06-11

### Added
- `delay` and `tries` to `Vault` constructor for runtime configuration of `retry_call`
- `delay` default to 60 seconds and `tries` to 5
- Changelog.md

### Changed
- Removed `retry` decorator usage in `vault.py`
- Invokes `vault_client` calls through `retry_call` instead


## 3.3.5 - 2023-12-08

### Added
- Vault request timeouts as a retry-able exception type for the vault provider.

## 3.3.4 - 2023-10-19

### Fixed
- Nested key plus default bug
- README.md spelling changes

## 3.3.3 - 2023-10-17

### Fixed
- Vault Thread for dynamic workers pool had memory leaks, this is gargbage collected now.

## 3.3.2 - 2023-08-02

### Updated
- PyYaml version to v6.0.1 to address cython 3 compatibility issues

## 3.3.1 - 2023-07-06
### Updated
- Removed async usage throughout the project

## 3.3.0 - 2023-06-21
### Added 
- Vault Response Caching in the provider with a TTL
- Dispatch to get interpolated scheme instead of 

### Changed
- Moved pytest fixtures into a dedicated conftest.py

## 3.2.0 - 2023-06-01
### Added
- Support for other non-standard database for vault plugin with un-nested data response

## 3.1.1 - 2023-01-27
### Added
- TTL Renew threads handled gracefully by stopping the deamon thread

## 3.1.0 - 2022-12-04
### Changed
- Codecov bumped to 2.0.16
- Vault Retry Logic
- Renew TTL Token testing

### Fixed
- Requirements.test.txt correctly gets used

## 3.0.0 - 2022-05-20
### Fixed
- Nested Config Override in gestalt by merging the dictionaries properly
- Exposes new public functions for merging a dictionary into another one using `merge_into`

## 2.0.3 - 2021-09-14
### Added
- Interpolation of providers such as Vault on `set` method in gestalt

## 2.0.2 - 2021-08-12
### Updated
- PyYaml version updated to v5.4.1

## 2.0.1 - 2021-08-11
### Fixed
- Packaging of gestalt

## 2.0.0 - 2021-08-05
### Added
- Vault Provider
- Abstract Base for remote (3rd) party providers

### Updated
- Calls to hvac.Client
- vault_client initialization is now done using the new method of hvac
- Vault Provider code refactoring
- README.md documentation
- GitHub Actions improved for Python

### Fixed 
- Generic Exceptions raised as RuntimeError

## 1.0.9 - 2021-06-15
### Updated
- Exception Handling for Vault

## 1.0.8 - 2021-06-03
### Added
- Support for Vault Mount Path

## 1.0.7 - 2021-05-11
### Updated
- Vault Secret Fetching refactoring
- Secret Fetching converted to public method

## 1.0.6 - 2021-04-26
### Added
- Vault support to Gestalt as a non breaking change

## 1.0.5 - 2020-05-18
**NOTE: This can be a potential breaking change depending on how glob.glob() works on your system.**

### Fixed
- Files are now globbed and sorted before loading to ensure deterministic order. 
- File extension checking for config

### Added
- Capability to load a single config file

## 1.0.4 - 2020-03-29
### Updated
- CVE Update for PyYaml

## 1.0.3 - [VERSION MISSED]

## 1.0.2 - 2020-01-15
### Fixed
- Fixing build issues

## 1.0.0 - 2020-01-06
### Added
- Initial Release

