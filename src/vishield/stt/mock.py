"""Deterministic mock backend for tests, CI and low-resource demos."""

from __future__ import annotations

import numpy as np
from numpy.typing import NDArray

from vishield.stt.base import Transcription, TranscriptSegment


class MockSpeechToText:
    """Returns a fixed transcript regardless of audio content.

    The default text is intentionally benign so a mis-configured deployment never produces
    alarming output by accident.
    """

    name = "mock"

    def __init__(self, fixed_text: str = "") -> None:
        self.fixed_text = fixed_text

    def transcribe(self, samples: NDArray[np.float32], sample_rate: int) -> Transcription:
        duration = float(len(samples)) / sample_rate if sample_rate else 0.0
        text = self.fixed_text or (
            "[mock transcript] Speech-to-text backend is set to 'mock'. Use the typed-transcript "
            "mode or install the whisper extra for real transcription."
        )
        return Transcription(
            text=text,
            backend=self.name,
            language="en",
            segments=[TranscriptSegment(start=0.0, end=duration, text=text)],
        )
