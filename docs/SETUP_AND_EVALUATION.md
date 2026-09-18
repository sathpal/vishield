# Setup and evaluation guide

Step-by-step instructions to get ViShield running on a student laptop and to evaluate it, both
as a machine-learning system (metrics) and as a project deliverable (what reviewers check).
Every command below is run from the repository root.

## 1. Prerequisites

| Requirement | Why | Check |
|---|---|---|
| Python 3.11 (3.12 also works) | pinned in `pyproject.toml` | `python3.11 --version` |
| git | clone and pull requests | `git --version` |
| `make` | all commands are Make targets | `make --version` |
| ffmpeg (optional) | decode MP3/M4A; WAV needs nothing | `ffmpeg -version` |
| Docker (optional) | one-command run without a local Python | `docker --version` |

Install Python 3.11 if missing:

```bash
# macOS
brew install python@3.11            # or: brew install uv && uv python install 3.11
# Ubuntu / Debian
sudo apt install python3.11 python3.11-venv libsndfile1 ffmpeg
# Windows: use WSL2 (Ubuntu) and follow the Ubuntu line, or install Python 3.11 from python.org
```

No GPU, no API keys and no paid service are needed. The default speech-to-text backend is a
mock, so nothing is downloaded.

## 2. Clone and install

```bash
git clone https://github.com/sathpal/vishield.git
cd vishield
make setup          # creates .venv, installs the package with dev extras, copies .env.example -> .env
```

If `python3.11` is not on your PATH:

```bash
make setup PY=/full/path/to/python3.11
# or, faster, with uv:
make setup-uv
```

Verify the install:

```bash
.venv/bin/python -c "import vishield; print(vishield.__version__)"
```

## 3. Build the data and the model

```bash
make data        # validates data/starter_dataset.jsonl and writes data/splits/{train,val,test}.jsonl
make train       # trains TF-IDF + logistic regression -> models/tfidf_logreg.joblib (seconds)
make evaluate    # rules vs ML vs hybrid on the held-out test split -> reports/metrics.json
```

Expected result of `make evaluate` (fictional data, n = 20; your numbers must match these
exactly because seeds are fixed):

| Detector | Accuracy | Precision | Recall | F1 | ROC-AUC |
|---|---|---|---|---|---|
| Rules only | 0.85 | 1.00 | 0.79 | 0.88 | 0.95 |
| TF-IDF + LR | 0.85 | 0.82 | 1.00 | 0.90 | 0.99 |
| Hybrid | 0.95 | 0.93 | 1.00 | 0.97 | 0.99 |

If the numbers differ, run `make data` again and check that `data/starter_dataset.jsonl` is
unchanged (`git status`).

## 4. Run the app

```bash
make run         # API on http://localhost:8000, dashboard on http://localhost:8501
```

Or separately in two terminals: `make run-api` and `make run-ui`.

Smoke test the API:

```bash
curl -s http://localhost:8000/health
curl -s -X POST http://localhost:8000/analyze/transcript \
  -H 'Content-Type: application/json' \
  -d '{"transcript": "This is your bank. Your account is blocked. Share the OTP now or it will be closed."}' | python -m json.tool
```

You should see a high risk score with credential, urgency and authority indicators. Interactive
API docs are at http://localhost:8000/docs.

Smoke test the dashboard: open http://localhost:8501, choose the **Typed transcript** tab, load
the example `vs-0001` and press **Analyse**. A gauge, indicator cards, highlighted spans and
recommendations should appear.

### Docker alternative

```bash
make docker-up   # builds the image, trains the model inside it, starts API + dashboard
make docker-down
```

### Optional: real speech-to-text

```bash
make install-stt                             # faster-whisper, CPU int8
echo VISHIELD_STT_BACKEND=whisper >> .env    # first run downloads the ~150 MB base model
```

## 5. Run the quality checks

```bash
make test        # pytest, about 100 tests, under a minute, STT mocked
make lint        # ruff
make typecheck   # mypy --strict
make check       # all three; must be green before every pull request
make test-cov    # coverage report; CI fails below 70 %
```

CI runs the same checks on every push and pull request, plus `pip-audit`, gitleaks secret
scanning and a Docker image build. See `.github/workflows/ci.yml`.

## 6. How to evaluate the system

### 6.1 Automated metrics

`make evaluate` scores every item of `data/splits/test.jsonl` with the three detectors and
writes accuracy, precision, recall, F1, ROC-AUC, confusion matrices and per-category accuracy
to `reports/metrics.json`. Thresholds: rules 0.35, ML 0.5, hybrid level medium at 35/100.

Rules for honest evaluation:

* Tune weights and thresholds on `val.jsonl` only. Report `test.jsonl` once, at the end.
* Never edit the dataset to make a metric improve. Add samples through the process in
  `data/README.md` and re-run `make data`.
* With n = 20 the 95 % confidence interval on 0.95 accuracy is roughly 0.76 to 0.99. Say so.

### 6.2 Batch evaluation through the API or dashboard

```bash
# build the request body from the held-out split, then post it
.venv/bin/python -c "import json; rows=[json.loads(l) for l in open('data/splits/test.jsonl')]; \
json.dump({'items': [{'id': r['id'], 'transcript': r['text'], 'label': r['label']} for r in rows]}, open('batch.json','w'))"
curl -s -X POST http://localhost:8000/evaluate/batch \
  -H 'Content-Type: application/json' -d @batch.json | python -m json.tool | head -40
```

The response contains a per-item result and a `metrics` block that matches `reports/metrics.json`
for the hybrid detector.

The dashboard **Batch** page loads the held-out split, runs it and shows metrics with the
confusion matrix and a caveat line.

### 6.3 Experiments to run and record

| ID | Question | Where to record |
|---|---|---|
| E1 | Baselines on the test split (done) | `docs/EXPERIMENTS.md` |
| E2 | Hybrid weight sensitivity on the validation split | `docs/EXPERIMENTS.md` |
| E3 | Does the acoustic heuristic add anything? | `docs/EXPERIMENTS.md` |
| E4 | Recall across casual, formal and terse phrasing | `docs/EXPERIMENTS.md` |

Each experiment must be reproducible with the exact commands written next to the table.

### 6.4 Manual test cases

`docs/TEST_PLAN.md` lists nine manual dashboard checks (M1 to M9), for example that the ethics
banner is always visible and that the Analyse button stays disabled until consent is ticked.
Run them before each sprint review and before the demo.

### 6.5 What reviewers check in a pull request

1. Code, tests and docs change together.
2. `make check` and CI are green.
3. Two approving reviews.
4. The PR template safety checkbox is ticked: no offensive capability, no real personal data.
5. The change can be demonstrated in the dashboard or via `curl`.

## 7. Troubleshooting

| Symptom | Fix |
|---|---|
| `python3.11: command not found` | install it (section 1) or pass `PY=` to `make setup` |
| `soundfile` or `libsndfile` import error on Linux | `sudo apt install libsndfile1` |
| MP3/M4A upload rejected as undecodable | install ffmpeg or use WAV |
| Dashboard says "in-process fallback" | the API is not running; start `make run-api` |
| `stt_unavailable` error | `VISHIELD_STT_BACKEND=whisper` without `make install-stt`; switch back to `mock` |
| Port already in use | `make run-api PORT_API=8010` or `make run-ui PORT_UI=8511` |
| Model not found, rules-only mode | run `make train` |
