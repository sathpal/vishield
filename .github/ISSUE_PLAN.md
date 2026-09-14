# GitHub milestones and issue plan

Create these with the GitHub UI or `gh`. Labels first, then milestones, then issues.

## Labels

```
phase:1  phase:2  phase:3
component:audio  component:stt  component:ml  component:data  component:api  component:db
component:risk-engine  component:dashboard  component:ci  component:docker
type:feature  type:bug  type:docs  type:test  type:chore
priority:high  priority:medium  priority:low
owner:student1  owner:student2  owner:student3  owner:student4  owner:all
documentation  dependencies  good-first-issue
```

```bash
# example
gh label create "phase:1" --color 0e8a16
gh milestone create "M1: Foundations" --due-date 2026-09-28   # adjust dates to your start
```

## Milestone M1: Foundations (weeks 1–2)

| # | Title | Labels | Owner |
|---|---|---|---|
| 1 | Repository skeleton, pyproject, Makefile, .env.example | phase:1 component:ci type:chore priority:high | student3 |
| 2 | CI: ruff, mypy, pytest, coverage, pip-audit, gitleaks, docker build | phase:1 component:ci priority:high | student3 |
| 3 | Ethics & safety policy doc + in-code policy endpoint | phase:1 documentation priority:high | student4 |
| 4 | Dataset schema + 80 fictional samples | phase:1 component:data priority:high | student2 |
| 5 | Dataset validation script (schema, duplicates, PII, org names) | phase:1 component:data type:test | student2 |
| 6 | Deterministic stratified split script + distribution report | phase:1 component:data | student2 |
| 7 | Redaction module + tests | phase:1 component:risk-engine priority:high | student3 |
| 8 | Rule-based baseline (8 families) + tests | phase:1 component:risk-engine priority:high | student3 |
| 9 | STT survey and adapter interface design | phase:1 component:stt documentation | student1 |
| 10 | Upload validation (extension, MIME, magic, size) | phase:1 component:audio | student1 |
| 11 | Streamlit skeleton with banner and tabs | phase:1 component:dashboard | student4 |
| 12 | SRS, ARCHITECTURE, PROJECT_PLAN drafts | phase:1 documentation | student4 |
| 13 | Literature review: 12 sources summarised | phase:1 documentation | all |

## Milestone M2: Core pipeline (weeks 3–5)

| # | Title | Labels | Owner |
|---|---|---|---|
| 14 | Audio decode + normalise + duration checks | phase:2 component:audio priority:high | student1 |
| 15 | Aggregate acoustic features (pauses, rate, pitch, spectral) | phase:2 component:audio | student1 |
| 16 | Mock STT backend + factory | phase:2 component:stt priority:high | student1 |
| 17 | faster-whisper adapter (optional extra, lazy load) | phase:2 component:stt priority:medium | student1 |
| 18 | TF-IDF + LR classifier with feature attributions | phase:2 component:ml priority:high | student2 |
| 19 | Train script + model metadata + load-failure handling | phase:2 component:ml | student2 |
| 20 | Metrics module (P/R/F1/AUC/confusion) | phase:2 component:ml | student2 |
| 21 | Risk engine fusion + thresholds + confidence | phase:2 component:risk-engine priority:high | student3 |
| 22 | Recommendations module | phase:2 component:risk-engine | student3 |
| 23 | SQLAlchemy models + repository (metadata only) | phase:2 component:db | student3 |
| 24 | Redacting logging filter | phase:2 component:db type:test | student3 |
| 25 | FastAPI endpoints + error handling + contract tests | phase:2 component:api priority:high | student3 |
| 26 | Dashboard result rendering (gauge, cards, spans, features) | phase:2 component:dashboard priority:high | student4 |
| 27 | Dashboard batch evaluation page | phase:2 component:dashboard | student4 |
| 28 | Dashboard model-info and limitations pages | phase:2 component:dashboard | student4 |
| 29 | Fairness tests across phrasing styles | phase:2 type:test | student2 |
| 30 | Dataset card + model card v1 | phase:2 documentation | student2 |

## Milestone M3: Evaluation & delivery (weeks 6–8)

| # | Title | Labels | Owner |
|---|---|---|---|
| 31 | Experimental synthetic-voice signal behind flag | phase:3 component:audio priority:low | student1 |
| 32 | Weight sensitivity study on validation split (E2) | phase:3 component:ml | student2 |
| 33 | Acoustic contribution study (E3) | phase:3 component:audio component:ml | student1, student2 |
| 34 | Phrasing robustness study (E4) | phase:3 component:ml | student2 |
| 35 | Rule improvements from error analysis (digit-code, reward lure) | phase:3 component:risk-engine | student3 |
| 36 | Dockerfile + compose + CI image build | phase:3 component:docker priority:high | student3 |
| 37 | Threat model + security review | phase:3 documentation priority:high | student3 |
| 38 | Test plan execution + coverage ≥ 70 % | phase:3 type:test | all |
| 39 | Demo guide + rehearsal | phase:3 documentation | student4 |
| 40 | Final report draft (outline §1–20) | phase:3 documentation priority:high | student4 (all contribute) |
| 41 | Presentation slides | phase:3 documentation | all |
| 42 | Viva Q&A preparation | phase:3 documentation | all |
| 43 | Release v1.0 tag + release notes | phase:3 type:chore | student3 |

## Board columns

Backlog → Ready → In progress → In review → Done. Cards move only with a linked PR.
