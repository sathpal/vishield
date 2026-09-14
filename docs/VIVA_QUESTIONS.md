# Viva questions and model answers

**Q1. Why not just use a large language model to judge the call?**
Cost, privacy (audio/transcripts leave the laptop), non-determinism and weak explanations. Our
rules give exact spans and the linear model gives per-token weights, both reproducible offline.

**Q2. Your accuracy is 95 %. Is the system ready for real use?**
No. n = 20 fictional samples; one error is 5 points; the Wilson interval is roughly 0.76–0.99.
The data was written by us, so style leakage inflates results. It is an awareness prototype.

**Q3. How do you prevent the tool from being misused by scammers?**
No generation, no dialing, no voice synthesis; indicators are publicly known tactics; policy in
code (`/safety/policy`), PR checklist, banner; explanations are coarse.

**Q4. Explain the rule score formula.**
Per category: weight × (1 + 0.5·ln(hits)); total passed through 1 − e^(−total/3), so it
saturates smoothly instead of clipping and repeated hits give diminishing returns.

**Q5. Why logistic regression over TF-IDF?**
Strong baseline on short text, convex training, deterministic, and coefficients × tf-idf give
faithful local explanations without a surrogate model.

**Q6. What is "confidence" in your output?**
A transparency heuristic: distance of the score from 50 plus agreement between components. It
is not a calibrated probability, and we say so in every response.

**Q7. How is audio kept private?**
Validated and decoded in memory, resampled, features aggregated, transcribed, then the samples
are discarded. No audio persistence unless a dev flag is set, which production ignores. Logs
pass through a redacting filter; the DB stores only metadata and a hash.

**Q8. What happens if the ML model file is missing or corrupt?**
`load_or_none` logs a warning and the service runs rules-only with weights renormalised to
`{rules: 1.0}`; `/health` reports `model_loaded: false`. Tested.

**Q9. Why is the synthetic-voice detector disabled?**
It is a heuristic on spectral flatness and pitch variance, not a trained anti-spoofing model.
Enabling it by default would invite over-claiming. It is exposed for research only, labelled
experimental in the output.

**Q10. How would you add Hindi or Hinglish?**
Consented or synthetic samples in the schema (`language` field), language-aware tokenisation,
rules with transliterated keywords, and separate per-language evaluation. STT via a
multilingual Whisper model.

**Q11. What is the biggest weakness of the rule engine?**
No negation handling: "we will never ask for your OTP" fires the credential rule. Fusion with
ML and the recommendation wording mitigate; a dependency-parse negation check is future work.

**Q12. How do you ensure reproducibility?**
Fixed seed 42 for splits and training, pinned dependency ranges, deterministic scripts,
metrics written to `reports/metrics.json`, CI on every PR, Docker build trains from data.

**Q13. Which threats did you consider?**
STRIDE table in `docs/THREAT_MODEL.md`: malicious files, path traversal, pickle trust, PII in
logs, DoS via large files or regex, container privileges, supply chain.

**Q14. How does the team split work and ensure everyone codes?**
RACI in `docs/PROJECT_PLAN.md`; every student owns a layer, everyone writes tests and reviews
PRs (CODEOWNERS requires it).

**Q15. What would you do with two more months?**
Consented multilingual dataset with an ethics-approved protocol, calibrated model and
threshold study, negation-aware rules, user study on explanation clarity, transformer
comparison, proper anti-spoofing baseline with ASVspoof-style evaluation.
