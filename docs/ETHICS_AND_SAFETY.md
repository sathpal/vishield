# Ethics and safety

## Purpose statement

ViShield exists to help people recognise voice-phishing tactics. It is a *defensive awareness*
tool. It must never become a capability for attackers, and it must never treat a real person's
voice or words without consent.

## Hard boundaries (enforced in code, review and policy)

The project **never**:

1. Places, automates or records telephone calls, or connects to PSTN/SIP/VoIP/bulk messaging.
2. Impersonates a real person or organisation (all names in data are placeholders).
3. Clones or imitates a real person's voice, or ships any voice-synthesis code.
4. Collects passwords, OTPs, banking data or credentials (the redactor removes such values even
   from *fictional* text before storage).
5. Generates personalised phishing scripts or pretexts.
6. Targets real individuals.
7. Bypasses consent, authentication or security controls.
8. Contains instructions for running a phishing campaign.
9. Retains raw audio by default.

Every PR includes a safety checklist; `GET /safety/policy` publishes these boundaries; the
dashboard shows a permanent banner.

## Consent and data provenance

* Only synthetic, public-domain, appropriately licensed or **explicitly consented** samples.
* Consent records live outside the repository; the dataset stores an opaque reference only.
* Browser recording requires an affirmative checkbox on every session.
* Audio is processed in memory and discarded; only anonymised metadata is stored.

## Honest communication of results

* Use "potential phishing indicators detected", "this result requires human review",
  "synthetic-voice score is experimental and may be inaccurate".
* Never say "this caller is a scammer" or "this audio is AI-generated".
* Report metrics only from the included test data; state that a small synthetic dataset does
  not prove real-world performance.

## Fairness considerations

Rules and models are trained on Indian-English phrasing (e.g. "kindly do the needful"). The
test suite includes phrasing-style fairness cases (formal, casual, bureaucratic, terse) and the
evaluation script reports per-category accuracy so weaknesses are visible rather than hidden.
Known bias: legitimate messages that *mention* OTPs ("we never ask for your OTP") can trigger
rules; this is documented and left visible as a teaching point.

## Dual-use review

Could the explanations help an attacker avoid detection? The indicators are generic, publicly
documented social-engineering tactics already found in consumer-protection material. The tool
adds no novel attacker capability. This assessment is revisited at each sprint review.

## Responsible disclosure and escalation

Security issues → `SECURITY.md`. Ethical concerns → supervisor; work stops on the affected
feature until resolved.
