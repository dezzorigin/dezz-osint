# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial OSINT tool setup with Python framework
- Web scraping utilities for data collection
- Username enumeration capabilities
- IP geolocation tools
- Report generation module

## [1.0-proper] — 2026-11-19 (rantai P1 repo #44)

### Added
- Docs lengkap: `docs/DESIGN.md`, `ARCHITECTURE.md`, `USAGE.md`,
  `TESTING.md`, `DEPLOY.md`, `diagrams.html` (SVG, bukan Mermaid).
- Landing statis etalase (`index.html`, `styles.css`, `app.js`) +
  `favicon.svg` + `og-image.png` — live di Cloudflare Pages
  (https://dezz-osint.pages.dev).
- CI `.github/workflows/ci.yml`: ruff + pytest (perilaku live,
  tanpa mock) + html-validate + gate P0 anti-slop + OSV
  advisory-sweep + Playwright e2e + smoke file deploy.
- `tests/test_cli.py`: 19 tes pytest (CLI, engine, MCP).
- `scripts/advisory-sweep.py`, `scripts/check-static.mjs`,
  `scripts/verify-live.py`, `scripts/make-og-image.py`.
- `.env.example` — semua kunci opsional terdokumentasi
  (`install.sh` sebelumnya gagal karena file ini tidak ada).
- PRD ditulis ulang dari audit kode (v2.0) + README standar.

### Changed
- `requirements.txt` + `pyproject.toml`: dependensi produksi dipin
  `==` (versi terbaru PyPI 19 Nov 2026) agar OSV sweep deterministik.
- `.gitignore`: menutup `*.egg-info/`, `.pytest_cache/`,
  `.ruff_cache/`, `htmlcov/` (sebelumnya build artifact lolos).

### Fixed
- `dezz_osint.egg-info/` yang ter-commit dihapus dari tree
  (build artifact, bukan source).

### Removed
- (Tidak ada penghapusan fitur — semua 14 perintah + 13 tool MCP
  dipertahankan apa adanya.)

### Changed
- Updated Python dependencies to latest security patches
- Improved scraper resilience against anti-bot measures
- Enhanced data validation and cleanup routines
- Refactored code structure for better maintainability

### Fixed
- Fixed rate limiting edge cases in web requests
- Fixed data parsing errors for malformed HTML
- Fixed report generation template issues

### Security
- Updated all dependency versions to latest
- Fixed potential information disclosure bugs
- Added input validation for all user inputs

## [0.1.0] - 2024-08-03

### Added
- Initial OSINT tool setup
- Python framework selection
- Basic scraping utilities
- Report generation module
- Configuration system
