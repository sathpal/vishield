# ViShield - academic defensive prototype. No model weights or audio are baked in.
FROM python:3.11-slim AS base

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    VISHIELD_STT_BACKEND=mock \
    VISHIELD_DATABASE_URL=sqlite:////data/vishield.db \
    VISHIELD_MODEL_PATH=/app/models/tfidf_logreg.joblib

RUN apt-get update \
 && apt-get install -y --no-install-recommends libsndfile1 ffmpeg \
 && rm -rf /var/lib/apt/lists/* \
 && useradd --create-home --uid 1000 vishield

WORKDIR /app
COPY pyproject.toml README.md LICENSE ./
COPY src ./src
RUN pip install --upgrade pip && pip install .

COPY data ./data
COPY scripts ./scripts
COPY models/.gitkeep ./models/.gitkeep

# Train the small baseline at build time so the image is self-contained (seconds, deterministic).
RUN python scripts/validate_dataset.py \
 && python scripts/split_dataset.py \
 && python scripts/train_model.py \
 && mkdir -p /data && chown -R vishield:vishield /app /data

USER vishield
EXPOSE 8000 8501
HEALTHCHECK --interval=30s --timeout=5s CMD python -c "import urllib.request;urllib.request.urlopen('http://127.0.0.1:8000/health')" || exit 1
CMD ["uvicorn", "vishield.api.app:app", "--host", "0.0.0.0", "--port", "8000"]
