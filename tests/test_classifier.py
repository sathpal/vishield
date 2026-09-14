from pathlib import Path

import pytest

from vishield.ml.classifier import ModelLoadError, PhishingClassifier, load_or_none
from vishield.ml.dataset import load_records, stratified_split
from vishield.ml.evaluate import compute_metrics


@pytest.fixture(scope="module")
def trained(starter_dataset_path: Path) -> tuple[PhishingClassifier, list, list]:
    records = load_records(starter_dataset_path)
    train, _val, test = stratified_split(records)
    clf = PhishingClassifier()
    clf.fit([r.text for r in train], [r.label for r in train])
    return clf, train, test


def test_training_is_deterministic(starter_dataset_path: Path) -> None:
    records = load_records(starter_dataset_path)
    train, _, _ = stratified_split(records)
    a, b = PhishingClassifier(), PhishingClassifier()
    for clf in (a, b):
        clf.fit([r.text for r in train], [r.label for r in train])
    assert a.predict_proba("share the otp now") == pytest.approx(
        b.predict_proba("share the otp now")
    )


def test_probabilities_separate_classes(
    trained: tuple, phishing_text: str, legit_text: str
) -> None:
    clf, _, _ = trained
    assert clf.predict_proba(phishing_text) > 0.5 > clf.predict_proba(legit_text)


def test_test_split_metrics_are_reasonable(trained: tuple) -> None:
    """Sanity bound only; the real numbers are reported by scripts/evaluate_model.py."""
    clf, _, test = trained
    scores = clf.predict_proba_batch([r.text for r in test])
    preds = ["phishing" if s >= 0.5 else "legitimate" for s in scores]
    m = compute_metrics([r.label for r in test], preds, scores)
    assert m.n == 20
    assert m.accuracy is not None and m.accuracy >= 0.7
    assert m.roc_auc is not None and m.roc_auc >= 0.7
    assert m.confusion_matrix is not None and len(m.confusion_matrix) == 2


def test_explanations_reference_present_tokens(trained: tuple, phishing_text: str) -> None:
    clf, _, _ = trained
    feats = clf.explain(phishing_text, top_k=5)
    assert feats
    lowered = phishing_text.lower()
    for f in feats:
        assert f.feature.split(" ")[0] in lowered
        assert f.direction in {"phishing", "legitimate"}


def test_single_class_training_rejected() -> None:
    with pytest.raises(ValueError):
        PhishingClassifier().fit(["a b c d", "e f g h"], ["phishing", "phishing"])


def test_save_and_load_roundtrip(trained: tuple, tmp_path: Path) -> None:
    clf, _, _ = trained
    path = tmp_path / "m.joblib"
    clf.save(path)
    loaded = PhishingClassifier.load(path)
    assert loaded.predict_proba("share the otp") == pytest.approx(
        clf.predict_proba("share the otp")
    )
    assert loaded.metadata.n_train == clf.metadata.n_train


def test_model_loading_failures(tmp_path: Path) -> None:
    with pytest.raises(ModelLoadError):
        PhishingClassifier.load(tmp_path / "missing.joblib")
    corrupt = tmp_path / "corrupt.joblib"
    corrupt.write_bytes(b"not a joblib file")
    with pytest.raises(ModelLoadError):
        PhishingClassifier.load(corrupt)
    assert load_or_none(corrupt) is None


def test_metrics_degenerate_inputs() -> None:
    assert compute_metrics([], []).n == 0
    m = compute_metrics(["phishing", "phishing"], ["phishing", "legitimate"], [0.9, 0.2])
    assert m.roc_auc is None  # single true class -> AUC undefined
    assert m.recall == 0.5
