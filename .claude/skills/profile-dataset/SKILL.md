---
name: profile-dataset
description: Register a new dataset and produce a profile notebook describing its structure, quality and what can and cannot be learned from it, with charts. Use when a new data file arrives, or the researcher asks to look at, explore, describe, chart or assess the quality of a dataset.
---

# Profile a dataset

## Steps

1. **Register it.** Leave the file as downloaded in `<study>/data/raw/`. Add or update `<study>/data/SOURCES.md` with: file name, where it came from (URL), download date, SHA-256 hash, licence or terms if known, and whether it names people.
2. **Look before loading.** Sheets or tables, header rows, row counts, merged cells, notes rows. Report anything odd.
3. **Build the notebook** `<study>/notebooks/NN_<dataset>_profile.ipynb` with these sections. `unfccc/notebooks/01_unfccc_eda.ipynb` is the model.
   1. Structure: tables, columns, types, row counts
   2. Completeness: blanks and placeholders such as `-`, `n/a`, `none`, per column and per group
   3. Duplicates and identity: is there a key; repeated rows; the same entity under several spellings
   4. Each important column: number of distinct values, most common values, the long tail, values that are not what the column is for
   5. Relation to the research questions: restrict to the rows in scope and size the work
   6. **Inferred or looked up:** a table of what the data states directly, what can be inferred from it and how reliably, and what needs an outside source
   7. Findings in plain language, and caveats for anything published from it
4. **Run it** from top to bottom and confirm there are no errors.
5. **Report** the five things the researcher most needs to know, with numbers, and anything that affects the plan.

## Charts

Load the `dataviz` skill before writing chart code. One message per chart, a title that states the finding, labelled axes with units, sorted bars. Use the chart style in `<study>/src/charts.py`.

## Rules

- Print counts and organisation names, not individuals.
- Describe; do not clean. Cleaning is `/clean-data`, so that every change is logged.
- Numbers in the findings are read from the run, never typed from memory.
