import numpy as np
import pytest

from tests.audio_fixtures import synthetic_speechlike, wav_bytes
from vishield.audio.features import acoustic_pressure_score, extract_features
from vishield.audio.normalize import DecodeError, decode_bytes, load_and_normalize, normalize
from vishield.audio.synthetic_voice import (
    DisabledSyntheticVoiceDetector,
    HeuristicSyntheticVoiceDetector,
)


def test_decode_and_normalize_wav() -> None:
    raw = synthetic_speechlike(1.5, sr=22_050)
    audio = load_and_normalize(wav_bytes(raw, 22_050), ".wav", 16_000)
    assert audio.sample_rate == 16_000
    assert 0.8 <= audio.duration_seconds <= 1.5  # edge silence is trimmed
    assert np.max(np.abs(audio.samples)) == pytest.approx(0.95, abs=0.02)
    assert audio.samples.dtype == np.float32


def test_stereo_is_downmixed() -> None:
    mono = synthetic_speechlike(0.5)
    stereo = np.stack([mono, mono * 0.5], axis=1)
    samples, sr = decode_bytes(wav_bytes(stereo), ".wav")
    assert samples.ndim == 1
    assert sr == 16_000


def test_garbage_wav_raises_decode_error() -> None:
    with pytest.raises(DecodeError):
        decode_bytes(b"RIFF----WAVEjunkjunkjunk", ".wav")


def test_normalize_handles_silence_and_empty() -> None:
    silent = normalize(np.zeros(16_000, dtype=np.float32), 16_000)
    assert silent.duration_seconds > 0
    empty = normalize(np.zeros(0, dtype=np.float32), 16_000)
    assert empty.duration_seconds == 0


def test_features_are_aggregate_only() -> None:
    audio = normalize(synthetic_speechlike(2.0), 16_000)
    f = extract_features(audio.samples, audio.sample_rate)
    assert 1.5 <= f.duration_seconds <= 2.0
    assert 0 < f.speech_ratio <= 1
    assert f.pause_count >= 1
    assert f.speaking_rate_proxy > 0
    assert f.spectral_centroid_mean > 0
    # every field is a scalar: no arrays, no embeddings
    for value in f.model_dump().values():
        assert value is None or isinstance(value, int | float)


def test_features_on_tiny_input() -> None:
    f = extract_features(np.zeros(100, dtype=np.float32), 16_000)
    assert f.speech_ratio == 0.0 and f.pause_count == 0


def test_pressure_and_synthetic_scores_bounded() -> None:
    audio = normalize(synthetic_speechlike(2.0), 16_000)
    f = extract_features(audio.samples, audio.sample_rate)
    assert 0.0 <= acoustic_pressure_score(f) <= 1.0
    assert 0.0 <= HeuristicSyntheticVoiceDetector().score(f) <= 1.0
    assert DisabledSyntheticVoiceDetector().score(f) == 0.0
