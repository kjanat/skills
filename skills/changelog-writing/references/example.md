# Example Changelog

A complete CHANGELOG.md following Keep a Changelog format.

## Template

```markdown
# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

- Dark mode toggle in application settings.
- Export dashboard data as CSV.

### Fixed

- Crash when uploading files larger than 50 MB.

## [2.1.0] - 2025-08-15

### Added

- User profile page with avatar upload.
- Email notification preferences.

### Changed

- Dashboard now loads data lazily for faster initial render.
- Upgrade Node.js runtime from 18 to 20.

### Deprecated

- `GET /api/v1/users` endpoint. Use `GET /api/v2/users` instead.

### Fixed

- Pagination off-by-one error on search results.
- Memory leak in WebSocket connection handler.

## [2.0.0] - 2025-06-01

### Added

- REST API v2 with OpenAPI spec.
- Role-based access control (admin, editor, viewer).

### Changed

- **BREAKING**: Authentication now requires OAuth 2.0. API key auth removed.
- Minimum supported Node.js version is now 18.

### Removed

- Legacy XML export format.
- `GET /api/v1/config` endpoint (use environment variables).

### Security

- Patch CVE-2025-1234: XSS in user bio field.

## [1.0.0] - 2025-01-10

### Added

- Initial public release.
- User authentication with email/password.
- Dashboard with real-time metrics.
- REST API v1.

[Unreleased]: https://github.com/org/repo/compare/v2.1.0...HEAD
[2.1.0]: https://github.com/org/repo/compare/v2.0.0...v2.1.0
[2.0.0]: https://github.com/org/repo/compare/v1.0.0...v2.0.0
[1.0.0]: https://github.com/org/repo/releases/tag/v1.0.0
```

## Key Points in This Example

- **Unreleased section** at top with pending changes
- **Breaking changes** called out with bold `**BREAKING**:` prefix
- **Deprecated** section warns before removal in next major version
- **Security** section for CVE patches
- **Comparison links** at bottom for every version
- **No empty categories** — only categories with entries are shown
- **3 releases** shown — enough to demonstrate the pattern without bloat
