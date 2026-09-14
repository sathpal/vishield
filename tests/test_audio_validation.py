import pytest

from tests.audio_fixtures import synthetic_speechlike, wav_bytes
from vishield.audio.validation import AudioValidationError, validate_duration, validate_upload
from vishield.config import Settings

S = Settings(_env_file=None, max_file_mb=1)


def test_valid_wav_accepted() -> None:
    data = wav_bytes(synthetic_speechlike(0.5))
    meta = validate_upload("call.wav", "audio/wav", data, S)
    assert meta.extension == ".wav"
    assert meta.size_bytes == len(data)


def test_empty_rejected() -> None:
    with pytest.raises(AudioValidationError) as exc:
        validate_upload("a.wav", "audio/wav", b"", S)
    assert exc.value.code == "empty"


def test_oversized_rejected() -> None:
    with pytest.raises(AudioValidationError) as exc:
        validate_upload("a.wav", "audio/wav", b"RIFF" + b"\0" * (2 * 1024 * 1024), S)
    assert exc.value.code == "too_large"


def test_bad_extension_rejected() -> None:
    with pytest.raises(AudioValidationError) as exc:
        validate_upload("notes.txt", "text/plain", b"hello", S)
    assert exc.value.code == "bad_extension"


def test_bad_mime_rejected() -> None:
    data = wav_bytes(synthetic_speechlike(0.2))
    with pytest.raises(AudioValidationError) as exc:
        validate_upload("a.wav", "application/pdf", data, S)
    assert exc.value.code == "bad_mime"


def test_magic_bytes_mismatch_rejected() -> None:
    with pytest.raises(AudioValidationError) as exc:
        validate_upload("a.mp3", "audio/mpeg", b"RIFF1234WAVEfmt ", S)
    assert exc.value.code == "bad_magic"


def test_path_traversal_in_filename_is_neutralised() -> None:
    data = wav_bytes(synthetic_speechlike(0.2))
    meta = validate_upload("../../etc/passwd.wav", "audio/wav", data, S)
    assert meta.filename == "passwd.wav"


def test_duration_limits() -> None:
    s = Settings(_env_file=None, max_duration_seconds=5, min_duration_seconds=1)
    validate_duration(3.0, s)
    with pytest.raises(AudioValidationError) as long_exc:
        validate_duration(6.0, s)
    assert long_exc.value.code == "too_long"
    with pytest.raises(AudioValidationError) as short_exc:
        validate_duration(0.2, s)
    assert short_exc.value.code == "too_short"
