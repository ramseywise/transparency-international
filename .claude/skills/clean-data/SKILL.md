---
name: clean-data
description: Clean a dataset with logged, repeatable rules, fill in missing values in separate columns, and build the organisation table that maps every spelling to one entity. Use after a dataset is profiled, or when the researcher asks to clean, standardise, deduplicate, preprocess, impute or match names.
---

# Clean data and build the organisation table

Cleaning is done by code that can be re-run, never by editing a file. Everything written goes to `<study>/data/derived/`.

## Steps

1. **Read the profile notebook** and the research plan. Clean only what the questions need.
2. **Write the rules as a script** in `<study>/src/cleaning/clean.py`, run with `uv run python -m cleaning.clean`. Typical rules: trim and collapse spaces; normalise Unicode; turn placeholders into empty; split titles from names; standardise country names against a fixed list; restrict to the rows in scope.
3. **Log each rule** in `<study>/docs/working/cleaning-log.md`: its name, what it does, how many rows it changed, three before-and-after examples.
4. **Reconcile.** Rows in, rows out, and the reason for every row dropped. Totals per group must match the raw file unless a logged rule explains the difference.
5. **Duplicates.** Apply the study's rule for the same person or record appearing twice. Flag, do not delete, anything the rule does not cover.
6. **Organisation table** (`organisations.parquet`):
   - an id, a canonical name, the country context, and every raw spelling that maps to it
   - pass 1: exact match after clean-up
   - pass 2: similar names within the same country, proposed as merges
   - pass 3: acronyms and translations resolved by looking them up, with the source recorded
   - merge only when confident. Two entities wrongly merged is worse than one entity left as two.
   - values that are not organisations keep a reason code and no id
7. **Missing values.** Decide per column whether it can be inferred, from what, and how reliably. Write inferred values to a new column next to the original, with `_method`, `_source` and `_confidence` columns. Never write into the original column.
8. **Report** in plain language: what was changed and how much, what could not be resolved, and the size of the job that remains for classification.

## Rules

- The raw file is never opened for writing.
- Any step that needs the web (resolving an acronym, finding a missing employer) follows the evidence rules: a source URL, or it stays empty.
- Looking up a person is allowed only when their organisation is missing, on public pages, recording the employer and URL only.
