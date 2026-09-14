# Demonstration guide (10 minutes)

## Before the demo

```bash
make setup && make data && make train && make evaluate
make run          # API :8000, dashboard :8501
```
Open http://localhost:8501 and http://localhost:8000/docs in two tabs. Have `reports/metrics.json`
open. Keep `VISHIELD_STT_BACKEND=mock` unless faster-whisper is installed and tested.

## Script

| Min | Action | Say |
|---|---|---|
| 0–1 | Show banner and sidebar | "Academic, defensive, no calls, no storage, no phishing generation." |
| 1–3 | Typed transcript → load `vs-0001 · bank_verification_scam` → Analyse | Walk through gauge, four indicator cards, highlighted spans, feature bar chart, recommendations. Stress "requires human review". |
| 3–4 | Load a `legit_personal_conversation` example | Low risk; explain calm recommendations and that absence of indicators ≠ safe. |
| 4–5 | Paste a transcript containing an OTP and a phone number | Show redaction `[CODE]`, `[PHONE]` and redaction counts. |
| 5–6 | Upload tab → tick consent → upload the 2-second synthetic WAV (`make demo-wav` or generate via `tests/audio_fixtures.py`) | Show acoustic summary expander (aggregates only), mock-transcript caption, consent gating. |
| 6–7 | Batch page → held-out split → run | Metrics, confusion matrix, caveat line. |
| 7–8 | Model information page | Weights, thresholds, feature flags, latest metrics. |
| 8–9 | API `/docs` → `/safety/policy` and `/health` | Typed schemas, error envelope, policy in code. |
| 9–10 | Limitations page | Close on honesty: tiny data, regex negation, experimental acoustics. |

## Generating a demo WAV without real voices

```bash
.venv/bin/python -c "from tests.audio_fixtures import *; open('demo.wav','wb').write(wav_bytes(synthetic_speechlike(3.0)))"
```
This is a synthetic tone pattern, so the mock STT text is used. For a spoken demo, record your
own voice reading a *fictional* transcript in the Record tab after ticking consent.

## Fallbacks

* API down → dashboard automatically uses the in-process service (caption changes).
* No ffmpeg → use WAV only.
* Projector colours poor → levels are also written as text.

## Questions to pre-empt

See `docs/VIVA_QUESTIONS.md`.
