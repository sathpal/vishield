# Experiments log

All numbers are produced by `make evaluate` (`scripts/evaluate_model.py`) on the committed
data and written to `reports/metrics.json`. Nothing here is estimated or copied from elsewhere.

## E1 — Baselines on the v1 fictional test split (2026-09-14)

Setup: dataset v1 (80 samples), split seed 42 → train 50 / val 10 / test 20 (14 phishing,
6 legitimate). Rules threshold 0.35 (= medium risk), ML threshold 0.5, hybrid weights
0.4 / 0.5 (acoustic absent for text).

| Detector | Acc | P | R | F1 | AUC | [[TN,FP],[FN,TP]] |
|---|---|---|---|---|---|---|
| A Rules only | 0.85 | 1.00 | 0.79 | 0.88 | 0.95 | [[6,0],[3,11]] |
| B TF-IDF + LR | 0.85 | 0.82 | 1.00 | 0.90 | 0.99 | [[3,3],[0,14]] |
| H Hybrid | 0.95 | 0.93 | 1.00 | 0.97 | 0.99 | [[5,1],[0,14]] |

Validation (n = 10) for B: accuracy 0.90, precision 0.875, recall 1.0, AUC 1.0.

### Error analysis

Rules (3 false negatives, all subtle phrasing without a bank/threat frame):

* `vs-0022` otp_request_scam — "I need the six digit code that was just texted to you" (rule
  score 0.23). The credential rule expects "OTP/verification code/PIN"; "six digit code" is not
  matched. **Action:** add `\b(?:four|six|eight|\d)[- ]digit (code|number)\b` in v0.2.
* `vs-0024` otp_request_scam — "tell me the verification code sent to you… valid only for the
  next five minutes" (0.33, just under threshold). Only one category fired strongly.
* `vs-0053` urgent_payment_scam — lottery/prize pretext: "pay the tax and courier charge…
  offer expires in fifteen minutes" (0.00). No payment pattern for "pay the tax/charge" and no
  prize-lure family. **Action:** consider a `reward_lure` family.

ML (3 false positives, all legitimate institutional messages):

* `vs-0067` legit_bank_notification (0.54), `vs-0060` legit_customer_support (0.52),
  `vs-0076` legit_personal_conversation (0.56). All hover at the boundary; the model has
  learned "this is X's team" framing as weakly phishing. Top global features include function
  words, confirming the model is data-starved.

Hybrid: one residual false positive (a legitimate message with ML ≈ 0.55 and a small rule
score). Fusion corrects the three rule misses because the ML term is decisive, and corrects two
of the three ML misses because the rule term is zero.

### Interpretation

RQ2 is answered *on this split*: fusion beats either component. With n = 20 the 95 % Wilson
interval for hybrid accuracy 0.95 is roughly 0.76–0.99; the result is encouraging, not
conclusive.

## E2 — Weight sensitivity (to be run in week 5)

Grid over rules weight ∈ {0.2, 0.3, 0.4, 0.5, 0.6}, ML = 1 − rules, on the **validation** split;
pick the best F1, then report test once. Record the table here. Do not tune on test.

## E3 — Acoustic heuristic contribution (week 6)

Generate 10 synthetic-speech demo clips (team's own voices, consent form on file) reading test
transcripts at normal vs. hurried pace. Compare hybrid score with acoustic weight 0 vs 0.1.
Expected outcome: small or no gain; document honestly.

## E4 — Phrasing-style robustness (week 6)

Paraphrase 10 test phishing samples into casual, formal and terse styles; measure rule and ML
recall per style. Feeds the fairness discussion in the report.

## Reproduction

```bash
make data && make train && make evaluate
cat reports/metrics.json
```
