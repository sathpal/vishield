from vishield.domain.safety import ETHICS_BANNER, get_policy


def test_policy_lists_core_prohibitions() -> None:
    p = get_policy()
    joined = " ".join(p.prohibited_uses).lower()
    for word in ("impersonat", "clon", "otp", "phishing scripts", "pstn", "target"):
        assert word in joined
    assert "requires human review" in p.disclaimer or "human review" in p.disclaimer
    assert "ACADEMIC DEFENSIVE PROTOTYPE" in ETHICS_BANNER
