# Literature review guide

Goal: 12–20 sources, organised by theme, each summarised in ≤ 5 sentences with relevance to
ViShield. Cite in IEEE style. Prefer peer-reviewed venues; use vendor reports only for
statistics and label them as such.

## Themes and starting points (search terms, not citations — verify every source)

1. **Voice phishing and social engineering**
   Search: "vishing detection", "voice phishing social engineering taxonomy", "telephone scam
   persuasion principles" (Cialdini's principles: authority, scarcity/urgency, reciprocity).
   Look for taxonomies that map to our eight indicator families.
2. **Text-based phishing detection**
   Search: "phishing email classification TF-IDF logistic regression", "SMS spam detection
   benchmark", "smishing detection". Explains why linear models are competitive and explainable.
3. **Speech-to-text for downstream classification**
   Search: "Whisper robust speech recognition", "ASR error propagation text classification",
   "call transcript analysis fraud".
4. **Explainable ML for security**
   Search: "LIME", "SHAP", "interpretable models security classification", "explanations for
   phishing detectors user study".
5. **Synthetic speech / anti-spoofing (context only)**
   Search: "ASVspoof challenge", "audio deepfake detection generalisation". Use this to justify
   why our synthetic-voice heuristic is labelled experimental.
6. **Acoustic correlates of stress and pressure**
   Search: "speech rate stress detection", "prosodic features deception". Note weak and
   inconsistent findings – this supports the low acoustic weight.
7. **Privacy and consent in speech datasets**
   Search: "speech data anonymisation", "GDPR voice biometric", "consent audio research ethics".
8. **Awareness training effectiveness**
   Search: "phishing awareness training effectiveness", "security education explanations".

## Template per source

```
[n] Authors, "Title," Venue, Year.
Summary: …
Method/data: …
Relevance to ViShield: …
Limitation noted by authors: …
```

## Existing-system limitations table (feeds report §6)

| Existing approach | Limitation | ViShield response |
|---|---|---|
| Carrier-side caller-ID/blocklists | reactive, number spoofing | content-based indicators |
| Black-box commercial "scam detectors" | no explanation, cloud upload of audio | explainable, local, no storage |
| Keyword-only apps | brittle, no probability | rules + ML fusion with spans |
| Deepfake detectors | poor generalisation | experimental flag, not a verdict |
