# Architecture

## Layered design

```
┌───────────────────────────┐   ┌────────────────────────────┐
│ Streamlit dashboard       │   │ FastAPI REST API           │   presentation
│ (dashboard/)              │   │ (api/)                     │
└─────────────┬─────────────┘   └──────────────┬─────────────┘
              │ client.py (HTTP or in-process)  │ deps.py
              └────────────────┬────────────────┘
                     ┌─────────▼──────────┐
                     │ AnalysisService    │                      application
                     │ (services/)        │
                     └──┬────┬────┬────┬──┘
        ┌───────────────┘    │    │    └────────────────┐
┌───────▼───────┐  ┌─────────▼──┐ ┌▼──────────┐  ┌──────▼──────┐
│ audio/        │  │ stt/       │ │ ml/       │  │ infra/      │  adapters
│ validate,     │  │ Protocol,  │ │ TF-IDF+LR │  │ SQLite,     │
│ normalise,    │  │ mock,      │ │ metrics   │  │ repository, │
│ features      │  │ whisper    │ │           │  │ logging     │
└───────────────┘  └────────────┘ └───────────┘  └─────────────┘
                     ┌────────────────────────┐
                     │ domain/ (pure Python)  │                  core
                     │ models · redaction ·   │
                     │ rules · risk_engine ·  │
                     │ recommendations ·      │
                     │ safety                 │
                     └────────────────────────┘
```

Dependencies point downward only. `domain/` imports nothing from other layers, so rules,
redaction and fusion are unit-testable with no I/O.

## Request flow (audio)

1. `POST /analyze/audio` → consent flag checked → body read with a hard byte cap.
2. `validate_upload`: extension, MIME, magic bytes, size. `load_and_normalize`: decode
   (soundfile / librosa), resample to 16 kHz, DC-remove, peak-normalise, trim silence.
   `validate_duration`.
3. Optional dev-only retention (off by default, ignored in production).
4. `extract_features` → aggregate `AcousticSummary` (no frames, no embeddings).
5. `SpeechToText.transcribe` → text. Raw samples are dropped.
6. `_analyze_text`: whitespace-normalise → **redact** → rule hits + score + indicators →
   ML probability + feature attributions → acoustic heuristic (+ experimental synthetic score
   if enabled) → `fuse` → `explain` → `recommend`.
7. Anonymised metadata persisted by `AnalysisRepository`; result returned.

Transcript requests enter at step 6.

## Risk engine

`score = Σ wᵢ·sᵢ / Σ wᵢ` over available components (rules always; ML if a model is loaded;
acoustic if audio was supplied). Weights come from settings and are renormalised, and the
weights actually used are returned so the reader can audit the number. Levels: `< medium` →
low, `< high` → medium, else high. Confidence is a documented heuristic (decisiveness +
component agreement), *not* a calibrated probability.

## Replaceable integrations

| Interface | Default | Replace with |
|---|---|---|
| `stt.SpeechToText` | `MockSpeechToText` | `FasterWhisperSpeechToText`, any local/remote STT |
| `ml.transformer_stub.TextProbabilityModel` | `PhishingClassifier` (TF-IDF+LR) | fine-tuned transformer (disabled by default) |
| `audio.synthetic_voice.SyntheticVoiceDetector` | disabled / heuristic | trained anti-spoofing model |
| `infra.db.Database` | SQLite | any SQLAlchemy URL |

## Data model (SQLite `analysis_results`)

analysis_id, created_at, input_kind, model_version, stt_backend, processing_ms, risk_score,
risk_level, confidence, rule_score, ml_probability, acoustic_score, indicator_categories,
redaction_total, transcript_sha256, duration_seconds. **No transcript, no audio, no identifiers.**

## Configuration

`vishield.config.Settings` (pydantic-settings, prefix `VISHIELD_`, `.env` support). Seeds are
fixed (`RANDOM_SEED = 42`). No module reads environment variables directly.

## Observability

`infra/metrics.py` holds a dedicated Prometheus registry. The service records outcome
metrics (analyses by level, score/component histograms, indicators, redactions), the error
handler records rejection codes, and a Starlette middleware records per-route HTTP counts and
latency. `observability/` ships them to Grafana Cloud via Alloy and generates the dashboard.

## Deployment

Single image (`Dockerfile`) runs API by default; `docker-compose.yml` starts API + dashboard
sharing a volume for SQLite. Baseline model is trained at image build time from the committed
fictional dataset so no binaries are versioned.
