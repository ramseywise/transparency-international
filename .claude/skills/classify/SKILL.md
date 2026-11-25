---
name: classify
description: Classify organisations against the approved codebook, producing for each a category, reasoning, source URL with quote, and confidence level, with automatic evidence checks. Use when the researcher asks to classify, categorise, label or look up organisations, or to run or re-run the classification.
---

# Classify organisations

## Before starting

Stop and say what is missing if any of these is not in place:
- an approved codebook (`<study>/docs/codebook.md`, version 1.0 or later, approval in `decisions.md`)
- the organisation table from `/clean-data`
- the codebook's "Labels for the script" block (see `/codebook`), which the script reads

## Who does the look-ups

The look-ups for many organisations are done by the **script** in `<study>/src/lookup/`, not by agents in the conversation. It does the same two steps as the `evidence-finder` and `org-classifier` agents, with the same models, but code decides everything that does not need judgement: which addresses may be opened (only those in the search results or a register), whether each quote is really on its page, whether a label and rule exist in the codebook, the confidence for a level of evidence, and what a failed or empty look-up becomes. A model only chooses pages, picks the evidence and applies the rules. A cheaper model (Haiku) then reads each result and flags any where the quote does not support the match or the label. It never changes a record; a person looks at what it flags. Use the agents only for a few organisations at a time (a re-check, a hard case), and start them by their type (`subagent_type: "evidence-finder"`, `"org-classifier"`), never as `general-purpose`.

```
uv run python -m lookup status   --study <study>
uv run python -m lookup evidence --study <study> --sample 50 --dry-run   # count and cost, no calls
uv run python -m lookup evidence --study <study> --sample 50
uv run python -m lookup classify --study <study> --batch
uv run python -m lookup check    --study <study> --batch
```

Every step prints how many organisations need a model call and the estimated cost before it starts. Run it with `--dry-run` first, and tell the researcher the cost before any step that costs more than a few dollars. A stopped run resumes where it stopped. With a codebook below 1.0 the script refuses unless given `--draft`, and its results then go to `data/derived/draft-codebook/`, apart from the real ones.

## Two steps, two records

Finding the evidence and classifying are separate steps, each saved before the next begins.

**The evidence record**, one file per organisation in `<study>/data/derived/evidence/`, named by `org_id`. It is what the `evidence-finder` agent returns, with `org_id`, `model` and `run_date` added: the entity matched, the status of the lookup, every search run, and for each item of evidence the page address, the page or section, the exact quote, the date and its level in the codebook's order of evidence. It holds no label.

**The classification record**, one line per organisation in `<study>/data/derived/classified.jsonl`:

```json
{
  "org_id": "", "name": "", "country_context": "",
  "matched_entity": "the real-world organisation this was taken to be, with its country and website",
  "category": "", "business_type": null, "sector": null, "fossil_tier": null,
  "rule": "the number of the codebook rule that decided",
  "reasoning": "2-3 sentences: the deciding fact and the codebook rule applied",
  "source_url": "", "page": "", "quote": "", "source_type": "registry | published list | independent | self-description",
  "evidence_level": null,
  "retrieved": "YYYY-MM-DD",
  "confidence": "high | medium | low",
  "status": "confident | uncertain | abstained | confirmed negative | failed",
  "unknown_reason": null,
  "method": "rule | list | lookup",
  "codebook_version": "", "model": "", "run_date": ""
}
```

Field values come from the codebook: the label is one from its list or `unknown`, and confidence follows from the level of evidence by its written rule. `status` takes one of the five values shown and no other. "Looked and found nothing" is `abstained`; a lookup that did not run is `failed`; the two are never recorded as the same value. A record with no `source_url` must be `unknown` with a reason, unless `method` is `rule`.

## Steps

1. **Rules.** Apply the codebook's rules for cases that need no lookup (for example obvious government bodies). Record the rule name as the reasoning.
2. **Lists.** Match against the published lists the codebook approves. The list entry is the source.
3. **Pilot.** Take 50 organisations, chosen at random from those remaining: `evidence --sample 50`, then `classify` and `check` on the same sample. The classifying model has no web access and sees only the evidence record and the codebook. Read the results the check flagged, and five others. Then report to the researcher: how many came back in each category and confidence level, how many unknown and why, five examples to read, and the estimated cost and time for the full run. Wait for a go-ahead.
4. **Full run.** The same three commands without `--sample`. The script saves each record as it returns, never repeats a step already done under the current codebook version and model, and looks up a `failed` record once more before it is classified.
5. **Check the evidence.** The script has already checked that each address opened and each quote is on its page, and Haiku has read each result. Everything Haiku flagged (`classified_checks.jsonl`, `needs_review`) is read by a person or by `citation-checker`, never re-labelled by the script. A record that fails twice becomes `unknown` with its reason.
6. **Consistency.** Classify a random 10% a second time, without showing the first result. Report the agreement rate and keep both results for the validation sample.
7. **Known answers.** Every organisation on an approved list must have the matching label. Investigate each miss.
8. **Report:** counts by category and confidence; unknowns by reason and by delegation; the agreement rate; what failed the evidence check. State plainly that accuracy is not yet measured, and offer `/validate`.

## Rules

- No label without a source opened in this run. Not from memory, not from the name alone unless the codebook has a rule for it, and then confidence is low.
- "Unknown" with a reason is a correct output.
- The instructions given to `evidence-finder` and `org-classifier` are neutral: find what this organisation is, classify this organisation; never "check whether this is a fossil fuel company".
- `org-classifier` is given the path of the evidence record and of the codebook, and nothing else: not the name list, not another organisation's result, not your own view.
- One model for the whole run of each step: the one set in the agent's file, which the script reads too. Do not override it for some batches. Write the exact model id into each record's `model` field.
- Do not show results by delegation or draw conclusions here. That waits for validation.
