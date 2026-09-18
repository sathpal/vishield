# Contributing to ViShield

Thank you for helping build a *defensive* awareness tool. Please read `SECURITY.md` and
`docs/ETHICS_AND_SAFETY.md` first; contributions that add offensive capability are rejected.

## Branching model

* `main` – always releasable; protected; merges only from `develop` via pull request.
* `develop` – integration branch; CI must be green.
* Feature branches from `develop`:

  ```
  <type>/<issue-number>-<short-kebab-description>
  feat/23-acoustic-features   fix/41-mp3-decode-error   docs/17-model-card   test/52-batch-api
  ```
  Types: `feat`, `fix`, `docs`, `test`, `chore`, `ci`, `refactor`.

## Workflow

1. Pick an issue (see `.github/ISSUE_PLAN.md`), assign yourself, move it to *In progress*.
2. `git checkout develop && git pull && git checkout -b feat/23-acoustic-features`
3. Write code **and tests**. Keep functions typed and small; add a concise docstring.
4. `make check` – Ruff, mypy strict and pytest must pass. `make format` fixes style.
5. Commit with a clear message: `feat(audio): add pause detection (#23)`.
6. Open a PR against `develop` using the template. Link the issue. Request a review from the
   CODEOWNER of the touched directory **and** one other team member.
7. Address review comments; squash-merge when approved and CI is green.

## Rules that are never relaxed

* No secrets, `.env` files, trained model binaries or audio files in git.
* No real person, organisation, phone number, email address or working URL in code, data, tests
  or docs. Use `Example Bank`, `Sample Delivery`, `[PHONE]`, `example.invalid`.
* New dataset samples must pass `python scripts/validate_dataset.py` and be reviewed by a
  second team member for privacy.
* Speech-to-text stays mocked in tests. Never add a test that downloads a model.
* Every new indicator rule needs at least one positive and one negative test.
* No offensive features: no dialer, no script generator, no voice synthesis, no credential form.

## Code style

* Python 3.11, `from __future__ import annotations`, full type hints, `ruff` (line length 100).
* Layers: `domain` (pure) ← `services` ← `api` / `dashboard`; `audio`, `stt`, `ml`, `infra` are
  adapters. Domain code must not import FastAPI, Streamlit or SQLAlchemy.
* Configuration only through `vishield.config.Settings`; no hard-coded paths or magic numbers.
* Log through `logging`; the redacting filter is installed by `configure_logging`.

## Definition of done

Code + tests + docs updated + CI green + reviewed by two team members + issue closed.
