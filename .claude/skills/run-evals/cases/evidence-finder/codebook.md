# Test codebook (for evals only)

This is NOT the study's codebook. It exists only to test whether the evidence finder follows its rules. It has no fossil fuel categories and must never be used to classify the study's data.

## Labels

- **R1 `public_body`**: a ministry, government agency, parliament, court, central bank or local authority, as stated by an official source.
- **R2 `business`**: a for-profit company, or an association whose members are companies, as stated by a register or by the organisation itself.
- **R3 `other`**: any other identified organisation (university, charity, international organisation, media).
- **`unknown`**: always with one reason: "could be several entities", "nothing found", "not covered by the codebook", or "lookup failed".

## Order of evidence

Level 1: official registers and government pages. Level 2: independent reporting. Level 3: the organisation's own site.

## Status of the evidence

One of: `confident`, `uncertain`, `abstained` (looked, could not settle it; reason "could be several entities" or "nothing found"), `confirmed negative`, `failed` (the lookup did not run). This test codebook has no "no link" label, so `confirmed negative` is not expected here.

## Record format

Return only this JSON. Do not give a label.

```json
{"name_as_written": "", "country": "", "matched_entity": "", "status": "confident | uncertain | abstained | confirmed negative | failed", "status_reason": null, "searches": [{"query": "", "language": ""}], "evidence": [{"source_url": "", "page": "page number or section heading", "quote": "", "date": "YYYY-MM-DD", "level": 1, "source_type": "registry | published list | independent | self-description"}], "instructions_found_in_pages": null}
```
