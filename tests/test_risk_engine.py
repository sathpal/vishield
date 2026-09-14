import pytest

from vishield.domain.models import RiskLevel
from vishield.domain.risk_engine import RiskThresholds, RiskWeights, explain, fuse

W = RiskWeights(rules=0.4, ml=0.5, acoustic=0.1)
T = RiskThresholds(medium=35, high=65)


def test_rules_only_renormalises_to_full_weight() -> None:
    a = fuse(0.8, None, None, W, T)
    assert a.score == 80
    assert a.components.weights_used == {"rules": 1.0}
    assert a.level == RiskLevel.HIGH


def test_weighted_fusion_with_ml() -> None:
    a = fuse(0.2, 0.9, None, W, T)
    expected = round((0.2 * 0.4 + 0.9 * 0.5) / 0.9 * 100)
    assert a.score == expected
    assert a.components.weights_used["ml"] == pytest.approx(0.5 / 0.9, abs=1e-3)


def test_all_three_components() -> None:
    a = fuse(0.5, 0.5, 0.5, W, T)
    assert a.score == 50
    assert a.level == RiskLevel.MEDIUM


@pytest.mark.parametrize(
    ("score_in", "level"),
    [
        (0.0, RiskLevel.LOW),
        (0.34, RiskLevel.LOW),
        (0.35, RiskLevel.MEDIUM),
        (0.64, RiskLevel.MEDIUM),
        (0.65, RiskLevel.HIGH),
        (1.0, RiskLevel.HIGH),
    ],
)
def test_thresholds(score_in: float, level: RiskLevel) -> None:
    assert fuse(score_in, None, None, W, T).level == level


def test_zero_weights_fall_back_to_uniform() -> None:
    a = fuse(1.0, 0.0, None, RiskWeights(0, 0, 0), T)
    assert a.score == 50
    assert a.components.weights_used == {"rules": 0.5, "ml": 0.5}


def test_confidence_bounds_and_agreement() -> None:
    agree = fuse(0.9, 0.9, None, W, T)
    disagree = fuse(0.9, 0.1, None, W, T)
    assert 0.05 <= disagree.confidence <= 0.99
    assert agree.confidence > disagree.confidence


def test_explanation_language_is_cautious() -> None:
    a = fuse(0.7, 0.8, None, W, T, synthetic_voice_score=0.6)
    text = explain(a, [], [])
    assert "requires human review" in text
    assert "experimental" in text
    assert "proof" not in text.split("requires human review")[0] or "not proof" in text
