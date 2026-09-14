from pathlib import Path

import pytest

from vishield.ml.dataset import (
    CATEGORIES,
    DatasetRecord,
    class_distribution,
    find_duplicates,
    load_records,
    scan_pii,
    stratified_split,
)


def test_starter_dataset_loads_and_is_balanced(starter_dataset_path: Path) -> None:
    records = load_records(starter_dataset_path)
    assert len(records) == 80
    dist = class_distribution(records)
    assert set(dist["category"]) == set(CATEGORIES)
    assert all(n == 8 for n in dist["category"].values())
    assert dist["label"] == {"legitimate": 24, "phishing": 56}


def test_starter_dataset_has_no_duplicates_or_pii(starter_dataset_path: Path) -> None:
    records = load_records(starter_dataset_path)
    assert find_duplicates(records) == []
    assert scan_pii(records) == []


def test_split_is_deterministic_and_stratified(starter_dataset_path: Path) -> None:
    records = load_records(starter_dataset_path)
    a = stratified_split(records)
    b = stratified_split(records)
    assert [r.id for r in a[2]] == [r.id for r in b[2]]
    train, val, test = a
    assert len(train) + len(val) + len(test) == 80
    assert len(test) == 20 and len(val) == 10 and len(train) == 50
    assert set(r.category for r in test) == set(CATEGORIES)
    assert not ({r.id for r in train} & {r.id for r in test})


def test_label_category_mismatch_rejected() -> None:
    with pytest.raises(ValueError):
        DatasetRecord(
            id="vs-9999",
            text="x" * 30,
            label="phishing",
            category="legit_customer_support",
            language="en",
            source="synthetic",
            license="CC0-1.0",
            consent="not_applicable_synthetic",
        )


def test_consented_requires_reference() -> None:
    with pytest.raises(ValueError):
        DatasetRecord(
            id="vs-9999",
            text="x" * 30,
            label="phishing",
            category="delivery_scam",
            language="en",
            source="consented",
            license="CC-BY-4.0",
            consent="not_applicable_synthetic",
        )


def test_pii_scan_flags_digits_and_real_orgs() -> None:
    bad = DatasetRecord(
        id="vs-9998",
        text="Call 9876543210 now, this is HDFC bank fraud team speaking.",
        label="phishing",
        category="bank_verification_scam",
        language="en",
        source="synthetic",
        license="CC0-1.0",
        consent="not_applicable_synthetic",
    )
    kinds = {i.kind for i in scan_pii([bad])}
    assert {"pii_pattern", "real_organisation"} <= kinds
