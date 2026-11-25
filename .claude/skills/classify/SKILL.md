---
name: classify
description: Classify organisations against the approved codebook, producing for each a category, reasoning, source URL with quote, and confidence level, with automatic evidence checks. Use when the researcher asks to classify, categorise, label or look up organisations, or to run or re-run the classification.
---

# Classify organisations

## Before starting

Stop and say what is missing if any of these is not in place:
- an approved codebook (`<study>/docs/codebook.md`, version 1.0 or later, approval in `decisions.md`)
- the organisation table from `/clean-data`
- the codebook's "Labels for the script" block (see `/codebook`), which the code check reads

## Who does the look-ups

The two helper agents, started from this conversation on the researcher's own Claude account. **No API key is used or needed** (decided 2026-11-25). The script route in `<study>/src/lookup/` (`python -m lookup evidence|classify|check`) needs a key and is not the intended route; do not offer it.

- `evidence-finder` finds the evidence about one organisation. `org-classifier` then classifies it from the stored evidence record only. Start each by its own type (`subagent_type: "evidence-finder"`, `"org-classifier"`), never as `general-purpose`, and never with a model override.
- Work in batches of about 10 organisations. Start a batch's agents in one message. Save each record as it returns, one JSON file per organisation, before starting the next batch. A stopped run resumes from the files already saved.
- Before a run, tell the researcher how many organisations it covers and the estimated use of the account, in tokens (the units of text a Claude account's usage is counted in), from the last measured run (`<study>/outputs/`). Wait for a go-ahead for anything larger than the pilot.
- **One order of search for every entry**, stopping at the first step that settles which body is meant, with the stopping point saved in the evidence record (`stopped_at`): (1) the organisation's name, in Roman letters and in the nominating country's own script where a source gives it; (2) the list's own context, if the codebook has a rule for it: counts of job titles, departments, places and relations under the entry, made by code and passed to `evidence-finder` without names; (3) a lookup of the delegates under the entry (rule 8: public pages, employer and source only), for all of them and never a chosen few, after telling the researcher how many; (4) a question to the delegation, which only the researcher can send. Work the entries with the most delegates first.
- With a codebook below 1.0, only the codebook's own test may run, and its records go to `data/processed/draft-codebook/`, apart from the real ones.

**Then code checks every record, with no model:**

```
uv run python -I -m lookup.verify --evidence <folder> --classified <folder> --codebook <study>/docs/codebook.md
```

It opens each cited address again and looks for the quote on the page, and checks each label, rule and reason for "unknown" against the codebook's list. It changes nothing; it writes `verify.json` beside the records, with one of three outcomes per record: **passed**, **failed** (a real problem: a quote not on its page, a label, rule or reason not in the codebook), or **could not check** (a cited page would not open again; not a failure, but its quote goes to `citation-checker`). Read everything it flags. A record whose quote cannot be found goes back to `evidence-finder` once; if it fails again the organisation is `unknown`, reason `lookup failed`.

## Two steps, two records

Finding the evidence and classifying are separate steps, each saved before the next begins.

**The evidence record**, one file per organisation in `<study>/data/processed/evidence/`, named by `org_id`. It is what the `evidence-finder` agent returns, with `org_id`, `model` and `run_date` added: the entity matched, the status of the lookup, every search run, and for each item of evidence the page address, the page or section, the exact quote, the date and its level in the codebook's order of evidence. It holds no label.

**The classification record**, one file per organisation in `<study>/data/processed/classified/`, named by `org_id`. It holds one entry for each attribute in the codebook's labels block (`fields`), under `attributes`, and nothing else at the top level but the record's identity and provenance:

```json
{
  "org_id": "", "name": "", "country_context": "",
  "matched_entity": "the real-world organisation this was taken to be, with its country and website",
  "acting_for": null,
  "attributes": {
    "<attribute>": {
      "label": "a value from the codebook's list for this attribute, or unknown",
      "rule": "the codebook rule that decided",
      "confidence": "high | medium | low",
      "source_url": "", "quote": "copied exactly from one stored evidence item",
      "unknown_reason": "one of the codebook's reasons, only when label is unknown",
      "inferred": null
    }
  },
  "reasoning": "2-3 sentences: the deciding facts and rules",
  "status": "confident | uncertain | abstained | confirmed negative | failed",
  "codebook_version": "", "model": "", "run_date": ""
}
```

`inferred` stays `null` unless the codebook allows a value beside the strict line (its section on values beside the strict line) and the strict label is `unknown`. Then it is `{"label", "basis": "limited_evidence | proxy", "rule", "confidence", "source_url", "quote"}`, or for a proxy from the type of body `{"label", "basis": "proxy", "rule", "confidence", "from_attribute": "kind"}`. Confidence never goes above the codebook's ceiling for the basis (`inference_bases`). An inferred value never replaces the strict label and is counted on its own line.

Field values come from the codebook: every label is one from its list or `unknown`, and confidence follows from the level of evidence by its written rule. `status` takes one of the five values shown and no other. "Looked and found nothing" is `abstained`; a lookup that did not run is `failed`; the two are never recorded as the same value. A label other than `unknown` needs a `source_url` and `quote` from the evidence record, unless the rule that decided needs none. Derived groupings (the reporting group, the tier summary) are made by code from these labels, never by the classifier. `lookup.verify` refuses a record in any other shape.

## Steps

1. **Rules.** Apply the codebook's rules for cases that need no lookup (for example obvious government bodies). Record the rule name as the reasoning.
2. **Lists.** Match against the published lists the codebook approves. The list entry is the source.
3. **Pilot.** Take 50 organisations, chosen at random from those remaining by the study's sampling code (fixed seed, draw saved). Evidence for all 50, then classification, then `lookup.verify`. The classifying agent has no web access and sees only the evidence record and the codebook. Read the records the check flagged, and five others. Then report to the researcher: how many came back in each category and confidence level, how many unknown and why, five examples to read, and the estimated tokens and time for the full run. Wait for a go-ahead.
4. **Full run.** The same three steps for the rest, batch by batch. Never repeat a step already saved under the current codebook version and model. Look up a `failed` record once more before it is classified.
5. **Check the evidence.** `lookup.verify` has checked that each address opens and each quote is on its page. Whether a quote *supports* its label is a judgement code cannot make: give a random 10% of the answered records, and everything `verify` flagged, to `citation-checker`. Nothing is re-labelled by a checker; a person decides. A record that fails twice becomes `unknown` with its reason.
6. **Consistency.** Classify a random 10% a second time, without showing the first result. Report the agreement rate and keep both results for the validation sample.
7. **Known answers.** Every organisation on an approved list must have the matching label. Investigate each miss.
8. **Report:** counts by category and confidence; unknowns by reason and by delegation; the agreement rate; what failed the evidence check. State plainly that accuracy is not yet measured, and offer `/validate`.

## Rules

- No label without a source opened in this run. Not from memory, not from the name alone unless the codebook has a rule for it, and then confidence is low.
- "Unknown" with a reason is a correct output.
- The instructions given to `evidence-finder` and `org-classifier` are neutral: find what this organisation is, classify this organisation; never "check whether this is a fossil fuel company".
- `org-classifier` is given the path of the evidence record and of the codebook, and nothing else: not the name list, not another organisation's result, not your own view.
- One model for the whole run of each step: the one set in the agent's file. Do not override it for some batches. Write the exact model id into each record's `model` field.
- Do not show results by delegation or draw conclusions here. That waits for validation.
