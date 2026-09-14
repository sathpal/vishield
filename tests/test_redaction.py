from vishield.domain.redaction import contains_sensitive, redact


def test_redacts_phone_numbers() -> None:
    result = redact("Call me back on +91 98765 43210 today")
    assert "98765" not in result.text
    assert "[PHONE]" in result.text
    assert result.counts.get("phone", 0) >= 1


def test_redacts_email_and_url() -> None:
    result = redact("Visit https://verify-example.test/login or mail help@example.com")
    assert "https://" not in result.text
    assert "@" not in result.text
    assert result.counts["url"] == 1
    assert result.counts["email"] == 1


def test_redacts_otp_like_values() -> None:
    result = redact("The OTP is 482913, please read it out")
    assert "482913" not in result.text
    assert "[CODE]" in result.text


def test_redacts_account_and_card_numbers() -> None:
    result = redact("Account 123456789012 and card 4111 1111 1111 1111")
    assert "123456789012" not in result.text
    assert "4111" not in result.text
    assert "[ACCOUNT]" in result.text
    assert "[CARD]" in result.text


def test_plain_text_untouched() -> None:
    text = "Hello, this is a normal sentence with two words and no numbers."
    result = redact(text)
    assert result.text == text
    assert result.total == 0
    assert not contains_sensitive(text)


def test_bare_domain_redacted() -> None:
    result = redact("go to secure-bank-login.xyz now")
    assert "secure-bank-login" not in result.text
