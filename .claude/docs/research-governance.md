# Research governance

Who decides what, when work stops for approval, and how an approval is recorded. `CLAUDE.md` rule 7 is the short version; this is the detail.

## Who decides

| Decision | Who |
|---|---|
| Definitions, thresholds, sampling, conclusions | the lead researcher |
| Whether a document (plan, proposal, codebook, report) is approved | the lead researcher |
| Whether an organisation is named in a report as fossil-linked | the lead researcher, case by case |
| How things are built: code, tools, file layout, which model does which work | the assistant, with Ramsey for anything that changes the shared setup |
| Version control, publishing, anything that leaves this machine | Ramsey, explicitly |

The assistant proposes. It does not decide a research question by building something that assumes the answer.

## Three kinds of approval

1. **Research decisions.** A definition, a threshold, a sampling rule, a conclusion. These are settled before the results are seen (rule 9). A change after results are seen is allowed only when it is logged with the reason.
2. **Project milestones.** The research plan, the research proposal, the codebook, the final report. Work on the next stage does not start until the milestone is approved.
3. **Publication-sensitive decisions.** Any organisation named in a report as fossil-linked. Each named organisation is checked against its evidence by a person before the report leaves.

## What an approval record holds

Every approval is a row in `<study>/docs/decisions.md`:

- the date;
- what was approved, with the **exact version** of the document (its version label or file name and date);
- who approved it;
- any conditions attached, and any objection that is still outstanding.

Three rules follow:

- **Approval applies only to the version reviewed.** If the document changes in substance afterwards, the approval no longer covers it.
- **Material changes need renewed approval.** A material change is one that could alter a definition, a threshold, a sample, a number or a conclusion. Fixing a typing error is not material; rewording a definition is.
- **Silence is not approval.** No reply means the question is still open. It goes under "Open" in the decision log, and the work that depends on it waits.

## Proposed is not approved

A document can hold proposals that nobody has approved yet. They are marked as proposed, kept in their own section, and nothing is built on them. The decision log is the only place that says what is approved; a sentence in a draft is not.

## Exchange points

Two milestones are exchange points: the research proposal (before any classification) and the report. At each, a full document goes to the lead researcher, who approves it, comments on it, or rewrites it.

- What comes back is saved unchanged, beside what was sent.
- The two are compared, and every change of substance is logged as a decision.
- The returned text is checked against the sources and the tables like any other text. A problem found there is raised with the lead researcher. It is never silently corrected and never silently accepted.

## Changing the assistant itself

The agents, skills, models and `CLAUDE.md` are part of the method. A change to any of them is logged in the decision log with the reason, and `/run-evals` is run again before results made after the change are relied on. Results made with different models are not mixed in one table.

## What these rules are and are not

They establish traceability, reproducibility and explicit human accountability. They do not replace independent expert review or peer review. The methods review done by the assistant is an additional critical reading of the research design; the lead researcher assesses its findings.
