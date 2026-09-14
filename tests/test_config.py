import pytest

from vishield.config import RANDOM_SEED, Settings


def test_defaults_are_safe() -> None:
    s = Settings(_env_file=None)
    assert s.dev_store_audio is False
    assert s.stt_backend == "mock"
    assert s.enable_synthetic_voice_signal is False
    assert s.max_file_bytes == 10 * 1024 * 1024
    assert RANDOM_SEED == 42


def test_threshold_ordering_enforced() -> None:
    with pytest.raises(ValueError):
        Settings(_env_file=None, risk_medium_threshold=70, risk_high_threshold=60)


def test_env_override(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("VISHIELD_MAX_FILE_MB", "2")
    assert Settings(_env_file=None).max_file_mb == 2
