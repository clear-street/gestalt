# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/)

## Unreleased

## [3.3.6] - 2023-06-11

### Changes
- Removed `retry` decorator usage in `vault.py`
- Invokes `vault_client` calls through `retry_call` instead
- Adds`delay` and `tries` to `Vault` constructor for runtime configuration of `retry_call`
- Sets `delay` default to 60 seconds and `tries` to 5



