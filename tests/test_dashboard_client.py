import pytest

from vishield.config import Settings
from vishield.dashboard.client import ClientError, LocalClient, build_client


def test_build_client_falls_back_to_local_when_api_down() -> None:
    settings = Settings(_env_file=None, api_base_url="http://127.0.0.1:9", database_url="sqlite://")
    client = build_client(settings)
    assert isinstance(client, LocalClient)
    assert "in-process" in client.mode


def test_local_client_maps_errors() -> None:
    client = LocalClient(Settings(_env_file=None, database_url="sqlite://"))
    with pytest.raises(ClientError) as exc:
        client.analyze_transcript("   ")
    assert exc.value.code == "empty_transcript"
    with pytest.raises(ClientError) as exc2:
        client.analyze_audio(b"nope", "x.txt", None)
    assert exc2.value.code == "audio_bad_extension"


def test_local_client_round_trip(phishing_text: str) -> None:
    client = LocalClient(Settings(_env_file=None, database_url="sqlite://"))
    result = client.analyze_transcript(phishing_text)
    assert result.risk_score > 0
    assert client.model_info().rule_count == 8
    assert client.safety_policy().prohibited_uses
