# Are we ready for the pilot? What the two tests of 20 show

**Date:** 2026-11-25. **Status:** PROVISIONAL and unchecked by an expert. Two tests of 20 organisations each; none of this is a result of the study.
**Numbers from:** `unfccc/outputs/review_sheets_summary_PROVISIONAL.csv` and notebook `unfccc/notebooks/06_review_sheets.ipynb` (section 4 for cost).
**Made with:** Claude Code, Claude Fable 5.2; the look-ups and classifications in both tests by Claude Sonnet. Feasibility test under the first draft rules (2026-11-24); codebook test under codebook 0.9 (2026-11-25).

## Recommendation

- **Do not start the full run.** The method works mechanically, but it does not yet answer the fossil fuel question often enough.
- **Go to the pilot of 50 only after two steps:** (1) the lead researcher approves the codebook with the wider rule for "no link" (option B); (2) the 40 organisations already looked up are classified again under that codebook, from the stored evidence, to see how many "unknown" answers move. This costs no expert time. If most stay unknown, the look-up step needs changing before the expert labels anything.

## What we found

- **Too many unknowns.** The approved standard allows at most 20 per cent unknown in the pilot. On the fossil fuel link, 17 of 20 were unknown in the feasibility test and 20 of 20 in the codebook test. On business, 11 of 20 and 8 of 20.
- **The organisation is usually found; the deciding fact is not.** An organisation was identified for 15 of 20 and 19 of 20. The reason given for an unknown fossil fuel link is "nothing found" in 14 of 17 and 18 of 20 cases.
- **Likely cause (our reading, not measured):** the draft rules accept "no link" only on strong evidence, which a short web search rarely finds, so ordinary organisations with no visible link end up unknown. Option B addresses this.
- **The kind of organisation is answered more often:** 14 of 20 in each test, with a source.
- **Every label about an organisation has a cited source**, except those worked out by rule from sourced ones (business and tier in the feasibility test). Unknowns carry a reason, in all but one field of one case.

## Performance

- **Repeatable.** Two classification runs of the feasibility 20 agreed on 85 to 100 per cent of cases, by attribute. For the fossil fuel link, state ownership and tier, most answers were "unknown", so agreement there mainly shows the rules refuse consistently.
- **Cost per organisation:** about 34,500 tokens (units of text the model reads and writes) and 46 seconds, for one look-up and two classification runs.
- **Scaled up:** about 1.7 million tokens for 50; about 52 million tokens and 19 hours, if run one after another, for all 1,501.

## Limits

- 20 organisations per test. The codebook test was chosen to be awkward, so its shares do not describe the whole table.
- No expert has labelled either test, so accuracy is unknown. Only the pilot measures it.
- Neither test used the current codebook draft (0.12).
- In the feasibility test the helpers ran in a general mode, not as the fixed helper types the study now requires.

## Where to look

- The two review sheets, with names and reviewer columns: `unfccc/data/processed/feasibility/review_sheet_PROVISIONAL.csv` and `unfccc/data/processed/draft-codebook/codebook-test/review_sheet_PROVISIONAL.csv`.
- The expert's blind sheet for the pilot (draft, 50 random and 19 hard cases): `unfccc/data/processed/draft-codebook/pilot_blind_sheet_DRAFT.csv`.
