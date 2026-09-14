import pytest

from vishield.domain.models import IndicatorCategory
from vishield.domain.rules import RULES, build_indicators, detect_hits, rule_count, rule_score


def categories(text: str) -> set[IndicatorCategory]:
    return {h.category for h in detect_hits(text)}


def test_rule_count_matches_definition() -> None:
    assert rule_count() == len(RULES) == 8


@pytest.mark.parametrize(
    ("text", "expected"),
    [
        ("You must act immediately, within the next ten minutes", IndicatorCategory.URGENCY),
        ("I am calling from the Example Bank fraud department", IndicatorCategory.AUTHORITY),
        ("Your account will be blocked today", IndicatorCategory.FEAR_THREAT),
        ("Your PC is hacked and has malware", IndicatorCategory.FEAR_THREAT),
        ("Please share the OTP you received", IndicatorCategory.CREDENTIAL_REQUEST),
        ("Please confirm the OTP you just received", IndicatorCategory.CREDENTIAL_REQUEST),
        ("Transfer the money to the safe account", IndicatorCategory.PAYMENT_REQUEST),
        ("Do not tell anyone about this call", IndicatorCategory.SECRECY),
        ("Click the link we sent by SMS", IndicatorCategory.SUSPICIOUS_CONTACT),
        ("Install AnyDesk so I can fix it", IndicatorCategory.REMOTE_ACCESS),
    ],
)
def test_each_category_fires(text: str, expected: IndicatorCategory) -> None:
    assert expected in categories(text)


def test_case_insensitive() -> None:
    assert IndicatorCategory.CREDENTIAL_REQUEST in categories("SHARE THE OTP NOW")


def test_benign_text_has_no_hits(legit_text: str) -> None:
    assert detect_hits(legit_text) == []
    assert rule_score([]) == 0.0


def test_score_is_monotonic_and_bounded(phishing_text: str, legit_text: str) -> None:
    hi = rule_score(detect_hits(phishing_text))
    lo = rule_score(detect_hits(legit_text))
    assert 0.0 <= lo < hi <= 1.0


def test_score_saturates_below_one() -> None:
    text = " ".join(
        [
            "act immediately",
            "calling from the police",
            "account will be blocked",
            "share the OTP",
            "transfer the money",
            "do not tell anyone",
            "click the link",
            "install AnyDesk",
        ]
        * 3
    )
    score = rule_score(detect_hits(text))
    assert 0.9 < score < 1.0


def test_spans_point_at_matched_text(phishing_text: str) -> None:
    for hit in detect_hits(phishing_text):
        assert phishing_text[hit.start : hit.end] == hit.text


def test_indicators_grouped_and_sorted(phishing_text: str) -> None:
    indicators = build_indicators(detect_hits(phishing_text))
    cats = [i.category for i in indicators]
    assert len(cats) == len(set(cats))
    assert all(i.evidence for i in indicators)
    severities = [i.severity for i in indicators]
    assert severities == sorted(severities, reverse=True)


@pytest.mark.parametrize(
    "phrasing",
    [
        "Kindly do the needful and share the OTP at the earliest, sir.",
        "yo just send me the otp real quick, it's urgent",
        "Please provide the one-time password immediately for verification purposes.",
        "Tell me the OTP that you received, do it now.",
    ],
)
def test_fairness_across_phrasing_styles(phrasing: str) -> None:
    """Formal, casual, bureaucratic and terse phrasings should all trigger credential rules."""
    assert IndicatorCategory.CREDENTIAL_REQUEST in categories(phrasing)
