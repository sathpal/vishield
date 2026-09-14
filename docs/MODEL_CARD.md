# Model card — ViShield hybrid detector `hybrid-0.1.0`

**Model details.** Three-part pipeline: (A) rule engine, 8 families, 27 regex patterns;
(B) scikit-learn TF-IDF(1–2 gram, sublinear tf, ≤ 20 k features) + LogisticRegression
(C = 2, class_weight = balanced, seed 42), 1 760 features on v1 data; (H) weighted fusion
0.4 rules / 0.5 ML / 0.1 acoustic (renormalised over available components). Trained in
seconds on CPU. Owner: Student 2 (ML), Student 3 (fusion).

**Intended use.** Educational demonstration of explainable vishing indicators on consented or
synthetic inputs. Output is an aid for human review.

**Out-of-scope use.** Automated blocking, law-enforcement evidence, deciding whether a real
caller is a criminal, deepfake verdicts, any language other than English.

**Training data.** `data/splits/train.jsonl` (50 fictional samples). See DATASET_CARD.

**Evaluation data.** `data/splits/test.jsonl` (20 samples: 14 phishing, 6 legitimate).

**Metrics (2026-09-14, `make evaluate`).**

| Detector | Acc | P | R | F1 | AUC | Confusion [[TN,FP],[FN,TP]] |
|---|---|---|---|---|---|---|
| Rules only | 0.85 | 1.00 | 0.79 | 0.88 | 0.95 | [[6,0],[3,11]] |
| TF-IDF + LR | 0.85 | 0.82 | 1.00 | 0.90 | 0.99 | [[3,3],[0,14]] |
| Hybrid | 0.95 | 0.93 | 1.00 | 0.97 | 0.99 | [[5,1],[0,14]] |

Validation split (n = 10): ML accuracy 0.90, AUC 1.00.

**Interpretation.** Rules are precise but miss subtle scams (3 FN); the linear model recalls
everything but over-flags legitimate bank notifications that mention OTP/PIN (3 FP). Fusion
cancels part of each weakness on this split. **n = 20 fictional samples: a single error is 5
accuracy points. These numbers do not indicate real-world performance.**

**Explainability.** Rule spans with character offsets; per-prediction tf-idf × coefficient
contributions (top 8); fusion weights returned with every result. Global top features on v1
include function words ("and", "now", "sir") — evidence of dataset smallness that students
should discuss, not hide.

**Ethical considerations.** See ETHICS_AND_SAFETY. Language in outputs is deliberately hedged.
Synthetic-voice heuristic is disabled by default and labelled experimental.

**Caveats and recommendations.** Retrain when the dataset changes (`make data train evaluate`).
Do not raise weights of the acoustic heuristic without a validated study. Add negation
handling before trusting rule hits on protective phrases.
