from vishield.domain.models import IndicatorCategory, RiskLevel
from vishield.domain.recommendations import BY_CATEGORY, recommend


def test_low_risk_is_short_and_calm() -> None:
    tips = recommend(RiskLevel.LOW, [])
    assert len(tips) == 2
    assert "stay alert" in tips[0]


def test_high_risk_includes_category_specific_and_reporting() -> None:
    tips = recommend(
        RiskLevel.HIGH, [IndicatorCategory.CREDENTIAL_REQUEST, IndicatorCategory.SECRECY]
    )
    assert BY_CATEGORY[IndicatorCategory.CREDENTIAL_REQUEST] in tips
    assert BY_CATEGORY[IndicatorCategory.SECRECY] in tips
    assert any("Report" in t for t in tips)


def test_no_duplicates() -> None:
    tips = recommend(RiskLevel.MEDIUM, [IndicatorCategory.URGENCY, IndicatorCategory.URGENCY])
    assert len(tips) == len(set(tips))


def test_every_category_has_a_tip() -> None:
    assert set(BY_CATEGORY) == set(IndicatorCategory)
