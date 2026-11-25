# Research proposal: agrochemical industry presence in delegations to the Corvale water conference

Draft v1, for the lead researcher's approval. No organisation has yet been classified.

## 1. Background and question

The question is what share of the delegates on the national delegations of six countries to the Corvale water conference come from organisations linked to the agrochemical industry.

### 1.1 Sources read

Six sources have been read in full: four earlier counts by campaign groups and two news reports. The methodology of the Brindlemoor Index, which publishes a list of agrochemical-linked companies, has been requested but not yet obtained or read.

## 2. Proposed definitions

### 2.1 Unit

The unit classified is the home organisation; delegates are counted through it. Every organisation receives one category and, separately, a link tier. The tier is a property of the organisation and is assigned whatever its category, so that a public body or a research institute with agrochemical activity can hold a tier.

### 2.2 Categories

Each organisation receives exactly one of five categories: public body; private company; state-owned enterprise; agriculture sector; support staff.

### 2.3 Link tiers

- **Tier 1:** manufactures or formulates pesticides or synthetic fertilisers.
- **Tier 2:** any organisation with any current link to agrochemical products, of any size, including distribution, retail, use on farms, advice and research funding.
- **Tier 3:** banks and investors with holdings in tier 1 companies.

### 2.4 Who can hold a tier

Tiers are applied to private companies and state-owned enterprises only. Public bodies, research institutes and associations do not receive a tier.

### 2.5 Evidence

Each label rests on one quotation from a web page that the model finds by search. An illustration of the record format: Tarrowmere Crop Sciences, tier 1, high confidence, evidence: "Tarrowmere Crop Sciences Ltd is entered in the Ostavian commercial register under number 44712, with its seat in Velmar."

## 3. Data

The six delegations list 1,400 delegates from 900 distinct organisations after cleaning. Of these, 41 organisations are named only by a short form or acronym that could not be resolved; together they cover 310 delegates. Because they are only 4.6 per cent of organisations, their effect on the results is expected to be negligible, and they will be reported as unknown.

## 4. Method

### 4.1 Classification

For each organisation the language model searches the web, chooses a page, and returns a category, a tier, a confidence level (high, medium or low) and two or three sentences of reasoning.

### 4.2 Checks

A random 10 per cent of organisations are classified a second time. Agreement above 95 per cent between the two runs will show that the classification is accurate.

### 4.3 Expert sample

The expert reviews every organisation the model places in a tier. In addition, a random sample of 200 organisations is drawn, stratified by category and confidence level, with at least 20 organisations in each of the resulting groups. Low-confidence groups are oversampled. The expert sees the organisation, the model's quotation and the page it came from, but not the model's label, and records an independent label.

### 4.4 Reporting

Accuracy is reported as the share of sampled organisations for which the expert agrees with the model. The headline share of delegates from linked organisations is reported with a 95 per cent confidence interval, whose lower end counts every unknown organisation as not linked and whose upper end counts every unknown organisation as linked.

## 5. Decisions requested

1. **Naming.** Whether linked organisations are named in the published report. *Recommendation:* yes, after a right of reply.
2. **Languages.** Whether the report is published in Ostavian as well as English. *Recommendation:* yes.
3. **Tier threshold.** *Recommendation:* adopt the threshold used by the Brindlemoor Index, as the most widely used in the field.
4. **Who can hold a tier.** Options: (a) private companies and state-owned enterprises only; (b) any organisation. *Recommendation:* (b).
5. **Accuracy threshold.** *Recommendation:* 90 per cent, agreed before the expert sample is drawn.

## 6. Timeline

| Step | Time |
|---|---|
| Classification | one week |
| Expert review | two working days of the expert's time |
| Drafting | two weeks |

## Annex A. Requirements

R1 Original files are never edited. R2 One organisation table with a stable identifier. R3 A random 5 per cent of organisations are classified twice. R4 An expert sample of 150 organisations, stratified. R5 The expert labels blind. R6 The accuracy threshold is set before validation.
