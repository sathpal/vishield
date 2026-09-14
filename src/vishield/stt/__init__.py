"""Speech-to-text adapters behind one Protocol so backends can be swapped freely."""

from vishield.stt.base import SpeechToText, STTUnavailableError, Transcription
from vishield.stt.factory import build_stt

__all__ = ["STTUnavailableError", "SpeechToText", "Transcription", "build_stt"]
