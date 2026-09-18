# Dataset card — ViShield starter transcripts v1

**Motivation.** Provide a tiny, safe, fully fictional dataset so the pipeline can be built,
tested and demonstrated without touching real calls.

**Composition.** 80 English transcripts, 10 categories × 8; binary label phishing (56) /
legitimate (24). Mean length ≈ 40 words. Fields per `data/schema.json`: id, text, label,
category, language, source, license, consent, notes.

**Collection process.** Written by the project team from public consumer-protection
descriptions of common scam patterns (bank verification, KYC, OTP, tech support, delivery,
authority threats, urgent payments) and everyday legitimate calls. No recordings, no real
calls, no scraping.

**Entities.** All placeholders: Example Bank, Example Wallet, Example Insurance, Sample
Delivery, Sample Shopping, Demo Telecom, Demo Power, Placeholder Software/Corp, Fictional City
Cyber Cell, Inspector Sample, Officer Example. No digits longer than three characters, no
emails, no URLs.

**Preprocessing.** None stored; the pipeline normalises whitespace and redacts at runtime.
Splits: `data/splits/` (50/10/20, seed 42, stratified by category).

**Validation.** `scripts/validate_dataset.py` — schema, duplicates, PII, real-organisation scan.
Result on v1: 0 issues.

**Uses.** Development, testing, demonstration, coursework evaluation.

**Not suitable for.** Any claim about real-world detection rates; training production systems;
languages other than English; non-Indian-English phrasing conventions.

**Distribution.** CC0-1.0 for the text. Repository is MIT.

**Maintenance.** The data/NLP area owner maintains the dataset. Additions follow `data/README.md` ("Adding
consented samples") and require a privacy review by a second team member.

**Known limitations and biases.**
* Authors wrote both classes → stylistic leakage (e.g. "sir/madam" frequent in scams).
* Legitimate class is smaller; `class_weight="balanced"` mitigates but does not remove bias.
* Several legitimate samples deliberately mention OTP/PIN in a protective sense to test rule
  false positives.
* No code-switching (Hinglish) despite its prevalence in real calls — future work.
