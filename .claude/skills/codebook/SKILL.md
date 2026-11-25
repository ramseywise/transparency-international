---
name: codebook
description: Write or revise the codebook - the classification rules for a study, with definitions, observable proxies, accepted evidence, confidence levels and reasons for "unknown" - based on the literature review, for expert approval. Use before any classification, or when a category definition or rule needs to change.
---

# Codebook

The codebook is the single place that says what each label means and how to decide. The classifier, the expert who checks it and the report's methods section all work from it.

## Input

`<study>/docs/literature-review.md`. If it does not exist, stop and say the review comes first. The brief's own definitions are the starting point, not the codebook.

## What it contains

Write `<study>/docs/codebook.md`:

1. **Label scheme.** Each field and its allowed values.
2. **For each category:**
   - definition, one or two sentences
   - proxies: the observable facts that put an organisation in this category
   - evidence accepted, in order of trust (for example: official registry, regulator or published list; independent reporting; the organisation's own description)
   - three examples that belong and three that look similar but do not
   - basis: the source and page from the literature review, or "study decision" with the reasoning
3. **Hard cases**, each with a rule: state-owned companies; subsidiaries of a parent in another category; trade associations; consultancies, law firms and public relations firms; utilities with mixed activities; holding companies; organisations with several roles.
4. **Order of decisions** when more than one category could apply.
5. **Confidence levels, defined by evidence:**
   - high: an authoritative source states the deciding fact, and the organisation is identified with certainty
   - medium: one indirect source, or some doubt about which organisation is meant
   - low: inferred from the name, or from a weak source
   Adjust the wording to the study, but keep it about evidence, never about how sure the model feels.
6. **Reasons for "unknown":** blank; generic text; not an organisation; could be several entities; nothing found; sources conflict; found but not covered by the codebook.
7. **Version and change log.**
8. **Labels for the script**: under a heading with exactly that name, one fenced `json` block that repeats, for code, what the prose says: `version`, `label_field` (the main label), `fields` (each field and its allowed values, with `unknown` allowed for the main label), `rules` (the rule numbers), `negative_labels` (the "no link" values, which need evidence of a confirmed negative), `confidence_by_level` (for each level of evidence and lookup status, the confidence), `status_by_confidence` and `unknown_reasons`. The look-up script refuses to run without it; `<study>/src/lookup/codebook.py` shows the format. It must agree with the prose: when one changes, the other changes in the same version.

## Steps

1. Draft from the review's recommendations.
2. Test it on 20 real organisations from the data, chosen to be awkward. Where the rules do not give one clear answer, fix the rule, not the answer.
3. Show the researcher: the scheme on one page, the hard-case rules, and the open choices that are theirs to make.
4. On approval, set the version to 1.0 and record it in `decisions.md`.

## Changing it later

Any change after classification has started gets a new version, a logged reason, and a statement of which organisations must be re-classified.
