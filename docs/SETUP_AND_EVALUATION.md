# Setup and evaluation guide

Step-by-step instructions to get ViShield running on macOS or Windows and to evaluate it, both
as a machine-learning system (metrics) and as a project deliverable (what reviewers check).
Every command is run from the repository root. No GPU, no API keys and no paid service are
needed; the default speech-to-text backend is a mock, so nothing is downloaded.

Pick one column and stay in it:

| | macOS | Windows (recommended): WSL2 | Windows: native PowerShell |
|---|---|---|---|
| Shell | Terminal (zsh) | Ubuntu terminal inside WSL2 | PowerShell 7 or Windows Terminal |
| `make` targets | yes | yes | no, use the equivalent commands shown below |
| Audio decoding | WAV built in; MP3/M4A via ffmpeg | same | same |
| Docker | Docker Desktop (optional) | Docker Desktop with WSL2 backend (optional) | Docker Desktop (optional) |

WSL2 is recommended on Windows because every `make` target, the Docker workflow and CI behave
exactly as on macOS and Linux. The native PowerShell path works too, but you type the commands
that `make` would run for you.

## 1. Prerequisites

### macOS

```bash
xcode-select --install                 # git and compilers, skip if already installed
brew install python@3.11 ffmpeg        # ffmpeg is optional (MP3/M4A only)
python3.11 --version
```

If you prefer `uv`: `brew install uv && uv python install 3.11`.

### Windows with WSL2

```powershell
wsl --install -d Ubuntu               # once, then reboot and open "Ubuntu" from the Start menu
```

Inside the Ubuntu terminal:

```bash
sudo apt update
sudo apt install -y python3.11 python3.11-venv python3-pip git make libsndfile1 ffmpeg
python3.11 --version
```

Keep the repository inside the Linux file system (for example `~/vishield`), not under
`/mnt/c/...`, or file watching and tests will be slow.

### Windows native (PowerShell)

1. Install Python 3.11 from [python.org](https://www.python.org/downloads/windows/) or
   `winget install Python.Python.3.11`. Tick **Add python.exe to PATH** in the installer.
2. Install Git: `winget install Git.Git`.
3. Optional, for MP3/M4A uploads: `winget install Gyan.FFmpeg`, then open a new terminal.
4. Check: `py -3.11 --version`.

WAV uploads need nothing else; `soundfile` ships its own `libsndfile` on Windows.

## 2. Clone and install

### macOS or WSL2

```bash
git clone https://github.com/sathpal/vishield.git
cd vishield
make setup          # creates .venv, installs the package with dev extras, copies .env.example -> .env
```

If `python3.11` is not on your PATH: `make setup PY=/full/path/to/python3.11`, or `make setup-uv`.

### Windows native

```powershell
git clone https://github.com/sathpal/vishield.git
cd vishield
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e ".[dev]"
Copy-Item .env.example .env
```

If `Activate.ps1` is blocked, run once:
`Set-ExecutionPolicy -Scope CurrentUser RemoteSigned`, then open a new terminal.
With the virtualenv active, every `python`, `pytest`, `ruff` and `uvicorn` below refers to it.

Verify the install (all platforms, virtualenv active on Windows):

```bash
python -c "import vishield; print(vishield.__version__)"
```

On macOS/WSL2 without activating: `.venv/bin/python -c "..."`.

## 3. Build the data and the model

| Step | macOS / WSL2 | Windows native |
|---|---|---|
| Validate dataset and write splits | `make data` | `python scripts\validate_dataset.py` then `python scripts\split_dataset.py` |
| Train the baseline (seconds) | `make train` | `python scripts\train_model.py` |
| Evaluate rules vs ML vs hybrid | `make evaluate` | `python scripts\evaluate_model.py` |

Expected result of the evaluation step (fictional data, n = 20; your numbers must match
exactly because seeds are fixed):

| Detector | Accuracy | Precision | Recall | F1 | ROC-AUC |
|---|---|---|---|---|---|
| Rules only | 0.85 | 1.00 | 0.79 | 0.88 | 0.95 |
| TF-IDF + LR | 0.85 | 0.82 | 1.00 | 0.90 | 0.99 |
| Hybrid | 0.95 | 0.93 | 1.00 | 0.97 | 0.99 |

If the numbers differ, re-run the data step and check that `data/starter_dataset.jsonl` is
unchanged (`git status`).

## 4. Run the app

### macOS or WSL2

```bash
make run         # API on http://localhost:8000, dashboard on http://localhost:8501
```

Or separately in two terminals: `make run-api` and `make run-ui`.

### Windows native (two PowerShell windows, virtualenv active in both)

```powershell
# window 1
uvicorn vishield.api.app:app --reload --port 8000
# window 2
streamlit run src\vishield\dashboard\app.py --server.port 8501
```

### Smoke tests (all platforms)

```bash
curl -s http://localhost:8000/health
```

macOS / WSL2:

```bash
curl -s -X POST http://localhost:8000/analyze/transcript \
  -H 'Content-Type: application/json' \
  -d '{"transcript": "This is your bank. Your account is blocked. Share the OTP now or it will be closed."}' | python -m json.tool
```

Windows PowerShell (its `curl` is an alias, so use `Invoke-RestMethod`):

```powershell
Invoke-RestMethod -Method Post -Uri http://localhost:8000/analyze/transcript `
  -ContentType 'application/json' `
  -Body '{"transcript": "This is your bank. Your account is blocked. Share the OTP now or it will be closed."}' | ConvertTo-Json -Depth 6
```

You should see a high risk score with credential, urgency and authority indicators. Interactive
API docs are at http://localhost:8000/docs.

Dashboard: open http://localhost:8501, choose the **Typed transcript** tab, load the example
`vs-0001` and press **Analyse**. A gauge, indicator cards, highlighted spans and
recommendations should appear.

### Docker alternative (macOS, WSL2 or Windows with Docker Desktop)

```bash
docker compose up --build     # same as: make docker-up
docker compose down -v
```

### Optional: real speech-to-text

```bash
pip install -e ".[stt]"                       # macOS/WSL2: make install-stt
echo VISHIELD_STT_BACKEND=whisper >> .env     # PowerShell: Add-Content .env 'VISHIELD_STT_BACKEND=whisper'
```

The first run downloads the ~150 MB `base` model and runs on CPU.

## 5. Run the quality checks

| Check | macOS / WSL2 | Windows native |
|---|---|---|
| Tests (about 100, under a minute, STT mocked) | `make test` | `pytest` |
| Lint | `make lint` | `ruff check .` |
| Types | `make typecheck` | `mypy` |
| All three, required before every pull request | `make check` | run the three above |
| Coverage report (CI fails below 70 %) | `make test-cov` | `pytest --cov --cov-report=term-missing` |

CI runs the same checks on every push and pull request, plus `pip-audit`, gitleaks secret
scanning and a Docker image build. See `.github/workflows/ci.yml`.

## 6. How to evaluate the system

### 6.1 Automated metrics

The evaluation step scores every item of `data/splits/test.jsonl` with the three detectors and
writes accuracy, precision, recall, F1, ROC-AUC, confusion matrices and per-category accuracy
to `reports/metrics.json`. Thresholds: rules 0.35, ML 0.5, hybrid level medium at 35/100.

Rules for honest evaluation:

* Tune weights and thresholds on `val.jsonl` only. Report `test.jsonl` once, at the end.
* Never edit the dataset to make a metric improve. Add samples through the process in
  `data/README.md` and re-run the data step.
* With n = 20 the 95 % confidence interval on 0.95 accuracy is roughly 0.76 to 0.99. Say so.

### 6.2 Batch evaluation through the API or dashboard

Build the request body from the held-out split, then post it (API running):

```bash
python -c "import json; rows=[json.loads(l) for l in open('data/splits/test.jsonl')]; json.dump({'items': [{'id': r['id'], 'transcript': r['text'], 'label': r['label']} for r in rows]}, open('batch.json','w'))"
```

macOS / WSL2:

```bash
curl -s -X POST http://localhost:8000/evaluate/batch -H 'Content-Type: application/json' -d @batch.json | python -m json.tool | head -40
```

Windows PowerShell:

```powershell
Invoke-RestMethod -Method Post -Uri http://localhost:8000/evaluate/batch -ContentType 'application/json' -InFile batch.json | ConvertTo-Json -Depth 6
```

The response contains a per-item result and a `metrics` block that matches `reports/metrics.json`
for the hybrid detector. The dashboard **Batch** page does the same with a confusion matrix and
a caveat line.

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
Run them before each review and before the demo.

### 6.5 What reviewers check in a pull request

1. Code, tests and docs change together.
2. The quality checks and CI are green.
3. Two approving reviews.
4. The PR template safety checkbox is ticked: no offensive capability, no real personal data.
5. The change can be demonstrated in the dashboard or via the API.

## 7. Troubleshooting

| Symptom | Platform | Fix |
|---|---|---|
| `python3.11: command not found` | macOS/WSL2 | install it (section 1) or pass `PY=` to `make setup` |
| `py : The term 'py' is not recognized` | Windows | reinstall Python with the "py launcher" and PATH options ticked |
| `Activate.ps1 cannot be loaded because running scripts is disabled` | Windows | `Set-ExecutionPolicy -Scope CurrentUser RemoteSigned` |
| `libsndfile` import error | WSL2/Linux | `sudo apt install libsndfile1` |
| MP3/M4A upload rejected as undecodable | all | install ffmpeg or use WAV |
| Dashboard says "in-process fallback" | all | the API is not running; start it |
| `stt_unavailable` error | all | `VISHIELD_STT_BACKEND=whisper` without the `stt` extra; switch back to `mock` |
| Port already in use | macOS/WSL2 | `make run-api PORT_API=8010` or `make run-ui PORT_UI=8511` |
| Port already in use | Windows | change `--port` / `--server.port` in the run commands |
| Model not found, rules-only mode | all | run the train step |
| Everything is slow under WSL2 | Windows | move the clone from `/mnt/c/...` into the Linux home directory |
