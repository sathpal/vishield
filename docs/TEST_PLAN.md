# Test plan

## Strategy

Test pyramid: many pure unit tests on `domain/`, adapter tests with synthetic fixtures generated
at runtime, API contract tests through `TestClient`, a handful of end-to-end typed-transcript
tests. Speech-to-text is always mocked; no network, no model downloads. `make test` must run in
under a minute on a laptop.

## Coverage map (all in `tests/`)

| Requirement | Test file(s) | Notes |
|---|---|---|
| Redaction of phone/email/URL/account/card/OTP | `test_redaction.py`, `test_api.py::test_transcript_is_redacted_in_response` | over-redaction accepted |
| Each indicator family fires; benign text does not | `test_rules.py` | spans verified against text |
| Rule score bounded, monotone, saturating | `test_rules.py` | |
| Fairness across phrasing styles | `test_rules.py::test_fairness_across_phrasing_styles` | formal/casual/bureaucratic/terse |
| Fusion, renormalisation, thresholds, confidence | `test_risk_engine.py` | |
| Recommendations per category, no duplicates | `test_recommendations.py` | |
| Config defaults safe; threshold ordering | `test_config.py` | |
| Dataset schema, balance, duplicates, PII, split determinism | `test_dataset.py` | runs on committed data |
| Upload validation: empty, oversized, bad ext/MIME/magic, traversal | `test_audio_validation.py` | |
| Decode/normalise, stereo downmix, garbage input, feature aggregates | `test_audio_pipeline.py` | synthetic WAV built in memory |
| STT mock, factory, lazy import, missing dependency, segment mapping | `test_stt.py` | faster-whisper faked |
| Classifier determinism, class separation, explanations, save/load, load failures | `test_classifier.py` | |
| API contract for all six endpoints; error envelope; 413/422/500 | `test_api.py` | |
| Empty transcript, missing field, consent required | `test_api.py` | |
| Model-loading failure → rules-only mode | `test_api.py::test_rules_only_mode_when_model_missing` | |
| Persisted metadata contains no text/audio | `test_api.py::test_persisted_metadata_has_no_text` | |
| Dev audio retention off by default / ignored in production | `test_logging_and_service.py` | |
| Logging filter redacts | `test_logging_and_service.py` | |
| Synthetic-voice signal only when enabled | `test_logging_and_service.py` | |
| Dashboard client fallback and error mapping | `test_dashboard_client.py` | UI itself is manually tested |

## Manual test cases (dashboard)

| ID | Steps | Expected |
|---|---|---|
| M1 | Open dashboard | ethics banner visible on every page |
| M2 | Upload tab → choose WAV without ticking consent | Analyse button disabled |
| M3 | Tick consent, upload 2 s WAV | gauge, transcript, cards, recommendations render |
| M4 | Record tab without consent | recorder disabled |
| M5 | Typed tab → load example `vs-0001` | high risk; credential + fear + authority cards |
| M6 | Typed tab → load a `legit_personal_conversation` example | low risk; calm recommendations |
| M7 | Batch page → held-out split → run | metrics + confusion matrix + caveat text |
| M8 | Model info page | weights, thresholds, flags, latest metrics |
| M9 | Stop API, reload dashboard | caption shows in-process fallback; analysis still works |

## Quality gates

`make check` locally; CI: Ruff, ruff-format, mypy strict, pytest with coverage ≥ 70 %,
dataset validation, pip-audit, gitleaks, Docker build smoke test.

## Current status

2026-09-14: 106 automated tests passing, 92 % branch coverage (dashboard excluded).
