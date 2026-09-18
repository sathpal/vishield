# Software Requirements Specification — ViShield v0.1

## 1. Introduction

**Purpose.** Specify the functional and non-functional requirements of ViShield, an explainable,
defensive voice-phishing awareness platform built as an academic project.

**Scope.** Analysis of synthetic, public-domain or explicitly consented audio/transcripts;
explainable risk scoring; educational dashboard. Out of scope: telephony, call interception,
voice synthesis, any offensive capability.

**Definitions.** Vishing – voice phishing. STT – speech-to-text. OTP – one-time password.
Indicator – a social-engineering tactic family detected in text.

## 2. Overall description

* **Users**: learners, awareness trainers, evaluators.
* **Environment**: laptop (8 GB RAM, no GPU), Python 3.11, optional Docker.
* **Constraints**: no paid services; no PII persistence; local execution.
* **Assumptions**: inputs are English (v0.1); users have confirmed consent.

## 3. Functional requirements

| ID | Requirement | Priority | Verified by |
|---|---|---|---|
| FR-1 | Accept WAV, MP3, M4A uploads with configurable size and duration limits | Must | `test_audio_validation.py`, `test_api.py` |
| FR-2 | Consent-gated browser recording in the dashboard | Must | manual (DEMO_GUIDE) |
| FR-3 | Validate MIME type, extension, magic bytes, size, duration | Must | `test_audio_validation.py` |
| FR-4 | Normalise audio (mono, 16 kHz, peak-normalised, trimmed) in memory | Must | `test_audio_pipeline.py` |
| FR-5 | Transcribe via a replaceable STT interface (mock + faster-whisper) | Must | `test_stt.py` |
| FR-6 | Accept typed transcripts | Must | `test_api.py` |
| FR-7 | Detect 8 indicator families with transcript spans | Must | `test_rules.py` |
| FR-8 | Train an explainable TF-IDF + LR classifier | Must | `test_classifier.py` |
| FR-9 | Extract non-identifying acoustic statistics | Should | `test_audio_pipeline.py` |
| FR-10 | Experimental synthetic-voice signal, disabled by default | Could | `test_logging_and_service.py` |
| FR-11 | Configurable weighted fusion of rule, ML, acoustic scores | Must | `test_risk_engine.py` |
| FR-12 | Output score 0–100, level, confidence, indicators, spans, explanation, recommendations | Must | `test_api.py` |
| FR-13 | Redact phone/account/email/OTP/URL before persistence and display | Must | `test_redaction.py`, `test_api.py` |
| FR-14 | Never store audio unless dev flag set; ignore flag in production | Must | `test_logging_and_service.py` |
| FR-15 | Individual and batch evaluation modes | Must | `test_api.py` |
| FR-16 | Show confusion matrix, precision, recall, F1, ROC-AUC | Must | `test_classifier.py`, dashboard |
| FR-17 | Record model version, processing time, anonymised metadata | Must | `test_api.py::test_persisted_metadata_has_no_text` |
| FR-18 | Health endpoint and OpenAPI docs | Must | `test_api.py` |
| FR-19 | Prometheus metrics endpoint with anonymised aggregates | Should | `test_metrics.py` |

## 4. Non-functional requirements

| ID | Requirement |
|---|---|
| NFR-1 | Transcript analysis < 500 ms on a laptop CPU (mock STT) |
| NFR-2 | Whole test suite runs in < 60 s without network access |
| NFR-3 | Strict typing (mypy `strict`) and lint clean (Ruff) |
| NFR-4 | ≥ 70 % branch coverage on `src/vishield` excluding the dashboard |
| NFR-5 | No raw audio or unredacted sensitive text in logs or database |
| NFR-6 | Deterministic: fixed seeds for splits and training |
| NFR-7 | Container runs as non-root; image has no secrets or private data |
| NFR-8 | Accessibility: dashboard usable without colour (levels are labelled textually) |

## 5. Interfaces

* REST: see README table and `/docs`.
* Dashboard: Analyze (upload / record / typed), Batch evaluation, Model information, Limitations.
* Data: JSONL matching `data/schema.json`.

## 6. Safety requirements

SR-1 No telephony or messaging integration. SR-2 No impersonation content. SR-3 No voice
cloning. SR-4 No credential capture fields. SR-5 No phishing-script generation. SR-6 Visible
ethics banner in UI and API description. SR-7 Consent confirmation before audio analysis.
