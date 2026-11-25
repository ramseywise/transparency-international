"""Organisation look-up as a script: find the evidence about each organisation, classify it
from that evidence, and have a cheaper model check each result.

This does in code what the `evidence-finder` and `org-classifier` agents do in a
conversation, for the ~1,250 organisations of a full run. What can be decided by code
is decided by code: which searches were run, whether a quote is on the page it cites,
whether a label is one the codebook allows, what the confidence is for a level of
evidence, and what happens to a failed or abstained look-up. A language model is used
only to choose pages, to pick the evidence from them, and to apply the codebook's
rules to it. A second, cheaper model (Haiku) then reads each result and flags any
where the quote does not support the match or the label; it never changes a record.

    uv run python -m lookup status   --study unfccc
    uv run python -m lookup evidence --study unfccc --sample 50 --seed 7 --dry-run
    uv run python -m lookup classify --study unfccc
    uv run python -m lookup check    --study unfccc --batch
"""
