import sys
import types

import numpy as np
import pytest

from vishield.config import Settings
from vishield.stt import STTUnavailableError, build_stt
from vishield.stt.mock import MockSpeechToText
from vishield.stt.whisper_adapter import FasterWhisperSpeechToText


def test_mock_returns_fixed_text() -> None:
    stt = MockSpeechToText("share the otp now")
    out = stt.transcribe(np.zeros(16_000, dtype=np.float32), 16_000)
    assert out.text == "share the otp now"
    assert out.backend == "mock"
    assert out.segments[0].end == pytest.approx(1.0)


def test_factory_defaults_to_mock() -> None:
    assert isinstance(build_stt(Settings(_env_file=None)), MockSpeechToText)


def test_factory_builds_whisper_without_importing_it() -> None:
    stt = build_stt(Settings(_env_file=None, stt_backend="whisper"))
    assert isinstance(stt, FasterWhisperSpeechToText)
    assert stt._model is None  # construction must be lazy: nothing imported or loaded yet


def test_whisper_missing_dependency_raises_clear_error(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setitem(sys.modules, "faster_whisper", None)  # simulate ImportError
    stt = FasterWhisperSpeechToText()
    with pytest.raises(STTUnavailableError, match="not installed"):
        stt.transcribe(np.zeros(16_000, dtype=np.float32), 16_000)


def test_whisper_adapter_maps_segments(monkeypatch: pytest.MonkeyPatch) -> None:
    class FakeSeg:
        def __init__(self, s: float, e: float, t: str) -> None:
            self.start, self.end, self.text = s, e, t

    class FakeInfo:
        language = "en"

    class FakeModel:
        def __init__(self, *a: object, **k: object) -> None:
            pass

        def transcribe(self, samples: object, **k: object) -> tuple[list[FakeSeg], FakeInfo]:
            return [FakeSeg(0, 1, " hello "), FakeSeg(1, 2, "share the otp")], FakeInfo()

    fake_module = types.SimpleNamespace(WhisperModel=FakeModel)
    monkeypatch.setitem(sys.modules, "faster_whisper", fake_module)
    stt = FasterWhisperSpeechToText(model_size="tiny")
    out = stt.transcribe(np.zeros(32_000, dtype=np.float32), 16_000)
    assert out.text == "hello share the otp"
    assert out.language == "en"
    assert len(out.segments) == 2


def test_whisper_rejects_wrong_sample_rate() -> None:
    with pytest.raises(ValueError):
        FasterWhisperSpeechToText().transcribe(np.zeros(100, dtype=np.float32), 8_000)
