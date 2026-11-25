---
name: validate
description: Measure how accurate a classification is by preparing a sample for an expert to check, then scoring the classifier against the expert's answers and reporting accuracy by confidence level with margins of error. Use after classification, when the researcher asks how reliable the results are, or when checked samples come back from the expert.
---

# Validate a classification

Automatic checks show the classifier followed the rules. Only a person checking a sample shows whether it is right. This skill has two parts, run at different times.

## Part 1: prepare the sample

1. **Write the design first**, in `<study>/docs/validation-plan.md`, and get it approved before drawing anything:
   - groups to sample from, built on what the model predicted for each finding (predicted yes and predicted no for each category the findings rest on), with confidence level inside those groups
   - the arithmetic, written out: each group's size in the population, the minimum drawn from it, each record's chance of being drawn, and the total. Check that the group numbers add up to the total before fixing the sample size (default about 250 organisations; say what margin of error that gives)
   - over-sample the predictions the findings rest on, low-confidence records, and records where two runs disagreed
   - always include predicted negatives and unknowns, or missed cases can never be estimated
   - none of the organisations in the fixed test set used to try out the classifier before the full run, or in the pilot; those were seen while the rules were being tuned
   - the expert's workload in hours (records times minutes per record), with the minutes measured in the pilot
   - the estimator, named: weighted precision and recall, a weighted table of what was confused with what, how intervals are calculated, and whether the finite size of the population is allowed for
   - the accuracy each confidence level must reach, and what happens if it does not (those records are reported as unknown, or all sent for checking)
   - the random seed
2. **Draw the sample** with the seed and save the list of ids.
3. **Make the expert's sheet**, `<study>/outputs/validation-sample.xlsx`. One row per organisation: name as written, country, matched entity, source link, quote. Empty columns for the expert: each label field, "evidence supports a decision? (y/n)", notes. **Leave out the model's label, reasoning and confidence.** Put the codebook's one-page scheme on a second sheet. Shuffle the row order.
4. **Tell the researcher** where the file is, roughly how long it will take, and that the expert should use the codebook and may use other sources.

## Part 2: score it

When the completed sheet is back:

1. **Join** the expert's labels to the model's records.
2. **Compute**, weighting each group back to its true size:
   - accuracy by confidence level, with 95% intervals
   - for each category the findings rest on: precision (of those labelled X, how many are X) and recall (of those that are X, how many were found)
   - a table of what was confused with what
   - how often the expert judged the evidence insufficient
3. **Review disagreements** with the researcher, now showing the model's reasoning. Sort each into: model wrong; expert corrected on seeing the evidence; codebook unclear. Report the scores both before and after this review.
4. **Apply the thresholds** from the plan exactly as written.
5. **Write** `<study>/docs/validation-report.md`: the design, the numbers, what they mean for each headline figure (as a range), the patterns in the errors, and limitations (one expert; small groups have wide ranges). Keep three kinds of uncertainty apart: classification error (from this sample), coverage (the unknowns) and sampling (the intervals). A range made by counting all unknowns in or out is a bound, not a confidence interval; say which is which. Repeatability (two runs agree) is not accuracy and is reported separately.
6. **Correct** every sampled record the expert overruled, marking it `method: expert`.

## Rules

- The design and thresholds do not change after the sample is drawn. If they must, log why.
- Do not describe confidence levels as reliable until this is done.
- A codebook problem found here means a new codebook version and re-classification of the affected group, not a quiet fix.
