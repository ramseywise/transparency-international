# Technical requirements and implementation plan

Status: draft v4, 2026-11-24. Changes from v3: references are sorted into tiers and all 134 are screened (4.1, L4d); search is checked against test questions (L8); the proposal follows the report register and the final document is an online article (P7); the shared chart style is built (6). Proposed since v4, awaiting approval: a graph of the data with its schema, static images and an interactive view (4.8, step 9a); deferred 2026-11-24 until Ramsey decides on it, and not built.

**The changes for v5 are listed in section 10. Ramsey approved them on 2026-11-24, except E10. Sections 1 to 9 have not yet been rewritten to match; where they differ, section 10 holds.**

**Section 11, added 2026-11-24, covers the workspace itself, not the research design: what was changed that day at Ramsey's request after an outside review of `CLAUDE.md` (the rules file, a study template, and read-only access from Claude Desktop and other clients), and what that review suggests for this study that is still a proposal.**

- Product requirement: `unfccc/docs/Research brief.docx`
- Data: UNFCCC COP31 list of registered on-site participants, public, downloaded from unfccc.int/documents/663817

## 1. What the brief asks for

Two questions about the **Parties** and **Party overflow** sheets.

| | Question | Unit | Scope |
|---|---|---|---|
| Q1a | How many delegates come from business, and from which sectors? Per delegation, Party and Party overflow separately, as a count and a share. | delegate | EU and its 27 member states |
| Q1b | The same for all countries, ranked by number and by share, with priority on full Party badges. | delegate | all Parties, "if feasible" |
| Q2 | How many delegates have a home organisation linked to the fossil fuel economy, in three tiers? | delegate | EU and its 27 member states |

Working definitions from the brief. The literature review turns these into testable rules (section 4.2).

- **Business:** for-profit companies, industry and trade associations, consultancies, law firms, financial institutions. State-owned enterprises possibly counted separately. NGOs, universities, think tanks and media excluded.
- **Fossil tier 1:** oil, gas and petrochemical companies, and fossil fuel infrastructure operators.
- **Fossil tier 2:** utilities and companies in sectors with ongoing fossil fuel activities or dependencies.
- **Fossil tier 3:** banks, insurers and asset managers with documented fossil fuel financing exposure.

Size of the job:

| Scope | Delegates | Distinct home organisations (as typed) |
|---|---|---|
| EU and 27 member states | 3,821 (1,381 Party, 2,440 overflow) | 1,599 as typed; 1,501 after cleaning, of which 840 have one delegate (`unfccc/data/derived/cleaning_stats.json`; corrected 2026-11-24 from the first profile's 1,559 and 913) |
| All Parties | 34,809 | 12,450 |

About 1,300 of the EU rows contain an obvious government word, which leaves roughly 1,250 organisations to classify. No row in scope carries an organisation type, and there is no labelled list from an earlier conference. Every label is inferred or looked up.

## 2. Research standard

The output will not be peer reviewed, so the method carries as many of the checks a reviewer would ask for as it can. What these checks give is traceability, reproducibility and explicit human accountability. They do not replace independent expert review or peer review, and the report says so.

| ID | Standard | What it means here |
|---|---|---|
| R1 | **Decide before you look.** | The codebook, the validation sample design and the accuracy thresholds are written, dated and approved before the classifier runs on the full data. Later changes are logged with a reason. |
| R2 | **Definitions come from the literature.** | Each category has a definition and observable indicators (proxies) with a cited source, or is marked as our own decision with the reasoning. |
| R3 | **A documented literature search.** | Search terms, dates, sources searched, and how many items were found, screened in and screened out, with reasons. Enough for someone else to repeat it. |
| R4 | **Every claim is traceable.** | Each classification has a source URL and quote. Each number in the report comes from a generated table. Each citation has a page. |
| R5 | **Measured error, stated uncertainty.** | An expert checks a random sample after the run. Headline numbers are reported with the error rates that sample shows, and with unknowns as their own line. |
| R6 | **Sensitivity.** | Results are shown under stricter and looser definitions (tier 1 only; tiers 1 to 2; tiers 1 to 3; with and without inferred affiliations). |
| R7 | **Reproducible.** | Code, codebook, prompts, model version, dates and the classified organisation table with evidence are kept so the result can be regenerated and audited. |
| R8 | **Limitations are written down.** | Registered is not attended. Affiliations are self-declared. One expert validates, so there is no second-rater agreement figure unless a second person labels a subset. |

## 3. The sequence

The literature review comes first, because the classification rules come out of it. Data preparation does not depend on it and runs alongside.

```
1 Plan (approved)
2 Literature: find, download, read, index        alongside: Data (clean, build organisation table)
3 Literature review                              alongside: House style from TI publications
4 Research proposal: literature review + methodology
      ⇄ EXCHANGE 1: the lead researcher approves, comments or rewrites
5 Codebook (approved)
6 Classify: pilot, then EU
7 Expert checks a sample ──> 8 Results
9 Report
      ⇄ EXCHANGE 2: the lead researcher approves, comments or rewrites
```

Nothing is classified before exchange 1 is closed. The proposal is where the definitions and the method are agreed; the codebook then turns the agreed definitions into working rules.

## 4. Requirements

### 4.1 Literature: building our own reference index

The brief gives three starting sources: one TI report (PDF) and two articles on transparency.org. All three are downloaded, extracted and searchable (221 passages). Between them they cite 134 further pages and documents (links, and endnote references in the report). All 134 have been screened from their title and the sentence they were cited in: 51 are in, 83 are out, each with a reason (`literature/search-log.md`). None is downloaded until the screened-in list is approved. No wider search has been run yet. The index is reusable for later topics.

| ID | Requirement |
|---|---|
| L1 | A ledger (`literature/ledger.jsonl`), one line per source: identifier (DOI or URL), title, authors, year, type (paper, NGO report, blog, dataset documentation), peer reviewed or not, status (candidate, screened in, screened out, read) and the reason. |
| L2 | A search log (`literature/search-log.md`): what was searched, where, when, and the counts at each stage (R3). |
| L3 | Sources are found three ways: the seeds, their reference lists and citing papers (through OpenAlex, which is free), and web search for NGO reports and blogs, which OpenAlex mostly lacks. |
| L4 | Screened-in sources are downloaded and never edited: PDFs to `literature/pdfs/`, web pages as received to `literature/pages/`. Every download is logged with its URL, date and result. Text is extracted to `literature/text/` and can be rebuilt from the raw files at any time. |
| L4a | **Web pages.** Only the article itself is kept: menus, footers, tag lists and "related" cards are dropped. Paragraphs are numbered so a quote can be located. Charts embedded from another service are not captured and are noted as missing. |
| L4b | **References inside a source.** Every link in the body of a page or PDF is recorded in the ledger as a candidate, with the sentence it appeared in, where it was found, and its kind (same site, document download, other site). |
| L4c | **The crawler does not wander.** It downloads only the pages it is given. Following links one step within the same site is an explicit option. Links to other sites are downloaded only after screening (L1). It respects each site's robots.txt, waits between requests, identifies itself generically, and never sends personal or project details. No pages behind a login. |
| L4d | **Tiers.** Candidates are sorted before screening: 1 primary (cited by two or more of our sources, or three or more times); 2 core (scholarly, official, data and method pages); 3 supporting (reports by TI and other organisations); 4 news; 5 low signal. A tier orders the work and is reported; it does not decide relevance. Every candidate is screened against the questions whatever its tier, and the decision, reason and question are recorded. |
| L5 | **One reading record per source** (`literature/records/<id>.json`), following the extraction template used in learn-ai-engineering: citation, research question, data, method, definitions of key terms, proxies used to identify a category, findings, limitations. Each item has a quote and page. A field that the source does not state is left empty, never filled from memory. This is the only model step on the literature and runs once per source. |
| L6 | Text is split into passages by section and paragraph. Each passage keeps its source id and its location: page for a PDF, section and paragraph number for a web page. |
| L7 | Passages are embedded on this computer with a small open multilingual model and stored as files in `literature/index/`. Search combines keyword and similarity ranking and returns passages with source and location. No hosted service and no cost per search. |
| L8 | About 20 test questions with known answers check that search finds the right passage, and an automated test fails if the result gets worse. Measured 2026-11-24 on 22 questions: the right passage came first for 17 and in the first five for 20. The two misses: a question asked in German about an English text, and a question asking for a definition where neighbouring passages on the same page ranked higher. |
| L9 | No compiled wiki and no summaries written into the index. Synthesis happens in the literature review, where a person reads it. |

### 4.2 Literature review and codebook

| ID | Requirement |
|---|---|
| K1 | The review answers a fixed list of questions (below), each with a table of how every source handles it, where sources agree and differ, and a recommendation. |
| K2 | The codebook is written from the review: for each category a definition, the proxies that identify it, which evidence sources count and in what order of trust, worked examples, and rules for hard cases. |
| K3 | The codebook defines the **confidence levels** by evidence, not by feeling (see C3), and the **reason codes for "unknown"** (see C4). |
| K4 | The codebook has a version number. The expert approves it before classification (R1). |

Questions the review must answer, taken from what the brief leaves open:

1. Which sector scheme do comparable studies use, and which fits this data?
2. What counts as evidence for tier 2 ("ongoing fossil fuel activities or dependencies") and tier 3 ("documented financing exposure")? Is there a threshold?
3. Does a subsidiary inherit its parent's tier?
4. How are trade associations with fossil fuel members treated? Consultancies and law firms with fossil clients?
5. Are state-owned enterprises business, public sector, or their own group?
6. How should the EU's own delegation (271 delegates) be reported next to the member states?
7. Which published lists of fossil-linked companies and financiers exist, how are they compiled, and can they be reused?
8. How did earlier counts of lobbyists at COPs (including TI's own) identify people, and what were the criticisms?

### 4.3 Data

| ID | Requirement |
|---|---|
| D1 | Raw files are never edited. Each has a note with its source URL, download date and file hash. |
| D2 | The data is public and names real people. Analysis and reporting are at organisation and delegation level. Individuals are looked up only under C6. |
| D3 | Every dataset gets a profile notebook from one template: structure, completeness, duplicates, top values, what can be inferred and what needs a lookup, findings in plain language. One shared chart style. |
| D4 | Cleaning is code with a log: each rule is named and counted. Row counts before and after must reconcile. |
| D5 | **Inferred values never overwrite.** They go in a separate column with the method, the source and a confidence. |
| D6 | A person on both sheets for the same country is counted once, on the Party badge. |
| D7 | The EU scope is a fixed list of 28 nominators. All 28 are present in the file. |
| D8 | One organisation table: a stable id, a canonical name and every raw spelling that maps to it. Matching uses exact match after clean-up, then text similarity within the same country. Acronyms and translations ("BMUKN", "MEAE", "Botschaft") are resolved with the country as context and the source recorded. |

### 4.4 Classification

There is no capacity to check every label by hand. The model does the lookup, and its output is built so that a sample can be audited afterwards.

| ID | Requirement |
|---|---|
| C1 | Classification is per organisation, joined back to delegates. |
| C2 | Each organisation gets one record with: **category** (and business type, sector, fossil tier where they apply); **reasoning** in two or three sentences naming the codebook rule used; **source URL** with the quote that supports the label and the retrieval date; **confidence**. Also: which real-world entity the name was matched to, codebook version, model and date. |
| C3 | **Confidence is defined by the evidence.** High: an official or authoritative source states what the organisation does and the name match is certain. Medium: one indirect source, or some doubt about the match. Low: inferred from the name or a weak source. The exact wording is set in the codebook. |
| C4 | **"Unknown" always has a reason**, so we can see where information is missing: (a) field blank; (b) generic text such as "Private sector"; (c) not an organisation, such as a place name; (d) acronym or name that could be several entities; (e) nothing found on the web; (f) sources conflict; (g) found, but the codebook does not cover the case. Counts per reason and per delegation are reported. |
| C5 | Cheapest step first: rules for obvious government bodies; matching against published lists the review approves (K1 question 7); then a model with web search, using the organisation's own site, registries and third-party sources. |
| C6 | **Filling in a missing affiliation.** When the organisation is blank or generic (reasons a to c), the person's name, title and country may be searched on public pages, including professional profiles that appear in search results, to find the employer. Only the employer and the source URL are recorded. The result goes in a separate inferred column (D5). No logged-in scraping of LinkedIn, which its terms forbid. |
| C7 | The model never answers from memory. No source, no label. |
| C8 | A pilot of 50 organisations measures cost, time and the share of unknowns before the full run. |
| C9 | Results are stored per organisation, so re-running costs nothing unless the codebook changes. |

### 4.5 Evaluation

| ID | Requirement |
|---|---|
| V1 | **Automatic checks on every record:** the URL opens; the quote appears on the page; the page is about the matched entity. Failures are re-run or set to unknown. |
| V2 | **Consistency:** a random 10% is classified a second time independently. The agreement rate is reported. Disagreements go to the expert sample. |
| V3 | **Known answers:** organisations that appear on an approved published list must come out in the matching tier. Misses are investigated. |
| V4 | **Expert sample, after the run.** A random sample of about 250 EU organisations, drawn with a recorded seed, stratified by predicted category and confidence level, with business and fossil predictions and low-confidence records over-represented. It includes predicted negatives, which is the only way to estimate what was missed. |
| V5 | The expert sees the organisation, country and evidence, but not the model's label or reasoning, and records their own label. Disagreements are then reviewed with the model's reasoning visible. |
| V6 | Reported from the sample: accuracy per confidence level; precision and recall for business and for each fossil tier, with confidence intervals; a table of what was confused with what. |
| V7 | **Using the result.** Thresholds are agreed beforehand (R1). If a confidence level falls below its threshold, those records are either reported as unknown or sent for review. Headline counts are published with the measured error range. |
| V8 | Every organisation **named** in the report as fossil-linked is checked by a person, whatever its confidence. |

### 4.6 Analysis and report

| ID | Requirement |
|---|---|
| A1 | One command regenerates every table and chart. No number is typed by hand. |
| A2 | Each table gives count and share, Party and overflow separately, with unknowns as a row. |
| A3 | Sensitivity versions per R6. |
| W1 | The report is drafted in order: methods from the codebook and logs, results from the tables, discussion last. |
| W2 | A check fails the draft if a number has no source table or a citation has no reading record and page. |
| W3 | Revision is done by independent reviewers that have not seen the author's reasoning: method, numbers, citations, plain language, fairness to named organisations. |
| W4 | Standing caveats are always included (R8), with the classification date, model and codebook version. |

### 4.7 Research proposal, exchange points and house style

| ID | Requirement |
|---|---|
| P1 | **A research proposal** is written after the literature review and before the codebook. It contains: background and research questions (from the brief, in the lead researcher's wording); what the literature says; proposed definitions with their sources and alternatives; the data; the method; how a language model is used, with risks and controls; limitations; a numbered list of decisions requested; timeline. It contains no results and names no organisation as fossil-linked. |
| P2 | The proposal is written for a researcher, not a builder: no requirement numbers, file names or model names in the main text. These requirements go in an annex. It promises only what these requirements deliver. |
| P3 | **Exchange 1.** The proposal goes to the lead researcher, who approves, comments or rewrites. No classification starts before her reply is taken in. |
| P4 | **Exchange 2.** The same for the report. It is final only when she has approved a version on which the number and citation checks pass and each named organisation is signed off (V8). |
| P5 | **Taking a returned document in.** What she sends is kept unchanged. It is compared with what she was sent, and each difference is sorted into substance (a definition, scope, method step, finding or claim), style, or question. Substance changes are logged as decisions with her name and the date and carried into these requirements and the codebook. |
| P6 | **Her text is checked too.** Citations and numbers in a rewritten passage are re-checked. A mismatch is reported to her with the evidence and a proposed wording; it is neither silently corrected nor silently accepted. |
| P7 | **House style.** A style guide (`.claude/docs/house-style.md`) is derived from TI's own publications in the library: structure, voice, how numbers and sources are presented, terms and spelling. Each pattern has a quoted example with its location. The guide separates two registers. The proposal follows the report register (impersonal, endnotes). The final document is an online article in the feature register, like the two TI articles named in the brief, with a closing methodology section. |
| P8 | Style governs how things are said, never what may be said. Where TI's published tone is stronger than this study's evidence supports, the evidence decides. Sentences from TI publications are not reused without quotation and citation. |
| P9 | The lead researcher's rewrites are fed back into the style guide, as the best evidence of the style she wants. An official TI style guide, if one exists, overrides the derived one. |

### 4.8 Graph of the data (proposed 2026-11-24, not yet approved)

Several things the plan already records are relationships: which source cites which (L4b), which spellings belong to one organisation (D8), which delegation an organisation's delegates came with, which category and tier an organisation was given and on what evidence (C2), and which source a definition comes from (R2). Questions 3 and 4 of the review (subsidiaries, trade association members) add links between organisations. At the moment these are kept in separate tables. This section keeps them together as one graph, so the structure of the data (its ontology: the kinds of things and the kinds of links between them) is written down, and can be looked at and queried.

| ID | Requirement |
|---|---|
| G1 | **The graph is built by code from the existing tables** (ledger, organisation table, classification records, codebook). It is never edited by hand and is regenerated by the same single command as the tables (A1). |
| G2 | **Node types:** source; organisation; delegation; category and fossil tier (the codebook's terms). **Edge types:** source *cites* source; delegation *has delegates from* organisation (count, Party and overflow separately); organisation *classified as* category or tier (confidence, source URL, codebook version, model, date); organisation *part of* or *member of* organisation (from the review, questions 3 and 4); category *defined by* source (the codebook's citation). |
| G3 | **No people in the graph.** Delegates appear only as counts on the edges between delegations and organisations (D2, rule 8). |
| G4 | **The schema is a document** (`<study>/outputs/graph/schema.md`): every node and edge type, what it means, which table it comes from. Its version follows the codebook's. The data is written as plain files (`nodes.csv`, `edges.csv`, and the same as one JSON file) that any tool can read. |
| G5 | **Static images** in the shared chart style: the schema as a diagram, the citation network of the literature, and the organisations of one delegation by category. These can go in the proposal, the report or the methodology section. |
| G6 | **An interactive view**, built as one web page with the graph data inside it and published as a private page on claude.ai (an artifact). Readers can zoom, filter by category, tier, confidence and "unknown", and click a link to see its evidence and source. It needs no server. Each page shows the date and codebook version it was made from, and it is rebuilt after each run, not updated by hand. |
| G7 | **Naming.** Until an organisation has been signed off (V8), a view shared outside the team does not show it by name as fossil-linked. Pages are private unless Ramsey shares them. |
| G8 | **Optional: an MCP server** (a connector that lets Claude use the library from claude.ai or the desktop app, not only from this folder). Read only: search the literature, fetch an organisation's record, fetch the links around one node, fetch the schema. **Partly built 2026-11-24 at Ramsey's request** (`mcp_server/`, section 11, S6): the working rules, the list of studies, a study's documents and decisions, search across study documents, literature search and source records. Not built: the organisation record and the graph tools, which wait for the classification and for approval of this section. The server never serves a `data/` folder. |

## 5. Risks of using a language model for this, and the controls

| Risk | What it looks like here | Control |
|---|---|---|
| **Invented facts or sources** | A plausible description of a company, or a URL that does not exist | C7, V1 |
| **Wrong entity** | "Titan" or "FAB" matched to a different company of the same name | Country as context; matched entity recorded (C2); V1 |
| **Confidence that means nothing** | The model says "high" for everything | Confidence defined by evidence (C3) and tested against the expert sample (V6) |
| **Uneven coverage** | Large, English-language companies are found; small or non-English ones become unknown. Country comparisons are then biased. | Unknown rate reported per delegation (C4); search in the country's language |
| **Out-of-date knowledge** | A company has merged, sold its gas business, or been renamed | C7; retrieval date on every source |
| **The model's own definitions** | Where the codebook is vague, the model fills the gap with its own idea of "fossil-linked" | Codebook with proxies and hard cases (K2); reason (g) for uncovered cases; reasoning must name the rule (C2) |
| **Self-description** | A company site says "energy transition leader" | Codebook ranks third-party sources above self-description for fossil tiers |
| **Leading the witness** | A prompt that expects to find fossil links finds them | Neutral instructions; negatives in the sample (V4) |
| **Instructions hidden in web pages** | A page tells the model how to classify | Web content is treated as data; V1 and V2 catch odd results |
| **Different answer each run** | Results change between runs or after a model update | Model version pinned and recorded; results stored (C9); V2 measures it |
| **Checking the model with the model** | Automatic checks pass but the label is wrong | Only the expert sample counts as accuracy (V4 to V6) |
| **The expert trusts the model** | Seeing the model's label, the expert agrees | Labelled blind first (V5) |
| **Wrongly naming an organisation** | A public claim that a company is fossil-linked, on weak evidence | V8 |
| **Under-counting** | Missed fossil delegates make the finding too small | Recall estimated from negatives (V4, V6) |
| **Personal data** | Looking up named delegates | Organisation first; person lookup only under C6; public pages only. TI should confirm this fits its own data protection practice. |
| **Invented or misread literature** | A citation that does not exist, or a finding the paper does not make | L5 quotes and pages; W2 |

What cannot be removed: with one expert and a sample, accuracy is an estimate with a range, and rare categories (tier 3 in a small delegation) will have wide ranges. The report has to say so.

## 6. Claude setup for researchers

The workspace carries its own instructions (`CLAUDE.md`), skills and agents in `.claude/`, written so that a researcher who is not a programmer can run each stage by name and is asked for a decision at each approval point.

| Stage | Skill | What it produces | Approval |
|---|---|---|---|
| Plan | `/plan-study` | Research plan and technical requirements from a brief | yes |
| Literature | `/find-sources` | Ledger, search log, downloaded pages and PDFs, their references as candidates, reading records, index | screening criteria and the screened-in list |
| Literature | `/literature-review` | Review answering the fixed questions | |
| Writing style | `/house-style` | Style guide derived from TI publications | open questions |
| Proposal | `/research-proposal` | Proposal for the lead researcher; her returned version compared and logged | **exchange 1** |
| Definitions | `/codebook` | Categories, proxies, evidence rules, confidence levels, from the approved proposal | yes |
| Data | `/profile-dataset` | Source note and profile notebook | |
| Data | `/clean-data` | Clean tables, organisation table, cleaning log | |
| Classify | `/classify` | One evidence record per organisation | after pilot |
| Evaluate | `/validate` | Expert sample sheet, then the accuracy report | thresholds |
| Write | `/draft-report`, `/revise-report` | Draft and revision; her returned version compared and logged | named organisations; **exchange 2** |
| Check | `/check-work` | Independent review of any output | |

Agents, each doing one narrow job: `source-reader` (one source to one reading record), `evidence-finder` (one organisation to one evidence record), `org-classifier` (one evidence record to one classification; C5), `citation-checker`, `numbers-checker`, `methods-reviewer`, `decision-triage` (sorts open questions before any reach the researcher; section 11.4).

### Which model does which job

The researcher never has to choose a model. The choice follows what the work needs: the strongest model available for research design and methods critique, a standard model for extraction and checking, and Python, not a language model, for numbers. In Claude Code the choice is fixed in the setup, as in the table. In another client (section 11, S5) the closest equivalent is used and nothing is substituted silently. In every case the client, the model and its exact version are written into every record, so a result can be traced to what produced it.

| Work | Done by | Model | Reason |
|---|---|---|---|
| Plan, literature review, house style, research proposal, codebook, validation design, report | the main session | the strongest model available in the session (today Claude Fable 5.2 or Opus 5.5) | judgement-dense; errors here spread to every later stage |
| Reading one source into a record | `source-reader` | Claude Sonnet 5.5 | careful extraction across many documents |
| Finding the evidence about one organisation | `evidence-finder` | Claude Sonnet 5.5 | careful reading of web pages for about 1,250 organisations |
| Classifying one organisation from the stored evidence | `org-classifier` | Claude Sonnet 5.5 | applies the codebook to what was found, with no web access (C5) |
| Citation and evidence checks | `citation-checker` | Claude Sonnet 5.5 | a narrow check on many items |
| Recomputing numbers | `numbers-checker` | Claude Sonnet 5.5 | a narrow check |
| Sorting open questions before they reach the researcher | `decision-triage` | Claude Opus 5.5 | judges which questions carry a research choice; sees only the questions and the study's documents |
| Methods review | `methods-reviewer` | Claude Opus 5.5 | an additional critical review of the research design. It is not independent academic peer review, and the lead researcher assesses its findings |
| Passage search in the literature index | code | a small multilingual embedding model run on this computer (`sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`; checked against the test questions, L8: good for English, weak across languages) | free, private, repeatable |
| Cleaning, name matching, sampling, statistics | code | none | must give the same answer every time |

Rules: one model for the whole classification run and its second-run check, so results are comparable. A model is changed only by changing the agent's file, with the reason logged, and the affected stage is re-run. Whether Sonnet is accurate enough for classification is not assumed: the pilot (step 6) and the validation (step 8) measure it, and if it falls short the whole run moves to a stronger model.

### What runs in parallel

The sequence in section 3 is the order of dependence. Within it, independent work runs at the same time:

- data cleaning alongside the literature steps
- the house style alongside the literature review
- sources read by several `source-reader` agents at once
- organisations classified in parallel batches, each record saved as it returns
- the three reviewers in `/check-work`

Each approval point still waits for a person.

Python code sits beside what it produces. In `literature/src/rag/`, shared by all studies: downloading and extracting pages and PDFs, the ledger, the tiering of references, the literature index and search. In `unfccc/src/`, for this study only: cleaning helpers, organisation matching, sampling and accuracy statistics, and one shared chart style (`charts.py`). In `mcp_server/src/research_mcp/`: read-only access for other clients (section 11, S6). All have automated tests, including tests of downloading that run without the internet. Known gaps: text extracted from PDFs has defects (split words in widely spaced text, lost hyphens at line ends, two-column order), so quotes are checked against the PDF page; charts are static images.

## 7. Implementation plan

| Step | What gets built or done | Done when |
|---|---|---|
| 1. Setup | Workspace instructions, skills, agents, raw-data guard | Done in draft; skills are untested until first use |
| 2. Literature index | Download, extraction, passage splitting, local embeddings, search, test questions (L4 to L8) | Built and tested: the three seed sources are searchable; 22 test questions (L8) |
| 3. Sources | Screen the 134 cited references and search wider, download, read (L1 to L5) | Screening done: 51 in, 83 out. Open: approval of the screened-in list, download, wider search, reading records |
| 4. Data (parallel with 2 and 3) | Cleaning rules, scoped delegate table, organisation table for the EU (D4 to D8) | Built: delegate counts per delegation match the raw file. Open: 108 proposed name merges need a person's review |
| 5a. Review and house style | Literature review on the eight questions; style guide | Citation check passes on both |
| 5b. Research proposal | Proposal v1, sent to the lead researcher (P1 to P6) | She approves, or her rewrite is taken in and the decisions logged |
| 5c. Codebook | Codebook v1 from the approved proposal | Expert approves the codebook |
| 6. Pilot | 50 organisations through the full lookup with automatic checks | Cost, time and unknown rate reported; go or no-go |
| 7. EU run | All EU organisations; V1 to V3 | Every organisation has a record or an unknown with a reason |
| 8. Validation | Sample drawn, sent to the expert, scored | Accuracy report; thresholds applied |
| 9. Results | Tables and charts for Q1a and Q2 with sensitivity versions | Regenerated by one command |
| 9a. Graph (proposed) | Schema, graph files, static images, interactive page (G1 to G7) | Sources and organisations can be built now from the ledger and organisation table; classification links after step 7 |
| 10. All countries | Q1b, business and sector only, with its own validation sample | Decided on the pilot's cost and accuracy |
| 11. Report | Draft, independent review, revision, sign-off on named organisations, then to the lead researcher (P4) | Number and citation checks pass on the version she approves |

## 8. Decisions taken

- No labelled data exists from earlier conferences. Validation is after the run, on a sample (V4).
- The expert labelling and sign-off is arranged by Ramsey.
- Sector scheme, tier 2 and 3 evidence, subsidiaries, trade associations and the EU delegation are settled by the literature review (4.2).
- The literature gets reading records as search metadata only. No wiki.
- The crawler downloads only what it is given; linked references are screened before download.
- The lead researcher sees two full documents, the proposal and the report, and may rewrite either. Her version becomes the base.
- The proposal reads like a TI research report. The final document is an online article like the two named in the brief (Ramsey, 2026-11-24).
- References are tiered by how often and by whom they are cited, then screened; the tier does not decide relevance (Ramsey, 2026-11-24).

Dated entries are kept in `unfccc/docs/decisions.md`.

- Proposed v5: ideas from another project's design notes that are not taken over, because they serve a product that acts on its own and this is a study with a person approving each stage: a separate fast and slow processing lane, an automatic policy gate, a layer for swapping model suppliers, a trained statistical classifier, a change of framework, and a loop in which the system rewrites its own rules.

## 9. Backlog

- Change over time: earlier COP participant lists from the UNFCCC site, in the same pipeline.
- A second expert on a subset, to report agreement between raters.
- Proposed v5: a second type of study run through the same setup, to show which parts are general.
- Proposed v5: one review by a model from a different family, as a manual one-off, to see whether it finds what the present reviewers miss.

## 10. Changes for v5 (approved by Ramsey 2026-11-24, except E10)

Three sources: the independent check of proposal draft v2 (`unfccc/docs/working/reviews/proposal-v2-review-2026-11-24.md`), two outside reviews of the proposal, and a review of this setup by a second working session. Ramsey approved every item on 2026-11-24 except E10, which stays a proposal. The items are requirements from that date; sections 1 to 8 are read together with this section until they are merged into one text. Changes to an agent or a skill are logged in `decisions.md` and followed by `/run-evals`; agent models stay as they are.

One item is already done because it was a fault in existing code, not a design choice: E1.

### 10.1 Changes to existing requirements

| Requirement | Proposed change | From |
|---|---|---|
| Size table (section 1) | State both figures: 1,501 organisations after cleaning, government bodies included, and the planning estimate of roughly 1,250 to classify. | check of v2, finding 16 |
| R1 | The evidence ranking and the sample design are approved before the run, with the definitions. | proposal v2 |
| L2, L3, 4.1 | The search extensions are a scope decision for the lead researcher. 4.1 records the wider search already run. | proposal v2; finding 2 |
| K2 | The codebook holds the evidence ranking per claim and the rules for hard cases. Every rule has a number, so that a classification can name the rule it applied. | proposal v2; setup review |
| D6 | The duplicate check is run and its result recorded; the rule applies if any appear. | proposal v2 |
| D8 | An identity step before classification for similar and acronym-like names; unresolved cases stay unknown; delegates affected are reported. | proposal v2 |
| C2 | Structured evidence fields per claim: source, level in the ranking, quotation, date, rule number, stored copy where permitted. The label is chosen from the codebook's list or the case is deferred; free-text labels are not accepted. | proposal v2; setup review |
| C2 to C4 | Every record carries one status from a fixed list: confident, uncertain, abstained (looked, could not decide), confirmed negative (looked, found evidence of no link), or failed (the lookup did not run). "Nothing found" and "did not look" are never the same value. | setup review |
| C3 | Confidence follows from the level of evidence, by a written rule. | proposal v2 |
| C5 | Finding evidence and classifying are separate steps, each logged. The `org-researcher` agent, which did both in one step, is split accordingly. **Done 2026-11-24**: `evidence-finder` (finds and stores the evidence, gives no label) and `org-classifier` (applies the codebook to the stored evidence, no web access), both Sonnet, each with an eval case; `org-researcher` retired and its case kept frozen (`evals/README.md`). | proposal v2; setup review |
| C6 | A match of a name to an organisation needs two agreeing details. | finding 17 |
| C8 | The pilot also measures the expert's time per organisation. | proposal v2 |
| C9, A1 | The organisation table is a named output; every count is generated from it. | proposal v2 |
| V2 | Reported as repeatability, apart from accuracy. Run two ways on a subset: with a new search and with the stored evidence. Cases where runs disagree are reviewed apart and kept out of the estimates. | proposal v2; findings 5, 18 |
| V4 | Groups defined by the model's result; tier groups reviewed in full; sizes fixed by a written rule once group sizes are known; no fixed minimum of 30 in 15 groups. | proposal v2 |
| V5 | The expert labels every case before seeing the model's label, tier cases included, seeing the stored evidence; 30 cases researched unaided, done first, reported apart. | proposal v2; findings 4, 19 |
| V6 | Weighted by chance of selection; per organisation and per delegate; limits on tier-by-tier estimates stated; pilot organisations outside the estimates. | proposal v2; finding 21 |
| V7 | The rule for what happens below the threshold is the one in proposal section 6.5. The threshold for cases found applies to business and to "any tier"; per-tier figures are indicative. | findings 3, 7 |
| V8 | The sign-off on a named organisation is tied to a fingerprint of the exact record signed. If the record changes afterwards, the sign-off no longer holds. | setup review |
| A2 | Ranges from unknowns are labelled apart from margins of error from sampling. | proposal v2 |
| A3 | The list of versions run side by side is fixed before results are seen; it includes a check with one delegation left out. | proposal v2; finding 23 |
| P1, section 8 | A provisional proposal may be written before the literature review is finished. Sector scheme, tier evidence, subsidiaries, trade associations and the EU delegation are decisions for the lead researcher, informed by the review, not settled by it. | finding 2 |
| W1 (`/check-work`) | The overall verdict follows from a fixed rule on the findings, not from the reviewer's summary. `methods-reviewer` gives each finding two separate marks: how well it is evidenced, and how much it matters. | setup review |

### 10.2 New requirements

| ID | Requirement | From |
|---|---|---|
| R9 | **Decision register.** Every design decision has one numbered entry: the options, the recommendation, who decides, by when, and its state (open, decided, superseded). The proposal's decision list and `decisions.md` are generated from it or checked against it. | setup review |
| R10 | **Uncertainty register.** One list of what is not known and how each item is handled: unknown organisations, unresolved names, unread sources, unmeasured accuracy. Each report states which items remain. | setup review |
| L10 | **Coverage and quality apart.** The literature tables show, for each question, how much of the screened-in literature has been read, and separately what kind of source each is (peer-reviewed, preprint, NGO report, official). To be agreed with the session that maintains the library. | setup review |
| C10 | **Run record.** Date, model, rule version, wording of the instructions, settings; no change during a run. **Done 2026-11-24 for eval runs** in `evals/score.py --record`: each run folder gets `run-record.json` (date, client, model of each agent, fingerprints of the agent files, `CLAUDE.md`, `/run-evals`, cases and scorer), and a run whose instructions changed while it ran does not pass; tested both ways in `evals/tests/test_score.py`. **Still to do for classification runs**, with the pilot (step 6). | proposal v2 |
| C11 | **Fixed test set.** 50 organisations, apart from the expert sample, run again after any change to rules, wording or model. | proposal v2 |
| C12 | **Language.** Search in the language of the nominating country is required; coverage is reported by country. | proposal v2 |
| C13 | **Attributes.** "Represents commercial interests" as a yes/no attribute (if decision 25 is approved); a tier for any organisation (if decision 15 (b) is approved); tier 2 in two parts (if decision 20 is approved); where two tiers are met, the highest is recorded. | proposal v2; finding 10 |
| C14 | **Independent evidence.** Two sources count as two only if one does not repeat the other. A press release and a news item copied from it count once. | setup review |
| W5 | **Design critic.** Before a plan, proposal or codebook goes for approval, a reviewer who has not seen the reasoning is asked only how the design fails: what it returns when it finds nothing, and what happens when a step is confidently wrong. | setup review |
| E1 | **Not run is not failed, and is not passed.** An agent with no answer in a test run is recorded as "not run". A run in which nothing was run does not pass. **Done 2026-11-24** in `evals/score.py`, with tests in both directions. | setup review |
| E2 | **Proposal test case.** The case with 15 planted flaws in a research proposal becomes part of the scorer: pass at 11 found, with seven that must be found. **Done 2026-11-24**: the case is in `evals/cases/methods-reviewer-proposal/` and scored by `evals/score.py`, with tests that a full answer passes and that a missed required flaw or a quote not in the review fails. | setup review |
| E3 | **Repeat runs.** Each case is run three times. Results are given as "found in k of n runs" with the range, and "found every time" is kept apart from "found at least once". **Done 2026-11-24** in `evals/score.py` (scoring a folder of runs writes `repeats.json`: passed in k of n runs, the range found, and each item as found every time, in some runs, or never), with tests, and `/run-evals` runs the set three times. First used on run 2026-11-24d: every case passed in 3 of 3 runs except the historical case (passed in 2 of 3; 11 to 13 of 18). | setup review |
| E4 | **The tests are out of the agents' reach.** The cases and the scorer cannot be changed by an agent under test; cases are frozen and fingerprinted, and a changed case is a new case. **Done 2026-11-24**: `evals/fingerprints.json` holds a fingerprint of every case file and the scorer, and `evals/tests/test_fingerprint.py` fails when one has changed, been added or been removed; the guard `.claude/hooks/protect_evals.py` blocks any agent from editing the cases, the planted answers, the scorer and the fingerprints, with tests in `evals/tests/test_setup.py` that it blocks an agent and allows the main session (`evals/README.md` part 6). Not covered: shell commands (E10), and an agent reading the planted answers, which rests on written instruction. | setup review |
| E5 | **Kinds of test.** Kept apart in `evals/README.md`: cases that must never fail again; hard cases that measure the limit; and past real documents with known problems. **Done 2026-11-24**: the table "Three kinds of case" in `evals/README.md`. | setup review |
| E6 | **What is reported first.** The headline result is the number of answers that were confident and wrong. Misses are weighted by how much they matter. **Done 2026-11-24** in `evals/score.py`: the headline (confident wrong answers, then misses with a required item counted three times) is printed before any per-agent score and saved in `summary.json`, with tests. | setup review |
| E7 | **Small end-to-end test study.** About 20 invented organisations taken through every stage, with one planted error per stage, to show that each stage's check catches its error. **Deferred 2026-11-24**: the stages it would test from the codebook on (classify, validate, report) are not yet fixed, and a test study built now would have to be rebuilt once the codebook is approved and the pilot has run. To be built with step 6. | setup review |
| E8 | **Historical test.** Proposal draft v1 and the problems the outside review found in it become a test case. The reviewer under test is never shown the outside review. **Done 2026-11-24**: `evals/cases/methods-reviewer-v1/`, a frozen copy of v1 and 18 problems from the outside review (5 required, pass at 12), scored by `evals/score.py` with tests; `/run-evals` tells the reviewer not to open the reviews folder or the study folder. | setup review |
| E9 | **Rules a machine can decide are enforced by a machine.** Where a rule can be checked without judgement (a number not in a generated file, an edit to a raw file, a missing source), it moves from the written instructions into an automatic check, tested both for blocking what it should and for allowing what it should. **Done 2026-11-24 for the three examples**, each with a test that it blocks and a test that it allows: an edit to a raw file (the guard on raw files, tested in `evals/tests/test_setup.py`); a number not in a generated file (literature counts in `evals/tests/test_numbers.py`, data figures in `evals/tests/test_output_numbers.py`, S10); a source cited but not read (`evals/tests/test_library.py`). Not covered: shell commands (E10), and a number labelled provisional entering a formal output (S10). | setup review |
| E10 | **Housekeeping.** The workspace is put under version control with a list of files to leave out. The guard on raw files also covers shell commands; it now covers file edits only. Needs Ramsey's explicit go-ahead, since it changes the workspace's settings. | setup review |

### 10.3 Lines for the risk table (section 5)

| Risk | What it looks like here | Control |
|---|---|---|
| **"Did not look" read as "found nothing"** | A failed lookup is counted as a non-fossil organisation | Status on every record (C2 to C4 as amended) |
| **One source counted twice** | Two pages that repeat the same press release are taken as confirmation | C14 |
| **A sign-off outlives the record** | An organisation is approved for naming, then its record changes | V8 as amended |
| **The model invents a category** | A label that is not in the codebook | Choice from the list or deferral (C2 as amended) |
| **A test that cannot fail** | An agent that was not run shows as passed, or a case is adjusted until it passes | E1, E4 |
| **A lucky run** | A reviewer finds a flaw once and the test is taken as passed | E3 |
| **A design nobody attacked** | Reviews check the text against sources but not how the design behaves when a step fails | W5 |
| **A rule that relies on being remembered** | A written instruction is skipped in a long session | E9 |

### 10.4 Steps for the implementation plan (section 7)

| Step | What gets built or done | Done when |
|---|---|---|
| 1a. Scorer | E1 | Done 2026-11-24; 365 tests pass |
| 1b. Tests of the reviewers | E2, E3, E5, E6, E8 | `/run-evals` reports three runs per case, with the proposal case and the historical case included. **Done 2026-11-24**, run `evals/results/2026-11-24d/`: no confident wrong answer in any run; the hard proposal case 15 of 15 in every run; the historical case passed in 2 of 3 runs (13, 12 and 11 of 18, all five required problems found every time; H5, H10, H12 and H15 never found) |
| 1c. Protection | E4, E9, E10 | Each automatic check has a test that it blocks and a test that it allows; Ramsey has approved the settings change. **Partly done 2026-11-24**: E4 and E9 built with blocking and allowing tests; E10 waits for Ramsey's go-ahead |
| 1d. Registers | R9, R10 | Proposal section 9 and `decisions.md` agree with the register |
| 3a. Literature tables | L10 | Agreed with the library session; columns in the screening export |
| 5b. Research proposal | W5 before sending; second check of the revised v2 | Design critic's points answered in the changes file |
| 5c. Codebook | K2 as amended (numbered rules), C13 | After the lead researcher's reply |
| 6. Pilot | C2 to C5 as amended, C10 to C12, C14; `org-researcher` split (done 2026-11-24: `evidence-finder` and `org-classifier`) | After the codebook is approved; `/run-evals` after the agent change |
| 6a. End-to-end test | E7 | Each stage's check catches its planted error. **Deferred 2026-11-24** to step 6, with E7 (reason there) |
| 8. Validation | V2, V4 to V8 as amended | After the lead researcher approves the sample design |

Order proposed: 1b first (it measures the reviewers the proposal depends on), then W5 and the second check of v2, then send the proposal. Steps 5c and later wait for the lead researcher. The second outside review's advice was to stop adding structure and show performance; 1b and 6a are the items that do that.

## 11. The workspace: portability and rules (added 2026-11-24)

Source: an outside review of `CLAUDE.md`, pasted by Ramsey on 2026-11-24 with the request to update the rules file, make the workspace usable over MCP, and bring this plan into line. The review is a reviewer's suggestions, not a source of facts about the study.

This section is about the workspace, not the research design. Two kinds of item are kept apart:

- **Built**: changes to the setup, made on 2026-11-24 at Ramsey's request. They are logged in `decisions.md`. Agent models are unchanged.
- **Proposed**: anything that touches this study's records, codebook or method, or that lets a client write. None of these is approved, and nothing is built on them.

### 11.1 Built

| ID | What | Where | Still to do |
|---|---|---|---|
| S1 | **One short entry point.** `CLAUDE.md` holds the rules that apply to every task; detail is in five documents. | `CLAUDE.md`, `.claude/docs/` | |
| S2 | **Rules reworded or added.** Traceable evidence (source, address, access date, page, quotation, the claim supported). Positive, negative and unknown are three outcomes; finding nothing is "unknown". Every reported number is reproducible, and exploratory numbers are labelled provisional. Three kinds of approval, each tied to the exact version approved; a material change needs renewed approval; silence is not approval. Reuse the process, not another study's conclusions. Shared tools are not changed for one study's problem. The claim that the rules make the work defensible without peer review is replaced by what they do give (section 2). | `CLAUDE.md` rules 2, 4, 6, 7, 13, 14 | Done 2026-11-24: `/run-evals` run 2026-11-24d, three runs |
| S3 | **A new study starts from a template**, never from this study's folder: brief, decision log, technical requirements, codebook and proposal, as outlines with no content from this study. | `templates/study-template/`, `.claude/docs/new-study-guide.md`, `/plan-study` | Try it: see S8 |
| S4 | **The methods reviewer is described as what it is**: an additional critical review, not independent academic peer review; the lead researcher assesses its findings. | `.claude/agents/methods-reviewer.md`, section 6, README | Done 2026-11-24: `/run-evals` run 2026-11-24d; `methods-reviewer` found 7 of 7 and 15 of 15 in every run, the historical case 11 to 13 of 18 |
| S5 | **The assistant does not assume where it is running.** At the start of a task it checks which files, tools and permissions it has, treats the workspace as read-only unless asked to change it, and says what the client cannot do. The client is recorded with the model and version in every result. | `CLAUDE.md` ("Using this repository", rule 11), `.claude/docs/client-setup.md` | Done for eval runs 2026-11-24: the run record (C10) carries the client. Still to do for classification records, with step 6 |
| S6 | **Read-only access from Claude Desktop and other clients** (an MCP server; G8 in part). Seven tools: the working rules, the list of studies, one study's documents, its decisions, search across study documents, literature search, one source's record. It cannot write, it never serves a `data/` folder, code or notebooks, and it has automated tests of each refusal. A client connected this way gets the tools, not the rules, so the first tool returns the rules and the set-up note says to read them first. | `mcp_server/`, `.claude/docs/client-setup.md` | Connect it in Claude Desktop (one setting on Ramsey's computer; not done by the assistant) |

### 11.2 Proposed, not approved

| ID | Proposal | Who decides |
|---|---|---|
| S7 | **Three outcomes and the five statuses.** Section 10 (C2 to C4) gives every record one of five statuses. The rules file names three outcomes. Proposed mapping, to be fixed in the codebook: "confirmed negative" is negative; "abstained" and "failed" are unknown, each with its reason; "confident" and "uncertain" describe a positive or a negative finding and its strength. The record also lists what was searched, so that "unknown" can be told from "not looked for". | Lead researcher, with the codebook |
| S8 | **Two trials of portability**, before anything more is built: (a) a new Claude Desktop session, with only the MCP server, answers questions about this study and its sources, and its answers are compared with the files; (b) a separate Claude Code session creates a small new study from the template, and the result is checked for anything carried over from this study. | Ramsey |
| S9 | **Tools that write** over MCP: create a study from the template; run a check. Not built. Each would need explicit authorisation on every use and a test that it cannot touch raw files or another study. | Ramsey |
| S10 | **Provisional numbers checked by a machine** (an addition to E9): a check that a number in a proposal or report is found in a generated file, and that a number labelled provisional is not in a formal output. **Partly done 2026-11-24** in `evals/tests/test_output_numbers.py`: every data figure in a study's `proposal/numbers.md` table of measures is checked both ways against the generated file it names (a number not in the file fails, and so does a measure named but not written), with tests on an invented table that it blocks and allows; for this study it covers 4 tables and 31 rows. Not done: the provisional half, since there is no register of exploratory numbers to check against yet; and the check that the numbers file agrees with the proposal text. | Ramsey |
| S11 | **Approvals tied to a fingerprint of the document** (an extension of V8 from organisation records to documents, and part of R9): the decision log records a fingerprint of the exact file approved, so a later change shows. | Ramsey |
| S12 | **A `studies/` folder** holding `unfccc/` and later studies. Not done: it would change every path in this study's documents and code for no gain in method. Reconsider when a second study exists. | Ramsey |
| S13 | **Access for people who do not have this computer** (a shared repository or a hosted server). Depends on E10 (version control) and on deciding which files may leave this computer: downloaded sources, and data that names people. | Ramsey, with TI |

### 11.3 Demonstration and release of read-only access (added 2026-11-24; proposed, not approved)

Asked by Ramsey on 2026-11-24: what the MCP server should give access to, whether the search index exists, and what is missing before a demonstration on Ramsey's computer and later access for a colleague.

**What exists today.**

- *Literature.* A search index of the sources read so far: 184 sources, 17,399 passages (`literature/index/meta.json`, built 2026-11-24 at 20:24; figures updated 2026-11-25). Each passage is stored with a vector, a list of numbers that stands for its meaning, so a search finds passages by meaning as well as by exact words. It covers only sources that have been read into the library, not those screened in and not yet read.
- *Study documents.* No vectors. The server searches the study's documents by matching words. With a few dozen documents this is enough; S19 says when to reconsider.
- *Not served, by design:* any `data/` folder, files named `delegates*`, code, notebooks, the downloaded PDFs and pages themselves.

**Recommended scope for the demonstration and the first release:** the literature and the study documents the server already serves (`docs/`, `report/`, `outputs/`; the proposal is in `docs/`). Literature alone would hide the decision log and the proposal, which are what a researcher asks about first. The study's data stays out. One caution: the proposal is an unapproved draft, so a client must be told so (S16).

| ID | Proposal | Why | Who decides |
|---|---|---|---|
| S14 | **A stale or missing index is reported, not a crash.** If the index files disagree with each other (as happened on 2026-11-24 while the library was being rebuilt), literature search returns a plain message saying the index is being rebuilt, and the other tools go on working. With a test. **Done 2026-11-24** in `mcp_server/src/research_mcp/workspace.py`; tested for a missing and a half-built index in `mcp_server/tests/test_research_mcp.py`. | Today the search fails with an error the client cannot explain. In a demonstration that reads as "the tool is broken". | Ramsey |
| S15 | **The index says how fresh it is.** Each literature search result carries the date the index was built and the number of sources in it, and the server says when a source has a record but is not yet in the index. **Done 2026-11-24** in the same file, with tests. | A client must not present "nothing found" as "nothing exists" (rule 4) when the index is behind the library. | Ramsey |
| S16 | **Every document is served with its status.** Draft, sent, approved or superseded, taken from the decision log, on `get_study` and on each search result. **Done 2026-11-24**: read only from the table "Document status" in `docs/decisions.md`; a document not in it is served as "not recorded, treat as a draft"; an unknown status word is not taken as a status. With tests. | Proposal draft v2 is not approved and carries literature counts that are out of date. A client that quotes it without that label misleads. | Ramsey |
| S17 | **A fixed set of demonstration questions with known answers**, about ten, asked through the server from a new Claude Desktop session and compared with the files. This is trial (a) of S8, made repeatable. Includes two questions whose right answer is "not in the repository" and one that asks for the delegate list, which must be refused. **Built 2026-11-24, reworked the same day** after Ramsey's feedback that the first set read as repository tests rather than researcher questions: fifteen questions in `mcp_server/demo-questions.json` (D1 to D15), in the order a new researcher would ask them, of five kinds (answerable, partial, not recorded, restricted, research required). Two layers: layer 1, the server, where `mcp_server/tests/test_demo_questions.py` runs each question's tool calls and checks the known text or the refusal; layer 2, the answer, where each question states what a good reply does, which documents it cites and what it must not do, for a person to judge in Claude Desktop. Further tools that would make some questions easier (study status, evidence search, literature record, document comparison, validation results, research gaps) are written down as proposals only, not built. **Still to do:** ask them from a new Claude Desktop session on Ramsey's computer and compare (trial (a) of S8). | Shows performance, not structure. Repeated before each release. | Ramsey |
| S18 | **A release checklist before another person gets access:** tests and evals pass; S14 to S17 done; no file that names people is reachable (the existing refusal tests, plus a scan of `outputs/` and `report/` for name lists); the published copies of sources are not handed on unless their licence allows it, only the records with quotations and the web addresses; the person receives the set-up note and is told the access is read-only and what is a draft. | Access for a second person is a publication-sensitive step, even when read-only. | Ramsey, with TI for what may leave this computer |
| S19 | **How the colleague gets access**, in order of effort: (1) Ramsey shares the screen or runs the questions for them, nothing leaves the computer; (2) a copy of the folder without `data/`, `literature/pdfs/` and `literature/pages/`, with the index, used on their computer with their own Claude app; (3) a hosted server with a login. Option 2 is the proposed first release. Option 3 needs a login, a log of who asked what, and a host, and is S13. | The server runs on the computer that holds the folder; there is no remote access today. | Ramsey |
| S20 | **Vectors for study documents: not now.** Reconsider when a study has a report and outputs large enough that word search misses passages, or when a second study exists. If built, it reuses the literature index code and gets the same freshness rule as S15. | Avoids building before the need is shown. | Ramsey |
| S21 | **A record of what was asked** (date, tool, question, number of results; no answer text), kept locally, switched on for the demonstration. | Shows what researchers actually ask and where search fails. Needs agreement because it records use. | Ramsey |
| S22 | **Further read-only tools, only where the Desktop trial shows a need.** Proposed with the demonstration questions: study status, evidence search, literature record, document comparison, validation results, research gaps. Before any is built, the trial (S17) must show a question the seven existing tools answer badly; the tool is then built for that question, with a test that the question now gets its known answer. Validation results waits until `/validate` has run, as there is nothing to return before. Study status and research gaps would only repeat the decision log unless the log keeps them in a fixed table, as S16 does for document status. *Proposed, not approved.* | A tool nobody needs is one more thing a client can misuse. The trial shows which gaps are real. | Ramsey |
| S23 | **A scan for name lists in what the server serves**, the part of S18 not yet built: a test that no served file in `outputs/` or `report/` holds a column or list of people's names (for example a column headed name, first name, surname or delegate, or many rows matching the participant list). Can be built before the review comes back. *Proposed, not approved.* | Today only the `data/` folder and files named `delegates*` are refused. A table written to `outputs/` by mistake would be served. | Ramsey |
| S24 | **The decision log's file references stay true.** A test that every file path written in `docs/decisions.md` either exists or is marked as moved or not expected. On 2026-11-24 eight references pointed to files that had moved (one log row now records where they are). *Proposed, not approved.* | The log is what a client reads first through the server; a dead reference sends it looking for a file that is not there. | Ramsey |
| S25 | **Generated files only in `outputs/`.** A test that `<study>/data/` holds only `raw/` and `derived/`. On 2026-11-24 two generated tables were found in `unfccc/data/outputs/`, which the server does not serve and rule 6 does not point to (removed the same day, see the decision log). The test is *proposed, not approved.* | A number's file must be where the checks and the server look for it. | Ramsey |
| S26 | **Code style checks become part of the tests**, once the cleaning and literature code is no longer being changed by other sessions. On 2026-11-24 `uv run ruff check` reports 460 findings, almost all long lines in `unfccc/src/` and `literature/`; `evals/` and `mcp_server/` are clean. Then they are fixed in one pass and kept at zero. *Proposed, not approved.* | Fixing them now would collide with work in progress; leaving them unmeasured lets the number grow. | Claude, reported to Ramsey |
| S27 | **The answers to the demonstration questions are graded, not only the server's replies** (layer 2 of S17), after the first Desktop trial: a second model reads each reply against the question's stated must, cite and must-not fields and quotes the reply for each verdict, as the methods review is graded in `/run-evals`. A person still reviews the grades. *Proposed, not approved.* | Makes the trial repeatable before each release (S18) without a person reading fifteen answers each time. | Ramsey |

### 11.4 Routing and review loops for the researcher (added 2026-11-24)

Asked by Ramsey on 2026-11-24: when the researcher works through the MCP server, the assistant should know which workflow a request needs and which review steps make the result trustworthy; and a separate reviewer should sort questions and decisions, so the researcher is asked only what needs their subject knowledge, not choices about the AI setup.

| ID | What | Where | Status |
|---|---|---|---|
| S28 | **A workflow guide.** For each kind of request: the workflow in Claude Code, the checks before it counts as done, what only the researcher decides, and what can be done in Claude Desktop. The seven checks named in plain words (source check, design critic, independent check, numbers check, decision sorting, approval record, eval run). An output whose check did not run is called unchecked. The guide is served by the MCP server, and the server's opening instructions tell the client to read it. | `.claude/docs/research-workflows.md`, `CLAUDE.md`, `mcp_server/src/research_mcp/` (instructions, guide list), with tests that the guide names only workflows and agents that exist and covers every workflow | Built 2026-11-24. Still to do: `/run-evals` (`CLAUDE.md` changed) |
| S29 | **Questions are sorted before they reach the researcher.** Three groups: decided by the assistant (how to build, run or check), the researcher's (definitions, thresholds, scope, sample, evidence, wording, naming, approval), and Ramsey's (setup, access, anything leaving this computer). A technical question that hides a research choice is split. Research questions go to the researcher at most three at a time, each with options, a recommendation and its reason, what changes, and what waits. In Claude Code a separate agent does the sorting from the questions and the study's documents only, not the reasoning that produced them; in Claude Desktop the assistant does it in a separate pass and says so. | `.claude/agents/decision-triage.md` (Claude Opus 5.5), `research-workflows.md` section 3, `CLAUDE.md` ("Who you are working with") | Built 2026-11-24. Still to do: an eval case with planted mis-sorted questions (for example a year limit worded as a technical question, a model choice worded as a research question), scored like the other agents |
| S30 | **Guided starting points in Claude Desktop** (MCP prompts): ready-made requests such as "where does the study stand", "what does the literature say about …", "prepare my questions", each of which reads the workflow guide first. *Proposed, not approved.* | `mcp_server/` | Ramsey |
| S31 | **The design critic as its own agent** (W5). Until it exists, `methods-reviewer` is asked the two critic questions in addition to its own. *Proposed, not approved.* | `.claude/agents/` | Ramsey |

### 11.5 Lower cost, shorter documents (added 2026-11-24, asked by Ramsey)

| ID | What | Where | Status |
|---|---|---|---|
| S32 | **The organisation look-up is a script.** The two steps of `evidence-finder` and `org-classifier`, same models and prompts, run from code. Code decides what needs no judgement: which addresses may be opened, whether a quote is on its page, whether a label and rule exist, confidence by level of evidence, what an empty or failed look-up becomes. Runs resume; classification can go as a batch at half price; every step prints its cost before it starts. | `unfccc/src/lookup/` | Built, 35 tests; not yet run on real organisations |
| S33 | **Haiku reads every result** and flags a quote that does not support the match or the label. It never changes a record; flags go to a person. | `lookup check` | Built; no eval case yet |
| S34 | **The codebook carries a block for the script** ("Labels for the script"). The script refuses a version below 1.0 unless `--draft`, whose results are kept apart. | `/codebook`, `lookup/codebook.py` | Built |
| S35 | **A source-reader starts from the passages that matter** (`rag chunks`), about a third of a long source, and searches the full text for anything missing. Measured on sources already read: about 40% of the words keep 68–69% of the quotes a full reading chose. | `literature/src/rag/chunks.py`, `source-reader` | Built; eval needed |
| S36 | **Which evals a change needs** is computed from what changed since the last passing run, at no cost. | `evals/what_to_run.py` | Built |
| S37 | **Length budgets.** The proposal: about 5,000 words of main text, never over 6,500, with a budget per section; a report 1,500–3,000. A new version is an edit, not a rewrite. Checked with `evals/doc_length.py` before handing over. Proposal v3 is 23,333 words of main text. | `/research-proposal`, `/draft-report`, `CLAUDE.md` | Built; proposal v3 not yet cut |
