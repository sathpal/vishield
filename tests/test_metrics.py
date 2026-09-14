from collections.abc import Iterator

import pytest
from fastapi.testclient import TestClient

from vishield.api.app import create_app
from vishield.config import Settings
from vishield.services.analyzer import AnalysisService
from vishield.stt.mock import MockSpeechToText


@pytest.fixture
def client() -> Iterator[TestClient]:
    settings = Settings(_env_file=None, env="test")
    service = AnalysisService(settings, stt=MockSpeechToText(), load_model=False)
    with TestClient(create_app(settings=settings, service=service)) as c:
        yield c


def test_metrics_endpoint_exposes_analysis_counters(client: TestClient, phishing_text: str) -> None:
    client.post("/analyze/transcript", json={"transcript": phishing_text + " call 98765 43210"})
    client.post("/analyze/transcript", json={"transcript": "   "})
    body = client.get("/metrics").text
    assert 'vishield_analyses_total{input_kind="transcript",risk_level=' in body
    assert 'vishield_indicators_total{category="credential_request"}' in body
    assert 'vishield_redactions_total{kind="phone"}' in body
    assert 'vishield_errors_total{code="empty_transcript"}' in body
    assert (
        'vishield_http_requests_total{method="POST",route="/analyze/transcript",status="200"}'
        in body
    )
    assert "vishield_model_loaded 0.0" in body
    assert "vishield_risk_score_bucket" in body


def test_metrics_contain_no_transcript_text(client: TestClient) -> None:
    secret = "zebra-unicorn-phrase"
    client.post("/analyze/transcript", json={"transcript": f"share the otp now {secret}"})
    assert secret not in client.get("/metrics").text


def test_batch_metrics_gauge(client: TestClient, phishing_text: str, legit_text: str) -> None:
    client.post(
        "/evaluate/batch",
        json={
            "items": [
                {"id": "a", "transcript": phishing_text, "label": "phishing"},
                {"id": "b", "transcript": legit_text, "label": "legitimate"},
            ]
        },
    )
    body = client.get("/metrics").text
    assert 'vishield_batch_metric{metric="accuracy"}' in body
    assert "vishield_batch_last_items 2.0" in body
