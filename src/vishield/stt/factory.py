"""Build the configured STT backend."""

from __future__ import annotations

from vishield.config import Settings
from vishield.stt.base import SpeechToText
from vishield.stt.mock import MockSpeechToText
from vishield.stt.whisper_adapter import FasterWhisperSpeechToText


def build_stt(settings: Settings) -> SpeechToText:
    if settings.stt_backend == "whisper":
        return FasterWhisperSpeechToText(
            model_size=settings.whisper_model_size, compute_type=settings.whisper_compute_type
        )
    return MockSpeechToText()
