# Threat model

Method: STRIDE over the components in `ARCHITECTURE.md`, plus misuse cases specific to a
phishing-analysis tool. Scope is the local/private-network academic deployment.

## Assets

A1 uploaded audio (transient) · A2 transcripts (may contain sensitive phrases) · A3 analysis
metadata DB · A4 model file · A5 source code & CI · A6 project reputation (misuse).

## Trust boundaries

Browser ↔ API/dashboard · API ↔ filesystem/DB · repo ↔ CI runners · optional STT model download.

## STRIDE table

| Threat | Component | Impact | Mitigation (implemented) | Residual |
|---|---|---|---|---|
| Spoofing – malicious file disguised as audio | upload | decoder crash / RCE in codec | extension + MIME + magic-byte check; libs updated via dependabot; size cap | decoder CVEs → `pip-audit` |
| Tampering – path traversal via filename | upload | write outside dir | filename stripped to basename; dev storage uses UUID names | – |
| Tampering – corrupt/poisoned model file | model load | wrong scores / pickle exec | model not committed; built from data at image build; load failures degrade to rules-only | joblib pickle trust: load only self-trained files |
| Repudiation – no record of analyses | DB | cannot audit | metadata with id, time, model version | – |
| Information disclosure – PII in logs | logging | privacy breach | redacting log filter; generic error messages | novel PII formats |
| Information disclosure – transcript stored | DB | privacy breach | only SHA-256 + metadata stored | – |
| Information disclosure – audio retained | filesystem | privacy breach | off by default; ignored in production; documented | dev misuse |
| Denial of service – huge/long files | API | CPU/memory exhaustion | streamed read cap, duration cap, batch size ≤ 500 | no rate limiting (add reverse proxy if exposed) |
| DoS – regex backtracking | rules | CPU | bounded quantifiers, no nested unbounded groups | review new rules |
| Elevation – container root | Docker | host compromise | non-root user; no secrets in image | – |
| Supply chain – vulnerable deps / leaked secrets | CI | compromise | `pip-audit`, gitleaks, dependabot, pinned major versions | zero-days |

## Misuse cases (defensive tool turned offensive)

| Misuse | Why it fails here |
|---|---|
| Use as a "scam script quality checker" to refine phishing | No generation; outputs list defensive indicators only; policy prohibits; explanations are coarse |
| Feed real victims' calls without consent | Consent checkbox/flag mandatory; docs + banner; no telephony; no storage |
| Present output as legal proof | Wording everywhere: "potential indicators… requires human review" |
| Claim deepfake detection | Synthetic signal disabled by default and labelled experimental |

## Out of scope

Internet-facing hardening (TLS, auth, rate limiting) – required before any non-academic use.
