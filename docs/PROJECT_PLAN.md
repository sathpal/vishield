# Project plan — ViShield (8 weeks, 4 students)

## Goal

Deliver a runnable, tested, documented academic prototype that explains *why* a call transcript
looks like voice phishing, using only synthetic/consented data and defensive techniques.

## Phases and milestones

| Phase | Weeks | Milestone (GitHub) | Exit criteria |
|---|---|---|---|
| 1 Foundations | 1–2 | `M1: Foundations` | Repo, CI, ethics doc, dataset v1 validated, architecture, UI skeleton, rule baseline with tests |
| 2 Core build | 3–5 | `M2: Core pipeline` | Audio pipeline, STT adapter, ML classifier, API, DB, risk engine, dashboard end-to-end |
| 3 Harden & deliver | 6–8 | `M3: Evaluation & delivery` | Explainability polish, full test plan executed, evaluation report, Docker, CI/CD, report, slides, demo |

## Week-by-week

| Week | Student 1 (audio/STT) | Student 2 (data/NLP/eval) | Student 3 (backend/DB/risk) | Student 4 (UI/docs/demo) | All |
|---|---|---|---|---|---|
| 1 | Survey STT options; audio format constraints | Draft dataset schema + 40 samples; literature list | Repo skeleton, config, CI, Makefile | README, ethics banner, SRS draft | Ethics review meeting; sign consent policy |
| 2 | Upload validation (size/MIME/magic) | Complete 80 samples; validation + split scripts; dataset card | Rule engine + redaction + tests | Streamlit skeleton (tabs, banner); architecture doc | Sprint review 1 |
| 3 | Decoding, normalisation, duration checks | TF-IDF+LR training script, metrics | SQLAlchemy models, repository, logging filter | Result rendering (gauge, cards) | Test writing pairs |
| 4 | Aggregate acoustic features; mock STT | Explanations (feature attributions); fairness tests | FastAPI routes + error handling + contract tests | Batch page, model-info page | Sprint review 2 |
| 5 | faster-whisper adapter (optional) | Hybrid weight tuning on val split | Risk engine fusion, thresholds, recommendations | Limitations page; demo script v1 | Integration day |
| 6 | Synthetic-voice heuristic (flagged experimental) | Evaluation report `reports/metrics.json`, EXPERIMENTS.md | Docker + compose; security review | Test plan execution; user-guide | Threat-model walkthrough |
| 7 | Performance profiling; edge-case tests | Model card; error analysis | CI hardening (audit, secret scan) | Final report draft; slides | Report review |
| 8 | Demo rehearsal | Demo rehearsal | Demo rehearsal | Demo rehearsal; viva prep | Final presentation |

## Responsibility matrix (RACI)

| Area | S1 | S2 | S3 | S4 |
|---|---|---|---|---|
| Audio validation/normalisation/features | **R/A** | C | C | I |
| Speech-to-text adapters | **R/A** | I | C | I |
| Dataset, validation scripts, cards | C | **R/A** | I | C |
| NLP model, evaluation, experiments | I | **R/A** | C | I |
| Rules, redaction, risk engine | C | C | **R/A** | I |
| API, DB, logging, Docker, CI | I | I | **R/A** | C |
| Dashboard | I | C | C | **R/A** |
| Documentation & report | C | C | C | **R/A** |
| Tests | R | R | R | R |
| PR reviews | R | R | R | R |
| Final presentation | R | R | R | R |

R = responsible, A = accountable, C = consulted, I = informed.

## Definition of done (every issue)

Code + tests + docs + `make check` green + CI green + 2 reviews + demo-able.

## Risks

| Risk | Mitigation |
|---|---|
| STT model too slow / large for laptops | Mock backend + typed transcripts; whisper optional |
| Tiny dataset overfits | Report honestly; stratified splits; rules as floor; add consented samples via process |
| Scope creep into offensive features | Safety policy in code; PR template checkbox; supervisor sign-off |
| Team member unavailable | Every area has a C-role backup; shared tests |
| ffmpeg missing on laptops | WAV path needs no ffmpeg; Docker image bundles it |
