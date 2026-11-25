# Study template

The clean starting point for a new study. Copy this folder to `<study>/` at the top of the workspace and follow `.claude/docs/new-study-guide.md`.

It holds structure only. There is no definition, threshold, data source, classification or conclusion in it, and none may be added: anything of that kind belongs to one study and is decided in that study.

```
docs/brief.md                    what the researcher wants to find out
docs/technical-requirements.md   outline, filled in by /plan-study
docs/decisions.md                the decision log, empty
docs/codebook.md                 outline, filled in by /codebook after the proposal is approved
docs/proposal.md                 outline, filled in by /research-proposal
```

`docs/` holds only what the researcher and stakeholders read or approve. Working records go in `docs/archived/`: `numbers.md`, `cleaning-log.md`, `reviews/` (each /check-work record) and `old/` (superseded drafts).

Folders created as the study needs them: `data/raw/`, `data/processed/`, `src/`, `tests/`, `notebooks/`, `outputs/`, `report/`.

After copying, delete this file from the new study folder.

Changing this template changes how every future study starts. It needs a logged reason (`CLAUDE.md` rule 14).
