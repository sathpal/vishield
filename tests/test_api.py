"""API contract tests. Uses an in-memory DB, mocked STT and a classifier trained in-process."""

from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from tests.audio_fixtures import synthetic_speechlike, wav_bytes
from vishield.api.app import create_app
from vishield.config import Settings
from vishield.infra.db import Database
from vishield.infra.repository import AnalysisRepository
from vishield.ml.classifier import PhishingClassifier
from vishield.ml.dataset import load_records
from vishield.services.analyzer import AnalysisService
from vishield.stt.mock import MockSpeechToText


@pytest.fixture(scope="module")
def classifier(starter_dataset_path: Path) -> PhishingClassifier:
    records = load_records(starter_dataset_path)
    clf = PhishingClassifier()
    clf.fit([r.text for r in records], [r.label for r in records])
    return clf


@pytest.fixture
def repo() -> AnalysisRepository:
    return AnalysisRepository(Database("sqlite://"))


@pytest.fixture
def client(classifier: PhishingClassifier, repo: AnalysisRepository) -> Iterator[TestClient]:
    settings = Settings(_env_file=None, env="test", max_file_mb=1, max_duration_seconds=10)
    service = AnalysisService(
        settings,
        classifier=classifier,
        stt=MockSpeechToText("This is Example Bank, share the OTP now or your account is blocked"),
        repository=repo,
    )
    app = create_app(settings=settings, service=service)
    with TestClient(app) as c:
        yield c


def test_health(client: TestClient) -> None:
    r = client.get("/health")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] == "ok" and body["model_loaded"] is True and body["stt_backend"] == "mock"


def test_openapi_docs_available(client: TestClient) -> None:
    assert client.get("/docs").status_code == 200
    paths = client.get("/openapi.json").json()["paths"]
    for p in (
        "/health",
        "/analyze/transcript",
        "/analyze/audio",
        "/evaluate/batch",
        "/models/info",
        "/safety/policy",
    ):
        assert p in paths


def test_safety_policy_and_model_info(client: TestClient) -> None:
    policy = client.get("/safety/policy").json()
    assert policy["prohibited_uses"]
    info = client.get("/models/info").json()
    assert info["ml_model_loaded"] is True
    assert info["rule_count"] == 8
    assert info["synthetic_voice_signal_enabled"] is False


def test_analyze_transcript_end_to_end(
    client: TestClient, repo: AnalysisRepository, phishing_text: str
) -> None:
    r = client.post("/analyze/transcript", json={"transcript": phishing_text})
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["risk_level"] in {"medium", "high"}
    assert body["risk_score"] >= 35
    assert body["indicators"]
    assert body["top_features"]
    assert body["components"]["ml_probability"] is not None
    assert "requires human review" in body["explanation"]
    assert body["recommendations"]
    assert body["input_kind"] == "transcript"
    assert repo.count() == 1


def test_legit_transcript_is_low(client: TestClient, legit_text: str) -> None:
    body = client.post("/analyze/transcript", json={"transcript": legit_text}).json()
    assert body["risk_level"] == "low"


def test_transcript_is_redacted_in_response(client: TestClient) -> None:
    text = "Share the OTP 483920 and call 9876543210 or visit http://bad.example/login"
    body = client.post("/analyze/transcript", json={"transcript": text}).json()
    assert "483920" not in body["redacted_transcript"]
    assert "9876543210" not in body["redacted_transcript"]
    assert "http://" not in body["redacted_transcript"]
    assert sum(body["redaction_counts"].values()) >= 3


def test_empty_transcript_rejected(client: TestClient) -> None:
    r = client.post("/analyze/transcript", json={"transcript": "   \n  "})
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "empty_transcript"


def test_missing_field_gives_safe_validation_error(client: TestClient) -> None:
    r = client.post("/analyze/transcript", json={})
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "validation_error"
    assert "transcript" in r.json()["error"]["message"]


def test_analyze_audio_happy_path(client: TestClient) -> None:
    data = wav_bytes(synthetic_speechlike(2.0))
    r = client.post(
        "/analyze/audio",
        files={"file": ("demo.wav", data, "audio/wav")},
        data={"consent_confirmed": "true"},
    )
    assert r.status_code == 200, r.text
    body = r.json()
    assert body["input_kind"] == "audio"
    assert body["acoustic"]["duration_seconds"] > 0
    assert body["components"]["acoustic_score"] is not None
    assert "Example Bank" in body["redacted_transcript"]


def test_audio_requires_consent(client: TestClient) -> None:
    data = wav_bytes(synthetic_speechlike(1.0))
    r = client.post("/analyze/audio", files={"file": ("demo.wav", data, "audio/wav")})
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "audio_consent_required"


def test_audio_invalid_file_rejected(client: TestClient) -> None:
    r = client.post(
        "/analyze/audio",
        files={"file": ("notes.txt", b"hello", "text/plain")},
        data={"consent_confirmed": "true"},
    )
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "audio_bad_extension"


def test_audio_oversized_rejected(client: TestClient) -> None:
    big = b"RIFF" + b"\0" * (1024 * 1024 + 10)
    r = client.post(
        "/analyze/audio",
        files={"file": ("big.wav", big, "audio/wav")},
        data={"consent_confirmed": "true"},
    )
    assert r.status_code == 413
    assert r.json()["error"]["code"] == "audio_too_large"


def test_audio_too_long_rejected(client: TestClient) -> None:
    data = wav_bytes(synthetic_speechlike(12.0))
    r = client.post(
        "/analyze/audio",
        files={"file": ("long.wav", data, "audio/wav")},
        data={"consent_confirmed": "true"},
    )
    assert r.status_code == 422
    assert r.json()["error"]["code"] == "audio_too_long"


def test_batch_evaluate_with_labels(
    client: TestClient, phishing_text: str, legit_text: str
) -> None:
    payload = {
        "items": [
            {"id": "a", "transcript": phishing_text, "label": "phishing"},
            {"id": "b", "transcript": legit_text, "label": "legitimate"},
            {"id": "c", "transcript": "Tell me the OTP immediately", "label": "phishing"},
        ]
    }
    r = client.post("/evaluate/batch", json=payload)
    assert r.status_code == 200, r.text
    body = r.json()
    assert len(body["results"]) == 3
    assert body["metrics"]["labels_present"] is True
    assert body["metrics"]["n"] == 3
    assert body["metrics"]["confusion_matrix"] is not None
    assert body["metrics"]["accuracy"] == 1.0


def test_batch_without_labels_has_no_metrics(client: TestClient, legit_text: str) -> None:
    body = client.post(
        "/evaluate/batch", json={"items": [{"id": "x", "transcript": legit_text}]}
    ).json()
    assert body["metrics"]["labels_present"] is False
    assert body["results"][0]["predicted_label"] == "legitimate"


def test_rules_only_mode_when_model_missing(
    repo: AnalysisRepository, phishing_text: str, tmp_path: Path
) -> None:
    settings = Settings(_env_file=None, env="test", model_path=tmp_path / "missing.joblib")
    service = AnalysisService(settings, stt=MockSpeechToText(), repository=repo)
    app = create_app(settings=settings, service=service)
    with TestClient(app) as c:
        assert c.get("/health").json()["model_loaded"] is False
        body = c.post("/analyze/transcript", json={"transcript": phishing_text}).json()
        assert body["components"]["ml_probability"] is None
        assert body["components"]["weights_used"] == {"rules": 1.0}
        assert body["risk_level"] in {"medium", "high"}


def test_persisted_metadata_has_no_text(client: TestClient, repo: AnalysisRepository) -> None:
    client.post("/analyze/transcript", json={"transcript": "Share the OTP 123456 now, sir"})
    rec = repo.recent(1)[0]
    columns = {c.name for c in rec.__table__.columns}
    assert "transcript" not in columns and "audio" not in columns
    assert rec.transcript_sha256 and rec.risk_level in {"low", "medium", "high"}
    assert repo.level_counts()[rec.risk_level] >= 1


def test_unhandled_error_is_masked(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    service = client.app.state.service  # type: ignore[attr-defined]

    def boom(_: str) -> None:
        raise RuntimeError("secret internal detail 9876543210")

    monkeypatch.setattr(service, "analyze_transcript", boom)
    client_no_raise = TestClient(client.app, raise_server_exceptions=False)
    r = client_no_raise.post("/analyze/transcript", json={"transcript": "hello there"})
    assert r.status_code == 500
    assert "secret" not in r.text and "9876543210" not in r.text
