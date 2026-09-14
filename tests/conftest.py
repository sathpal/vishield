"""Shared fixtures. Speech-to-text is always mocked; no model downloads happen in tests."""

from __future__ import annotations

import os
from collections.abc import Iterator
from pathlib import Path

import pytest

os.environ.setdefault("VISHIELD_ENV", "test")
os.environ.setdefault("VISHIELD_STT_BACKEND", "mock")
os.environ.setdefault("VISHIELD_DATABASE_URL", "sqlite://")  # in-memory
os.environ.setdefault("VISHIELD_DEV_STORE_AUDIO", "false")

REPO_ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session")
def repo_root() -> Path:
    return REPO_ROOT


@pytest.fixture(scope="session")
def starter_dataset_path(repo_root: Path) -> Path:
    return repo_root / "data" / "starter_dataset.jsonl"


@pytest.fixture
def settings() -> Iterator[object]:
    from vishield.config import get_settings, reset_settings_cache

    reset_settings_cache()
    yield get_settings()
    reset_settings_cache()


PHISHING_SAMPLE = (
    "This is the Example Bank fraud department. Your account will be blocked within thirty "
    "minutes unless you confirm the OTP you just received. Do not tell anyone about this call."
)
LEGIT_SAMPLE = (
    "Hey, are you coming to the study group tonight? We're doing the operating systems "
    "assignment in the library at seven. Bring your laptop."
)


@pytest.fixture
def phishing_text() -> str:
    return PHISHING_SAMPLE


@pytest.fixture
def legit_text() -> str:
    return LEGIT_SAMPLE
