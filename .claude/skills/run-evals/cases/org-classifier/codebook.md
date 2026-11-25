# Test codebook (for evals only)

This is NOT the study's codebook. It exists only to test whether the organisation classifier follows its rules. It has no fossil fuel categories and must never be used to classify the study's data.

## Labels

- **R1 `public_body`**: a ministry, government agency, parliament, court, central bank or local authority, as stated by an official source.
- **R2 `business`**: a for-profit company, or an association whose members are companies, as stated by a register or by the organisation itself.
- **R3 `other`**: any other identified organisation (university, charity, international organisation, media).
- **`unknown`**: always with one reason: "could be several entities", "nothing found", "not covered by the codebook", or "lookup failed".

## Order of evidence

Level 1: official registers and government pages. Level 2: independent reporting. Level 3: the organisation's own site.

## Confidence

Confidence follows from the evidence item relied on and the status of the evidence record:

- high: a level 1 item, and the evidence status is `confident`.
- medium: a level 2 item with evidence status `confident`, or a level 1 item with evidence status `uncertain`.
- low: a level 3 item, or a level 2 item with evidence status `uncertain`.

## Status of the classification

- `confident`: a label with confidence high.
- `uncertain`: a label with confidence medium or low.
- `abstained`: `unknown`, reason "could be several entities", "nothing found" or "not covered by the codebook".
- `failed`: `unknown`, reason "lookup failed" (the evidence record says the lookup did not run).
- `confirmed negative`: not used in this test codebook, which has no "no link" label.

## Record format

Return only this JSON:

```json
{"name_as_written": "", "country": "", "matched_entity": "", "label": "public_body | business | other | unknown", "unknown_reason": null, "rule": "R1 | R2 | R3 | null", "reasoning": "", "source_url": "", "page": "", "quote": "", "evidence_level": null, "confidence": "high | medium | low | null", "status": "confident | uncertain | abstained | confirmed negative | failed"}
```
