# Final report outline

Target length 40–60 pages including appendices. Each section lists what to include and where
the material already exists in the repository.

1. **Abstract** — problem, approach (rules + explainable ML + fusion), headline test result
   with the small-data caveat, contribution to awareness.
2. **Introduction** — vishing context, why explanations matter, academic/defensive framing.
3. **Problem statement** — people cannot recognise tactics in real time; black-box tools give
   no learning value; privacy risk of uploading calls.
4. **Objectives** — O1 explainable indicators, O2 safe handling of audio, O3 measurable
   baselines, O4 usable dashboard, O5 documented ethics.
5. **Literature review** — from `docs/LITERATURE_REVIEW_GUIDE.md` themes 1–8.
6. **Existing-system limitations** — table in the literature guide.
7. **Proposed system** — overview figure (ARCHITECTURE.md), feature list, safety boundaries.
8. **Requirements** — condensed `docs/SRS.md` tables.
9. **Architecture** — layered diagram, request flow, replaceable interfaces, data model.
10. **Dataset methodology** — `docs/DATASET_CARD.md`, validation pipeline, split strategy.
11. **Model methodology** — Baseline A, B, hybrid; explanation mechanisms; `docs/METHODOLOGY.md`.
12. **Implementation** — stack, package layout, key modules, CI/CD, Docker; screenshots.
13. **Experiments** — `docs/EXPERIMENTS.md` E1–E4 with exact commands.
14. **Results** — metric tables, confusion matrices, per-category accuracy, error analysis,
    example explanations.
15. **Security, privacy and ethics** — `docs/THREAT_MODEL.md`, `docs/ETHICS_AND_SAFETY.md`,
    redaction, no-storage policy, consent flow.
16. **Limitations** — tiny synthetic data, English only, regex negation, heuristic acoustics,
    uncalibrated confidence, no real-world validation.
17. **Future work** — consented multilingual data, negation-aware rules, calibrated models,
    transformer extension, anti-spoofing study, user study on explanations.
18. **Conclusion** — what was built, what was learned, honest statement of evidence strength.
19. **References** — IEEE style.
20. **Appendices** — A dataset schema and samples; B API reference (OpenAPI export); C test
    plan and results; D user guide; E issue/milestone history; F consent form template;
    G individual contribution statements.
