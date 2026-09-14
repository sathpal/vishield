import logging
from pathlib import Path

from tests.audio_fixtures import synthetic_speechlike, wav_bytes
from vishield.config import Settings
from vishield.infra.logging import RedactingFilter
from vishield.services.analyzer import AnalysisService
from vishield.stt.mock import MockSpeechToText


def test_logging_filter_redacts_messages() -> None:
    record = logging.LogRecord(
        "x", logging.INFO, "f", 1, "otp is %s call %s", ("123456", "9876543210"), None
    )
    assert RedactingFilter().filter(record)
    assert "123456" not in record.getMessage() and "[CODE]" in record.getMessage()


def test_dev_audio_storage_off_by_default(tmp_path: Path) -> None:
    settings = Settings(_env_file=None, dev_audio_dir=tmp_path / "audio", dev_store_audio=False)
    service = AnalysisService(settings, stt=MockSpeechToText("hello"), load_model=False)
    service.analyze_audio(wav_bytes(synthetic_speechlike(2.5)), "a.wav", "audio/wav")
    assert not (tmp_path / "audio").exists()


def test_dev_audio_storage_when_enabled(tmp_path: Path) -> None:
    settings = Settings(_env_file=None, dev_audio_dir=tmp_path / "audio", dev_store_audio=True)
    service = AnalysisService(settings, stt=MockSpeechToText("hello"), load_model=False)
    service.analyze_audio(wav_bytes(synthetic_speechlike(2.5)), "a.wav", "audio/wav")
    assert len(list((tmp_path / "audio").glob("*.wav"))) == 1


def test_dev_audio_storage_ignored_in_production(tmp_path: Path) -> None:
    settings = Settings(
        _env_file=None, env="production", dev_audio_dir=tmp_path / "audio", dev_store_audio=True
    )
    service = AnalysisService(settings, stt=MockSpeechToText("hello"), load_model=False)
    service.analyze_audio(wav_bytes(synthetic_speechlike(2.5)), "a.wav", "audio/wav")
    assert not (tmp_path / "audio").exists()


def test_synthetic_voice_signal_only_when_enabled(tmp_path: Path) -> None:
    on = Settings(_env_file=None, enable_synthetic_voice_signal=True)
    off = Settings(_env_file=None)
    audio = wav_bytes(synthetic_speechlike(2.0))
    r_on = AnalysisService(on, stt=MockSpeechToText("hi"), load_model=False).analyze_audio(
        audio, "a.wav", None
    )
    r_off = AnalysisService(off, stt=MockSpeechToText("hi"), load_model=False).analyze_audio(
        audio, "a.wav", None
    )
    assert r_on.components.synthetic_voice_score is not None
    assert "experimental" in r_on.explanation
    assert r_off.components.synthetic_voice_score is None
