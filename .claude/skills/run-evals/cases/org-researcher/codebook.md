# Test codebook (for evals only)

This is NOT the study's codebook. It exists only to test whether the organisation researcher follows its rules. It has no fossil fuel categories and must never be used to classify the study's data.

## Labels

- **R1 `public_body`**: a ministry, government agency, parliament, court, central bank or local authority, as stated by an official source.
- **R2 `business`**: a for-profit company, or an association whose members are companies, as stated by a register or by the organisation itself.
- **R3 `other`**: any other identified organisation (university, charity, international organisation, media).
- **`unknown`**: always with one reason: "could be several entities", "nothing found", or "not covered by the codebook".

## Order of evidence

1. Official registers and government pages. 2. Independent reporting. 3. The organisation's own site.

## Confidence

- high: an official source states what the organisation is, and the match to the name is certain.
- medium: one indirect source, or some doubt about the match.
- low: inferred from the name or a weak source.

## Record format

Return only this JSON:

```json
{"name_as_written": "", "country": "", "matched_entity": "", "label": "public_body | business | other | unknown", "unknown_reason": null, "rule": "R1 | R2 | R3 | null", "reasoning": "", "source_url": "", "quote": "", "confidence": "high | medium | low | null"}
```
