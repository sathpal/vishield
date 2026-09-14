# Observability: metrics to Grafana Cloud

ViShield exposes Prometheus metrics at `GET /metrics`. Everything is an anonymised aggregate:
counts, histograms and gauges. No transcript text, no identifiers, no audio.

```
FastAPI /metrics ──scrape 15s──► Grafana Alloy (Docker) ──OTLP/HTTP──► Grafana Cloud Metrics
                                                                          └─► dashboard "ViShield — Voice Phishing Detection Overview"
```

## Metrics

| Metric | Type | Labels | Meaning |
|---|---|---|---|
| `vishield_analyses_total` | counter | input_kind, risk_level | completed analyses |
| `vishield_processing_seconds` | histogram | input_kind | end-to-end analysis latency |
| `vishield_risk_score` | histogram | input_kind | fused 0–100 score distribution |
| `vishield_rule_score`, `vishield_ml_probability`, `vishield_confidence` | histogram | – | component distributions |
| `vishield_indicators_total` | counter | category | indicator families fired |
| `vishield_redactions_total` | counter | kind | values removed before persistence |
| `vishield_audio_duration_seconds` | histogram | – | analysed audio length |
| `vishield_errors_total` | counter | code | rejected / failed requests |
| `vishield_model_loaded`, `vishield_model_info` | gauge | version, type, stt | model state |
| `vishield_batch_evaluations_total`, `vishield_batch_metric`, `vishield_batch_last_items` | counter / gauge | metric | last labelled batch evaluation |
| `vishield_http_requests_total`, `vishield_http_request_seconds` | counter / histogram | method, route, status | service health |

## Setup

1. `cp observability/.env.example observability/.env` and fill in the Grafana Cloud OTLP
   endpoint, stack id, a Cloud Access Policy token (`metrics:write`) and a service-account
   token (Editor) for the dashboard push. The file is git-ignored.
2. Start the API: `make run-api`.
3. `make observability-up` → Alloy UI at http://localhost:12345 shows the scrape pipeline.
4. `make dashboard` → generates `observability/grafana/vishield.json` and pushes it to the
   folder **ViShield**. Regenerate with the script; never hand-edit the JSON.
5. `make traffic` → replays fictional transcripts for five minutes so panels fill.

## Dashboard rows

Headline stats · Risk outcomes (rate by level, score histogram, level mix) · Explainability
signals (indicator families, rule vs ML medians) · Privacy and quality (redactions, rejections,
last batch metrics) · Service health (requests, status mix, latency percentiles).

The `instance` variable filters by the `VISHIELD_INSTANCE_NAME` label set in `.env`.

## Privacy note

Label cardinality is bounded by design: risk levels (3), indicator categories (8), redaction
kinds (6), error codes (~10), routes (6). Nothing derived from user input becomes a label.
