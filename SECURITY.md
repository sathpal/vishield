# Security policy

ViShield is an academic, defensive prototype. It is not hardened for internet exposure and must
be run locally or on a private network during the project.

## Reporting a vulnerability

Do **not** open a public issue. Email the project supervisor and the student maintainers listed
in `.github/CODEOWNERS` with:

* a description of the issue and its impact,
* steps to reproduce (redact any sensitive data),
* the commit hash you tested.

You will receive an acknowledgement within 5 working days. Confirmed issues are fixed on a
`fix/` branch and noted in the release notes.

## Scope

In scope: the FastAPI service, Streamlit dashboard, data-handling code, CI configuration,
Docker image and documentation.

Out of scope: third-party libraries (report upstream), the optional `faster-whisper` model files,
and any deployment configuration you create outside this repository.

## Security controls in the codebase

* Upload validation: extension, MIME type, magic bytes, size (streamed with a hard cap) and
  duration limits; filenames are stripped of paths.
* Audio is processed in memory and discarded. A development-only retention flag exists, is off
  by default, and is ignored when `VISHIELD_ENV=production`.
* Transcripts are redacted before logging, persistence and display; the database stores only
  anonymised metadata and a SHA-256 of the redacted text.
* Centralised exception handling returns generic messages; stack traces go to logs only, through
  a redacting filter.
* No secrets in the repository; configuration via environment variables (`.env` is git-ignored).
* CI runs Ruff, mypy, pytest, `pip-audit`, gitleaks secret scanning and a Docker build.
* The container runs as a non-root user.

## Responsible use

See `docs/ETHICS_AND_SAFETY.md`. The safety policy is also served at `GET /safety/policy`.
