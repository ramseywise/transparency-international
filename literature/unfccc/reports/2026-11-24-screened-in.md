# Screened-in sources: relevance, reading batches and the limit of 50

Written on 2026-11-24 (Claude Code, model claude-fable-5-2; source readers and screeners: sonnet), and updated the same day after batch 2 and the second screening round. Batch 4 (open copies through OpenAlex, 21 kept) was added the same day by Claude Code, model claude-opus-5-5; readers and relevance check: sonnet.

## What this file is

On 2026-11-24 all 2,439 undecided candidates were screened and 280 were kept in. Seven of those turned out to be copies of sources we already had and were taken out again, and two were replaced by a better address for the same work. This file sorts what remains by **relevance**: what each source is for, and whether it adds something or repeats what we already hold.

**How far to trust the relevance column.** For batch 1 it rests on reading the source. For everything else it rests on the title, the address and the screening reason only; nothing has been read. It is a reading order, not a finding.

## The limit of 50

**Withdrawn.** Ramsey decided later on 2026-11-24 that there is no hard limit of 50 (recorded in `unfccc/docs/decisions.md`). The text below is kept as the record of the earlier decision.

Ramsey decided earlier on 2026-11-24 that the literature review should hold no more than 50 papers, read in batches of 25.

My reading of that decision, to be confirmed: the limit applies to the works discussed in the literature review itself. Before batch 1 we held 44 read sources, which Ramsey confirmed on 2026-11-24 are kept. They are: 28 on the substance (Q1: 10, Q2: 11, context: 4, TI's own: 3) and 16 on method. If the 16 method sources are cited in the methodology and not counted, there are at most **22 places** left for new works. If they are counted, there are 6. Which works take the places is decided after reading, not before.

Sources that are not literature (data, reference lists, official rules, earlier counts) do not use a place. They are cited where they are used.

## What the roles mean, and why so many are reports

| Role | What it is for | Counts toward the 50? |
|---|---|---|
| Literature review candidate | Academic work that could be discussed in the review | Yes, if chosen after reading |
| TI's own publication | For consistency with TI's terms and earlier positions | Yes, if discussed |
| Earlier count or report (advocacy or news) | A previous count to compare ours with, or a position | No |
| Data or reference list | A list of companies or participants used to build or check the dataset | No |
| Official rule or document | UNFCCC or EU rules and definitions | No |
| Method reference | How to classify, or how to check a classification | No, under my reading above |

Many of the sources are reports because, on this subject, the counting has been done by campaign groups and journalists, not by academics. Those reports matter in two ways: as the earlier counts our results will be compared with, and as the lists and counting rules the dataset is built from. Few of them belong in the literature review. Reading batch 1 confirmed this.

## Gaps in what we hold, which the batches are chosen to fill

- Business and NGO attendance at COPs over time (academic).
- How delegations are made up, how that changed, and what explains it.
- Counting an industry from participant lists in other sectors or other UN bodies.
- A definition of "access".
- The lobbyist counts before COP28, and the original counting method.
- Reference lists of fossil fuel companies, and official classifications of economic activity and of company groups.
- Checking model labels against imperfect human labels.
- TI's own integrity rules for national delegations.
- Obstruction and business presence outside the US and EU.

## Batch 1: downloaded and read on 2026-11-24 (25)

Of the 25, 21 were obtained and read into a record; 4 could not be obtained. Of the 21 read, four were only a landing page and one only an abstract. What the records say is retrieved from the sources by a reader agent; it has not been independently verified.

| Work | Role | Outcome of the download | Adds or reinforces | Library id |
|---|---|---|---|---|
| Analysis: How delegations at COP climate summits have changed over time | Earlier count or report (advocacy or news) | Read in full | Adds. Delegation sizes over time; warns that the named Party lists leave out overflow badge holders in early years, and that Parties give badges to NGOs. Nothing on business or fossil fuel presence. | `carbonbrief-analysis-how-delegations-at-cop-climate-summits-have-chang` |
| The global health community at international climate change negotiations | Literature review candidate | Not obtained (publisher refused, 403) | Would add: counting one industry's delegates from participant lists at another UN treaty. Needs supplying by hand. | `doi-10-1136-bmjgh-2024-015292` |
| Decision influence and the link to internal modalities of delegations to conferences of the parties | Literature review candidate | Not obtained (page not found, 404) | Would add: who sits in delegations and why. Needs supplying by hand. | `ac-ej-20goodwin-20jel-20article` |
| The determinants and importance of states' attendance at conferences of the UNFCCC | Literature review candidate | Read in full (47 pages), but it is a conference draft marked "Please do not cite without permission" | Adds: delegation sizes 1995 to 2014 and what explains them (OPEC members send larger delegations). Cannot be cited as it stands; look for a published version. | `peio-102-80-1443623897416-kaya-schofield-09302015` |
| Transnational Advocacy over Time: Business and NGO Mobilization at UN Climate Summits (Hanegraaff 2015) | Literature review candidate | Not obtained (publisher refused, 403) | Would add: business and NGO attendance at COPs over time, the closest academic precedent for Q1. Needs supplying by hand. | `doi-10-1162-glep-a-00273` |
| UNFCCC list of admitted NGOs | Official rule or document | Page came back empty | Would add: the official list of admitted observer organisations, usable as a reference list. Needs supplying by hand. | `unfccc-list-of-admitted-ngos` |
| Anonymised list of fossil fuel lobbyists (Kick Big Polluters Out) | Data or reference list | Not obtained (the spreadsheet is no longer there, 410) | Would add: the Kick Big Polluters Out list behind their count. Ask the publisher. | `google-edit-322e50` |
| InfluenceMap COP Attendee Database | Data or reference list | Landing page only (153 words) | Points to a COP31 attendee database and a methodology page (the size given, over 1,000 companies and 330 industry groups, is for InfluenceMap's whole database). The methodology page is the real source and has not been fetched. | `influencemap-corporateinfluencedatabase` |
| Investigation: fossil fuel lobbyists attend UN climate talks more than 7,000 times (Corporate Europe Observatory) | Earlier count or report (advocacy or news) | Read in full | Adds: the longest count series (at least 7,200 passes, COP9 to COP27) and how names were matched to fossil fuel companies. | `corporateeurope-investigation-fossil-fuel-lobbyists-attend-un-climate` |
| Europe brings gas lobbyists to COP29 to strike deals (unsure) | Earlier count or report (advocacy or news) | Read in full | Reinforces: 113 fossil fuel lobbyists in EU government delegations at COP29, quoted from Kick Big Polluters Out. | `fossilfreepolitics-europe-brings-gas-lobbyists-to-cop29-to-strike-deal` |
| EU Accused of Inviting Fossil Fuel Executives to COP28 Under False Pretences | Earlier count or report (advocacy or news) | Read in full | Adds one point: the Commission's position that company staff on Party overflow badges were not part of the EU delegation. Bears directly on how we read overflow badges. | `desmog-eu-accused-of-inviting-fossil-fuel-executives-to-cop28-under-fa` |
| Release: Kick Out The Suits, COP30 (Kick Big Polluters Out) | Earlier count or report (advocacy or news) | Read in full | Adds: the COP30 count (1,602; about 599 on Party overflow; 164 on government badges) and the definition of "fossil fuel lobbyist". The method page it links to has not been read. | `kickbigpollutersout-release-kick-out-the-suits-cop30` |
| Our methodology for the COP27 fossil fuel lobbyists analysis (Global Witness) | Method reference | Read in full | Adds: the three-test counting rule behind the lobbyist counts; self-declared affiliation only, so the count is a floor. | `globalwitness-our-methodology-for-the-cop27-fossil-fuel-lobbyists-anal` |
| Banking on Climate Chaos: company list 2026 | Data or reference list | Read (pages 1 to 36) | Adds: a list of 859 fossil fuel expansion companies. No country or parent-company column. | `bankingonclimatechaos-companies-2026` |
| Banking on Climate Chaos 2026 methodology | Method reference | Read in full (10 pages) | Adds: a written rule for what makes a company fossil (on an Urgewald list, or in the GEM or Enerdata data, or a Bloomberg fossil segment) and how subsidiaries are treated. | `bankingonclimatechaos-methodology-2026` |
| Regulation (EEC) No 696/93 | Official rule or document | Not obtained (the EU law site did not return the page) | Would add: the legal definition of an enterprise group. Needs supplying by hand. | `europa-eng` |
| Overview - NACE - Eurostat | Official rule or document | Landing page only | The classification of economic activities itself sits in linked documents that have not been fetched. | `europa-overview-2` |
| Carbon Majors database | Data or reference list | Landing page only | Says the database covers 178 producers. The methodology and the list are on other pages. | `carbonmajors-index` |
| https://gogel.org/. | Data or reference list | Landing page only | Says the list covers about 1,900 oil and gas companies (published 10 November 2026). The list needs registration. | `gogel-home` |
| Codebook LLMs: Evaluating LLMs as Measurement Tools for Political Science Concepts | Method reference | Read in full | Adds: how to write a codebook for a language model and test it; smaller open models followed exclusion rules poorly. No tests on classifying organisations. | `doi-10-1017-pan-2025-10017` |
| Automated Annotation with Generative AI Requires Validation (Pangakis, Wolken, Fasching 2023) | Method reference | Read (pages 1 to 20), preprint | Reinforces with numbers: performance must be validated task by task (it ranged from very poor to very good across 27 tasks). | `arxiv-2306-00176-2` |
| Transparency International letter to UNFCCC and COP30 Presidency on integrity reforms for undue influence | TI's own publication | Not obtained (the site's robots.txt refuses automated download) | TI's own letter. Please ask the TI colleague for the file. | `transparencycdn-transparency-internationals-letter-to-unfccc-and-cop30` |
| Integrity Checklist for National Delegations to COP (Transparency International) | TI's own publication | Not obtained (the site's robots.txt refuses automated download) | TI's own integrity checklist for national delegations: probably the most relevant single document for the recommendations. Please ask the TI colleague for the file. | `transparencycdn-integrity-checklist-for-national-delegations-to-cop-tr` |
| Corporate capture of the IMO (InfluenceMap) (unsure) | Earlier count or report (advocacy or news) | Summary page only | Adds a comparison: industry inside state delegations at the UN shipping body ("31% of nations were represented in part by direct business interests"). Not comparable in method. | `influencemap-corporate-capture-of-the-imo-902bf81c05a0591c551f96502062` |
| What is access? A discussion of the definition and measurement of interest group access (unsure) | Literature review candidate | Abstract only | Would add: the definition of "access" that Q1 leans on. Full text needs supplying by hand. | `doi-10-1057-eps-2016-17` |

## Batch 2: downloaded and read on 2026-11-24 (25)

Of the 25, 18 were read into a record and 7 were not (not obtained, or only an empty or landing page). Of those read, four are an abstract or preview only and one is a landing page. Most of the academic works were filed by the reader under context: they inform the background, not the measurement of business or fossil fuel presence.

| Work | Role | Outcome of the download | Adds or reinforces | Library id |
|---|---|---|---|---|
| Procedural justice and (in)equitable participation in climate negotiations | Literature review candidate | Read in full | Adds: fairness of participation. The reader filed it under context, not Q1: it does not measure business presence. | `doi-10-14324-111-444-ucloe-3116` |
| Networks of climate obstruction (unsure) | Literature review candidate | Read in full | Context for Q2: obstruction actors as a network. The reader filed it under context only. | `doi-10-1371-journal-pclm-0000370` |
| Exchanging access goods for access: A comparative study of business lobbying in the European Union institutions (unsure) | Literature review candidate | Abstract only (181 words) | Two definitions recorded, no findings. Full text needs supplying by hand. | `doi-10-1111-j-1475-6765-2004-00157-x` |
| Following the money: trade associations, political activity and climate change | Literature review candidate | Abstract and reference list only | Two findings from the abstract. Full text needs supplying by hand. | `doi-10-s10584-022-03466-0` |
| How foes become allies: the shifting role of business in climate politics (unsure) | Literature review candidate | Read in full | Context: six findings and five definitions recorded. | `doi-10-s11077-023-09517-2` |
| Discourses of climate delay (unsure) | Literature review candidate | Read in full | Context: the vocabulary of delay, five definitions recorded. | `doi-10-1017-sus-2020-13` |
| Pipelines of Power (TI-EU report) (unsure) | TI's own publication | Read in full (13 pages) | Adds: TI's own terms on fossil fuel lobbying in the EU (Q2 and context). The file name says embargoed: check with the TI colleague before citing. | `transparency-embargoed-ti-eu-pipelines-of-power-report` |
| Conflict of Interests - Corruptionary A-Z | TI's own publication | Read in full (a glossary entry of 66 words) | Adds: TI's own definition of conflict of interest. | `transparency-conflict-of-interests` |
| Record number of fossil fuel lobbyists granted access to COP28 climate talks | Earlier count or report (advocacy or news) | Read in full | Adds: the COP28 count with its methodology and definitions (seven definitions recorded). | `globalwitness-record-number-fossil-fuel-lobbyists-granted-access-cop28` |
| 636 fossil fuel lobbyists granted access to COP27 (Global Witness) | Earlier count or report (advocacy or news) | Read in full; two charts are not in the text | Adds: the COP27 count. | `globalwitness-636-fossil-fuel-lobbyists-granted-access-cop27` |
| Thousands of fossil fuel observers attended climate negotiations: UNFCCC data 2005-2018 COP1-COP24 | Earlier count or report (advocacy or news) | Read; a long list of organisations at the end was skimmed, not recounted | Adds: fossil fuel observers over many years. Its totals have not been recounted by us. | `climateinvestigations-thousands-of-fossil-fuel-observers-attended-clim` |
| Big Meat and Dairy delegates triple at COP28 (DeSmog) | Earlier count or report (advocacy or news) | Read in full | Adds a comparison: the same counting method applied to meat and dairy. | `desmog-big-meat-dairy-delegates-triple-cop28` |
| Corporate Capture and the UN International Civil Aviation Organization (InfluenceMap, 2022) (unsure) | Earlier count or report (advocacy or news) | Not obtained (page not found, 404) | Needs supplying by hand. | `influencemap-corporate-captureof-the-un-international-civil-aviation-o` |
| Kick Big Polluters Out: demands | Earlier count or report (advocacy or news) | Read in full (363 words) | Reinforces: campaign demands. One finding. | `kickbigpollutersout-demands` |
| CAN position on conflicts of interest | Earlier count or report (advocacy or news) | Read in full (4 pages) | Adds: a civil society position with six definitions on conflicts of interest. | `climatenetwork-can-position-on-conflicts-of-interest-2` |
| Analysis code for 'Tracing inclusivity at UNFCCC conferences through side events and interest group dynamics' | Data or reference list | Landing page only (61 words); not read | A code and data deposit. Open it only if we reuse the code. | `doi-10-5281-zenodo-14010847` |
| unfccc-cop-analysis repository | Data or reference list | Landing page only (229 words); read | No findings: the page is a file listing. The code itself has not been examined. | `github-unfccc-cop-analysis` |
| European business statistics methodological manual for statistical business registers — 2021 edition - Products Manuals and Guidelines - Eur | Official rule or document | The page held 12 words; not read | The manual itself was not obtained. Needs supplying by hand. | `europa-ks-gq-20-006` |
| Code of Conduct for UNFCCC Conferences, Meetings and Events | Official rule or document | Not obtained (the UNFCCC site returned an empty page) | Needs supplying by hand. | `unfccc-code-of-conduct-for-unfccc-conferences-meetings-and-events` |
| UNFCCC: What are Parties and non-Party stakeholders | Official rule or document | Not obtained (the UNFCCC site returned an empty page) | Needs supplying by hand. | `unfccc-what-are-parties-non-party-stakeholders` |
| Process to strengthen observer engagement in the UNFCCC (PTSOE) | Official rule or document | Not obtained (the UNFCCC site returned an empty page) | Needs supplying by hand. | `unfccc-process-to-strengthen-observer-engagement-in-the-unfccc-ptsoe` |
| Using imperfect surrogates for downstream inference: Design-based supervised learning for social science applications of LLMs | Method reference | Read (the paper itself, filed as `nips-d862f7f5445255090de13b825b880d59-paper-conference`) | Adds: valid estimates from imperfect model labels with a small hand-checked sample. | `nips-d862f7f5445255090de13b825b880d59-abstract-conference` |
| Measurement Validity: A Shared Standard for Qualitative and Quantitative Research (unsure) | Method reference | Abstract only (157 words) | No findings and no quotes could be recorded. Full text needs supplying by hand. | `doi-10-1017-s0003055401003100` |
| The dangers of using proprietary LLMs for research (Ollion et al., Nature Machine Intelligence) (unsure) | Method reference | Preview only (461 words) | One finding from the opening paragraphs. Full text needs supplying by hand. | `nature-s42256-023-00783-6` |
| ChatGPT outperforms crowd workers for text-annotation tasks | Method reference | Not obtained (publisher refused, 403) | Needs supplying by hand. | `doi-10-1073-pnas-2305016120` |

## Batch 3: the four works Ramsey kept on 2026-11-24

Only one of the four could be obtained.

| Work | Role | Outcome of the download | Adds or reinforces | Library id |
|---|---|---|---|---|
| Non-state actors in global climate governance: from Copenhagen to Paris and beyond | Literature review candidate | Not obtained (the search engine refused, 403) | The work has still to be located and supplied by hand. | `google-scholar-lookup-859b9e` |
| Open or closed meetings? Explaining nonstate actor involvement in the international climate change negotiations | Literature review candidate | Read in full | Eight findings on access rules for observers. The reader filed it under context. | `google-scholar-lookup-b4b729` |
| The role of non-nation-state actors and side events in the international climate negotiations | Literature review candidate | Not obtained (the search engine refused, 403) | The work has still to be located and supplied by hand. | `google-scholar-lookup-52c8dc` |
| From Laggards to Leaders: The Evolving Role of the Private Actors in the International Climate Regime | Literature review candidate | Not obtained (publisher refused, 403) | Needs supplying by hand. | `doi-10-1163-9789004372887-004` |

## Rest of batch 3: not planned (Ramsey, 2026-11-24)

Ramsey decided on 2026-11-24 not to go on with the rest of batch 3. These 20 stay in the library list as screened in, so the decision can be revisited; none was downloaded.

| Work | Role | Adds or reinforces (from the title only) | Address | Library id |
|---|---|---|---|---|
| Agrarianizing climate accords & discord: food, agriculture & agrarian movements at UNFCCC Conference of the Parties (unsure) | Literature review candidate | Adds a comparison: agriculture interests in the climate talks. | https://doi.org/10.1080/17565529.2024.2347372 | `doi-10-1080-17565529-2024-2347372` |
| COP26 and the dynamics of anti-fossil fuel norms (unsure) | Literature review candidate | Adds: anti-fossil-fuel norms after COP26; context for Q2. | https://doi.org/10.1002/wcc.816 | `doi-10-1002-wcc-816` |
| The Evolution of the UNFCCC (unsure) | Literature review candidate | Context: a standard history of the UNFCCC. Useful for one paragraph, reinforces. | https://doi.org/10.1146/annurev-environ-102017-030119 | `doi-10-1146-annurev-environ-102017-030119` |
| Climate obstruction in the Global South: Future research trajectories (unsure) | Literature review candidate | Adds: obstruction in the global South, a gap (most of what we hold is about the US and EU). | https://doi.org/10.1371/journal.pclm.0000241 | `doi-10-1371-journal-pclm-0000241` |
| Biased access? Exploring selection to advisory committees (unsure) | Literature review candidate | Adds: measured bias in access to official advisory bodies, a comparison for Q1. | https://doi.org/10.1017/S1755773914000228 | `doi-10-1017-s1755773914000228` |
| A Wide Net? Who sits on the EU's Fisheries Advisory Councils (unsure) | TI's own publication | Adds: TI's own count of who sits in EU expert groups, a methodological cousin of this study. | https://transparency.eu/a-wide-net-new-report-exposes-who-really-sits-on-the-eus-fisheries-advisory-councils/ | `transparency-a-wide-net-new-report-exposes-who-really-sits-on-the-eus` |
| Big Agribusiness delegates double at COP27 | Earlier count or report (advocacy or news) | Adds a comparison: agribusiness delegates counted at COP27. | https://www.desmog.com/2022/11/18/big-agribusiness-delegates-double-cop27/ | `desmog-big-agribusiness-delegates-double-cop27` |
| COP27: 100 more fossil fuel lobbyists than last year | Earlier count or report (advocacy or news) | Reinforces the count series (COP27). | https://corporateeurope.org/en/2022/11/cop27-100-more-fossil-fuel-lobbyists-last-year | `corporateeurope-cop27-100-more-fossil-fuel-lobbyists-last-year` |
| EU floods COP28 climate talks with fossil fuel lobbyists | Earlier count or report (advocacy or news) | Reinforces: EU delegations at COP28. | https://corporateeurope.org/en/2023/12/eu-floods-cop28-climate-talks-fossil-fuel-lobbyists-0 | `corporateeurope-eu-floods-cop28-climate-talks-fossil-fuel-lobbyists-0` |
| List of observers found to have links with tobacco companies at INC (unsure) | Earlier count or report (advocacy or news) | Adds a comparison: observers with tobacco links listed at the tobacco treaty meetings. | https://ggtc.world/knowledge/partnerships-lobbying-and-corruption/list-of-observers-found-to-have-links-with-tobacco-companies-at-inc-4 | `ggtc-list-of-observers-found-to-have-links-with-tobacco-companies-at-i` |
| COP29 party delegation sizes list (Carbon Brief) | Data or reference list | Adds: Carbon Brief's COP29 delegation sizes as a table, to check our totals against. | https://docs.google.com/spreadsheets/d/1323XC-AOuNSMiDhITv-Ks082PTAwcMOAVOctoYNbr1I/edit?usp=sharing | `google-edit-7af9ff` |
| Analysis: Which countries have sent the most delegates to COP28 | Data or reference list | Adds: COP28 delegation sizes by country. | https://www.carbonbrief.org/analysis-which-countries-have-sent-the-most-delegates-to-cop28/ | `carbonbrief-analysis-which-countries-have-sent-the-most-delegates-to-c-2` |
| Analysis: Which countries have sent the most delegates to COP27? | Data or reference list | Adds: COP27 delegation sizes by country. | https://www.carbonbrief.org/analysis-which-countries-have-sent-the-most-delegates-to-cop27/ | `carbonbrief-analysis-which-countries-have-sent-the-most-delegates-to-c-3` |
| LobbyMap Scores (unsure) | Data or reference list | Adds: scores of companies' and trade groups' climate lobbying; a possible reference list. | https://lobbymap.org/LobbyMapScores | `lobbymap-lobbymapscores` |
| The Carbon Underground 200 | Data or reference list | Adds: the 200 largest owners of fossil fuel reserves; a possible reference list. | https://www.ffisolutions.com/research-analytics-index-solutions/research-screening/the-carbon-underground-200/ | `ffisolutions-the-carbon-underground-200` |
| UNFCCC SBI 2025 INF.06 (unsure) | Official rule or document | Adds: an official 2025 information document of the Subsidiary Body for Implementation. | https://unfccc.int/sites/default/files/resource/sbi2025_inf06.pdf | `unfccc-sbi2025-inf06` |
| From Codebooks to Promptbooks: Extracting Information from Text with Generative Large Language Models | Method reference | Reinforces Halterman and Keith on codebooks for language models. | https://doi.org/10.1177/00491241251336794 | `doi-10-1177-00491241251336794` |
| Non-determinism of 'deterministic' LLM settings (unsure) | Method reference | Adds: evidence that the same model gives different answers on repeat runs; supports our second-run check. | http://arxiv.org/abs/2408.04667 | `arxiv-2408-04667` |
| Can unconfident LLM annotations be used for confident conclusions? | Method reference | Adds: using the model's own uncertainty to choose what a person checks. | https://doi.org/10.48550/ARXIV.2408.15204 | `doi-10-48550-arxiv-2408-15204` |
| In Validations We Trust? The Impact of Imperfect Human Annotations as a Gold Standard on the Quality of Validation of Automated Content Anal | Method reference | Adds: what a validation must report to be believed. | https://doi.org/10.1080/10584609.2020.1723752 | `doi-10-1080-10584609-2020-1723752` |

Already held and read before this decision, so kept: `lobbymap-lobbymap-methodology-24422` (its page was already on disk and was read into a record on 2026-11-24 by the source reader, sonnet; that record was in the sample of the independent check).

## Batch 4: open copies found through OpenAlex, 2026-11-24 (21 kept)

**What was done.** Many screened-in papers had failed to download because the publisher refuses automated access, while a legal open copy (a repository, an author's manuscript, a preprint) often exists. The new `rag openaccess` command asked OpenAlex for such copies. It sent only DOIs and, where there was no DOI, an exact title; nothing about the study went out. This gave 90 sources with an open copy that we did not yet hold. Before each download the tool checked the library for the same address and, after the download, for the same bytes, so nothing is stored twice.

**What came back.**

| Outcome | Sources |
|---|---|
| Downloaded with readable text | 53 |
| Downloaded, but the file was a web page (a "Preparing to download", "Redirecting" or reCAPTCHA page) or held no text | 13 |
| Refused by the site (HTTP 403: 19; 503: 1; 202: 1) | 21 |
| The address in OpenAlex was not valid | 1 |
| A copy of a work already held, not stored twice | 2 |
| **Total** | **90** |

One of the 53 was the wrong document: `doi-10-00323292231195184` is a memo on US state climate plans, not the paper the title promised.

**How the 21 were chosen.** A relevance check (sonnet agents, reading the stored text) put each of the 66 held files against the study's questions: 21 keep, 24 doubtful, 8 drop, and 13 unknown (no text to judge). Ramsey decided on 2026-11-24 to keep the 21 and not pursue the other 45. The 21 were then read in full into records by reader agents (sonnet, general-purpose, following the source-reader instructions), the index was rebuilt (184 sources, 17,399 passages) and `literature/by-topic/` was exported again.

**What the 21 add.** Most are background or method; only one also bears on Q1, and none on Q2 directly. Seven are about non-state actors, obstruction and the fossil fuel industry in climate politics (context). Fourteen are about classifying text with language models and checking them against human coders (method). That fills the gap the earlier batches left on validation, but it does not add counts of business or fossil fuel delegates.

| Work | Role (reader's tags) | Adds or reinforces | Library id |
|---|---|---|---|
| Kuyper, Linnér and Schroeder: Non-state actors in hybrid global climate governance | context | Adds: an overview of what non-state actors do at the UNFCCC after Paris, and the justice, legitimacy and effectiveness questions this raises. Author's manuscript. | `doi-10-1002-wcc-497` |
| Bergmann (2020): Non-state actors in the international climate change regulatory framework | context | Adds: the rules for observer access and participation, from a law review. Ledger tag was Q1; the reader found it background only. | `doi-10-33344-vol14iss1pp88-104` |
| Van Asselt and Green (2023): COP26 and the dynamics of anti-fossil fuel norms | context | Adds: how fossil fuels entered the COP texts at COP26. Ledger tag was Q2; the reader found it background only. Was in "Rest of batch 3". | `doi-10-1002-wcc-816` |
| Desai et al. (2026): Renewable energy discourses of fossil fuel companies: obstruction and delay | context, method | Adds: how fossil fuel companies talk about renewables, coded from company texts. Ledger tag was Q2. | `doi-10-1186-s13705-026-00565-z` |
| Edwards et al. (2023): Climate obstruction in the Global South | context | Adds: obstruction outside the US and EU, a gap in what we held. Was in "Rest of batch 3". | `doi-10-1371-journal-pclm-0000241` |
| Franta (2022): Weaponizing economics: Big Oil, economic consultants, and climate policy delay | context | Adds: consultancies working for the oil industry, which matters for how Q1 treats consultancies. Ledger tag was Q2. | `doi-10-1080-09644016-2021-1947636` |
| Jouty and Bonneuil (2025): European oil companies against the European carbon tax | context | Adds: European oil majors lobbying the EU, the closest case to EU delegations. HAL manuscript. | `doi-10-1080-07075332-2025-2583948` |
| Green (2023): The Climate Establishment and the Structural Constraints of the Paris Partnerships | context, Q1 | Adds: corporate partnerships inside the Paris process. The only one of the 21 that also bears on Q1. Research Square preprint. | `springer-s10584-024-03730-5` |
| Törnberg (2023): How to use large language models for text analysis | method | Adds: a step-by-step workflow with validation. arXiv preprint, not the published book version. | `doi-10-4135-9781529683707` |
| Bunt et al. (2025): Validating the use of LLMs for psychological text classification | method | Adds: a validation protocol against human coders. | `doi-10-3389-frsps-2025-1460277` |
| Chae and Davidson (2025): LLMs for text classification, from zero-shot learning to instruction-tuning | method | Adds: zero-shot versus fine-tuned classification in social science. Preprint. | `doi-10-31235-osf-io-sthwk` |
| Nakamura, Tan and Yean (2026): Observational equivalence of LLM and human annotation | method | Adds: when model labels can stand in for human labels in a downstream estimate. Preprint. | `doi-10-2139-ssrn-7389359` |
| González-Bustamante (2024): Benchmarking LLMs in political content text-annotation | method | Reinforces: model labels checked against a human gold standard. Preprint. | `doi-10-48550-arxiv-2409-09741` |
| Timoneda and Vallejo Vera (2025): Rolling memory, annotation with generative LLMs | method | Adds: reshuffling and repeat runs to check stability; supports our second-run check. | `doi-10-1007-s41111-025-00327-w` |
| Grimmer and Stewart (2013): Text as data | method | Reinforces: the standard warning that automated methods must be validated. | `doi-10-1093-pan-mps028` |
| Bonikowski, Luo and Stuhler: Politics as usual? Measuring populism, nationalism and authoritarianism | method | Adds: a transformer classifier with active learning, and its validation. Author's manuscript. | `sagepub-00491241221122317` |
| Do, Ollion and Shen: The augmented social scientist | method | Adds: model annotation at human-level accuracy, measured against human coders. Author's manuscript. | `sagepub-00491241221134526` |
| Atreja et al. (2025): What's in a prompt? | method | Adds: how much prompt design changes model labels; supports fixing and recording the prompt. | `doi-10-1609-icwsm-v19i1-35807` |
| Burnham (2025): Stance detection, a practical guide | method | Adds: practical guidance on applying and validating LLM classification. | `doi-10-1017-psrm-2024-35` |
| Heseltine and Clemm von Hohenberg (2024): LLMs as a substitute for human experts in annotating political text | method | Reinforces: GPT-4 against expert coders. UvA repository copy. | `doi-10-1177-20531680241236239` |
| Thalken et al. (2023): Modeling legal reasoning, LM annotation at the edge of human agreement | method | Adds: where models fail on a concept that humans also find hard to agree on. | `doi-10-18653-v1-2023-emnlp-main-575` |

The ledger's question tag (set at screening) was left as it was. Where the reader's tags differ, this table says so.

**How far to trust these records.**

- The records were written by reader agents (sonnet). The quote check below confirms that each quote is in the stored text on the cited page. It does not confirm that the claim beside the quote reads the source correctly; no independent second reading was done for this batch.
- The PDFs were read as extracted text, because the page renderer (`pdftoppm`) is not installed. Page numbers are PDF page indices, not printed page numbers, and figures were not seen. Five findings were read from tables and carry no quote.
- Several copies are not the published version: Törnberg is the arXiv preprint, Green is a Research Square preprint, and Kuyper et al., Jouty and Bonneuil (HAL), Bonikowski et al. and Do et al. are authors' manuscripts. Quote from them as such, or check the published version before quoting in a report.
- At first, 35 of 525 quotes and 4 of 97 recommendation quotes were not found exactly in the stored text. The causes were soft-hyphen line breaks, quotes running across a page break or a figure, and one misquote. Each was replaced with the exact stored wording and the page where it was found, and was kept only if the checker then confirmed it. All quotes in the library now check: 2,239 quotes in 123 records. The standard checker does not look at recommendations; those were checked separately.

### Not pursued from batch 4 (45; Ramsey, 2026-11-24)

These are status "out" in the library list, with the reason recorded, so the decision can be revisited.

**Read for relevance and judged doubtful or off-topic (32).**

| Group | Library ids |
|---|---|
| Non-state actors and UNFCCC governance, general or marginal | `doi-10-1017-s2045381725000012`, `doi-10-14782-marmarasbd-763831`, `doi-10-1007-s10784-018-9384-2`, `doi-10-1007-s10784-020-09493-5`, `doi-10-1007-s10784-018-9398-9`, `doi-10-1007-s10767-023-09448-z` (Women and Gender Constituency), `doi-10-1007-s10784-020-09513-4` (practice note), `doi-10-1007-s10584-017-2134-6` (anti-fossil fuel norms) |
| A national case, not the UNFCCC | `doi-10-1093-oso-9780197762042-003-0007` (obstruction in the Netherlands) |
| EU lobbying in general | `doi-10-1080-13501763-2015-1008792`, `doi-10-25234-eclic-38141`, `doi-10-1515-bap-2015-0039`, `doi-10-1177-1465116520944572`, `doi-10-1080-07036337-2025-2532423` |
| US politics | `doi-10-1017-s1537592719000951` |
| Language-model and annotation papers too general or off-topic | `doi-10-48550-arxiv-2308-10092`, `doi-10-48550-arxiv-2305-14310`, `doi-10-48550-arxiv-2412-06864`, `doi-10-48550-arxiv-2607-28119`, `doi-10-48550-arxiv-2312-07182`, `doi-10-18653-v1-2025-findings-acl-1323` (anchoring when a person checks model labels: a caveat only), `doi-10-18653-v1-2024-acl-long-104`, `doi-10-1145-3731120-3744574`, `doi-10-1038-s41598-025-96508-3`, `doi-10-18653-v1-2022-emnlp-main-731`, `doi-10-1613-jair-1-12752`, `doi-10-1177-00491241221134527` (tutorial), `doi-10-1017-pan-2024-31` (synthetic data), `doi-10-18653-v1-2025-gebnlp-1-9`, `doi-10-1145-3543873-3587368`, `doi-10-1038-s43588-023-00585-1` |
| The wrong document | `doi-10-00323292231195184` (a US state memo, not the paper in the title) |

**No usable copy (13).** The open link gave a web page or an empty file, so relevance could not be judged: `doi-10-1016-j-crm-2020-100260`, `doi-10-2458-v24i1-20980`, `doi-10-1002-wcc-791`, `doi-10-1088-2753-3751-ae854c`, `doi-10-7765-9781526137296`, `doi-10-31219-osf-io-jvgc5-v3`, `doi-10-1073-pnas-2308950121`, `doi-10-1073-pnas-2305016120`, `doi-10-1017-s0003055416000058`, `doi-10-1016-j-esr-2021-100723`, `doi-10-1111-1475-6765-12194`, `pnas-pnas-2314021121`, `doi-10-1109-access-2024-3402809`.

Two of these look worth reviving if a copy can be supplied by hand: `doi-10-1109-access-2024-3402809` (human against model labels) and `doi-10-1017-s0003055416000058` (crowd-sourced text analysis, APSR).

**Not obtained (22).** These 22 were refused by the site or had no valid address, so they were never in the relevance check. They keep their earlier status in the library list. Three are from "Rest of batch 3": `doi-10-1080-17565529-2024-2347372`, `doi-10-1146-annurev-environ-102017-030119` and `doi-10-1080-10584609-2020-1723752`.

**Copies of works already held (2).** `doi-10-1177-00491241251336794` (From codebooks to promptbooks, also in "Rest of batch 3") came back as the same file as `doi-10-31219-osf-io-jvgc5-v3`, which is empty; `doi-10-52202-075280-3000` is another version of a NeurIPS paper already held.

## Reserve: not planned for download (confirmed by Ramsey, 2026-11-24)

Kept in the library list so the decision can be revisited. Each group says what it would add to what we hold.

### UNFCCC participant lists and figures (9)

Role: data or reference list. Data, not literature. Wanted only if the study compares COP31 with earlier years; then fetch the years needed.

| Tier | Work | Address | Library id |
|---|---|---|---|
| 2 | COP28 Final List of Participants (on-site) | https://unfccc.int/sites/default/files/resource/COP28%20FLOP%20On-site.xlsx | `unfccc-cop28-20flop-20on-site-xlsx` |
| 2 | COP29 Final List of Participants (on-site) | https://unfccc.int/sites/default/files/resource/COP29_FLOP_On-site.xlsx | `unfccc-cop29-flop-on-site-xlsx` |
| 2 | COP29 final participant lists | https://unfccc.int/documents/644764 | `unfccc-644764` |
| 2 | COP29 participant lists | https://unfccc.int/documents/644762 | `unfccc-644762` |
| 2 | COP29 provisional list of participants (unsure) | https://unfccc.int/documents/643061 | `unfccc-643061` |
| 2 | Gender Composition. Report by the Secretariat (UNFCCC, 2023) (unsure) | https://unfccc.int/documents/631338 | `unfccc-631338` |
| 2 | UNFCCC document 643064 (participant figures) (unsure) | https://unfccc.int/documents/643064 | `unfccc-643064` |
| 2 | UNFCCC list of participants spreadsheets (Baku) | https://unfccc.int/documents/643063 | `unfccc-643063` |
| 2 | UNFCCC participant list (documents/634503) | https://unfccc.int/documents/634503 | `unfccc-634503` |

### UNFCCC reference pages (8)

Role: official rule or document. Official pages on observers and constituencies. Cited as sources of rules where needed; not literature.

| Tier | Work | Address | Library id |
|---|---|---|---|
| 1 | UNFCCC parties_and_observers application document 855rev (unsure) | https://unfccc.int/files/parties_and_observers/application/pdf/855rev.pdf | `unfccc-855rev` |
| 2 | ratified the convention (unsure) | https://treaties.un.org/Pages/ViewDetailsIII.aspx?src=IND&mtdsg_no=XXVII-7&chapter=27&Temp=mtdsg3&clang=_en | `un-viewdetailsiii-3b4981` |
| 2 | UNFCCC Admitted NGOs | https://unfccc.int/process-and-meetings/parties-non-party-stakeholders/non-party-stakeholders/overview/admitted-ngos | `unfccc-admitted-ngos` |
| 2 | UNFCCC list of admitted IGOs/NGOs | https://unfccc.int/process/parties-non-party-stakeholders/non-party-stakeholders/admitted-igos/list-of-admitted-igos | `unfccc-list-of-admitted-igos` |
| 2 | UNFCCC observer organizations constituencies | http://unfccc.int/parties_and_observers/observer_organizations/items/9519.php | `unfccc-9519` |
| 2 | UNFCCC SEORS side events archive (unsure) | https://seors.unfccc.int/applications/seors/reports/archive.html | `unfccc-archive` |
| 5 | Constituencies and You (UNFCCC) | http://https://unfccc.int/files/parties_and_observers/ngo/application/pdf/constituencies_and_you.pdf | `https-constituencies-and-you` |
| 5 | UNFCCC constituency focal point contact details | http://https://unfccc.int/files/parties_and_observers/ngo/application/pdf/constituency_focal_point_contact_details.pdf | `https-constituency-focal-point-contact-details` |

### Non-state actors, constituencies and reform of the UNFCCC (34)

Role: literature review candidate. Reinforces Kuyper, Nasiritousi and Xie, which we hold. Read only if a specific gap appears.

| Tier | Work | Address | Library id |
|---|---|---|---|
| 2 | Exploring national and regional orchestration of non-state action for a < 1.5 °C world (unsure) | https://doi.org/10.1007/s10784-018-9384-2 | `doi-10-1007-s10784-018-9384-2` |
| 2 | Global Climate Governance between State and Non-State Actors: Dynamics of Contestation and Re-Legitimation (unsure) | https://doi.org/10.14782/marmarasbd.763831 | `doi-10-14782-marmarasbd-763831` |
| 2 | Lessons from the Women and Gender Constituency: Interrogating Civil Society Strategies for Organising in the UNFCCC (unsure) | https://doi.org/10.1007/s10767-023-09448-z | `doi-10-1007-s10767-023-09448-z` |
| 2 | Mainstreaming Gender in Global Climate Governance: Women and Gender Constituency in the UNFCCC (unsure) | https://doi.org/10.4324/9781003306474 | `doi-10-4324-9781003306474` |
| 2 | Making climate governance global: how UN climate summitry comes to matter in a complex climate regime (unsure) | https://doi.org/10.1080/09644016.2017.1319019 | `doi-10-1080-09644016-2017-1319019` |
| 2 | Making initiatives resonate: how can non-state initiatives advance national contributions under the UNFCCC? (unsure) | https://doi.org/10.1007/s10784-018-9398-9 | `doi-10-1007-s10784-018-9398-9` |
| 2 | New alliances in global environmental governance: how intergovernmental treaty secretariats interact with non-state actors (unsure) | https://doi.org/10.1007/s10784-020-09493-5 | `doi-10-1007-s10784-020-09493-5` |
| 2 | Non- and sub-state climate action after Paris: From a facilitative regime to a contested governance landscape (unsure) | https://doi.org/10.1002/wcc.791 | `doi-10-1002-wcc-791` |
| 2 | Non-state actors in hybrid global climate governance: justice, legitimacy, and effectiveness in a post-Paris era (unsure) | https://doi.org/10.1002/wcc.497 | `doi-10-1002-wcc-497` |
| 2 | Non-state Actors in the International Climate Change Regulatory Framework | https://doi.org/10.33344/vol14iss1pp88-104 | `doi-10-33344-vol14iss1pp88-104` |
| 2 | Partners for the climate? How and why EU Delegations engage with CSOs (unsure) | https://doi.org/10.1080/07036337.2025.2532423 | `doi-10-1080-07036337-2025-2532423` |
| 2 | Recognising differentiated affectedness within a global demos: promoting the democratic legitimacy of the UNFCCC (unsure) | https://doi.org/10.1017/s2045381725000012 | `doi-10-1017-s2045381725000012` |
| 2 | Shapers, Brokers and Doers: The Dynamic Roles of Non-State Actors in Global Climate Change Governance (unsure) | https://doi.org/10.3384/diss.diva-123295 | `doi-10-3384-diss-diva-123295` |
| 2 | The democratic legitimacy of orchestration: the UNFCCC, non-state actors, and transnational climate governance | https://doi.org/10.1080/09644016.2017.1323579 | `doi-10-1080-09644016-2017-1323579` |
| 2 | The United Nations Framework Convention on Climate Change Secretariat as an orchestrator in global climate policymaking (unsure) | https://doi.org/10.1177/0020852319840425 | `doi-10-1177-0020852319840425` |
| 2 | UN environmental policy: Non-State Actors, trends, and the regulatory role of the state (unsure) | https://doi.org/10.2458/v24i1.20980 | `doi-10-2458-v24i1-20980` |
| 2 | Who Tells Your Story? Women and Indigenous Peoples Advocacy at the UNFCCC (unsure) | https://doi.org/10.1017/9781009472920 | `doi-10-1017-9781009472920` |
| 5 | Brokering climate action: the UNFCCC secretariat between parties and nonparty stakeholders | http://scholar.google.com/scholar_lookup?title=Brokering+climate+action%3A+the+UNFCCC+secretariat+between+parties+and+nonparty+stakeholders&journal=Glob.+Environ.+Polit.&volume=20&pages=105-127&publication_year=2020&author=Saerbeck%2CB&author=Well%2CM&author=J%C3%B6rgens%2CH&author=Goritz%2CA&author=Kolleck%2CN | `google-scholar-lookup-f436ea` |
| 5 | Climate Changing Civil Society? Norwegian non-state actors channels, strategies, and influence in the UNFCCC negotiations | https://hdl.handle.net/10852/45353 | `handle-45353` |
| 5 | Climate governance: reform or perish, the future of the UNFCCC (unsure) | https://theglobalobservatory.org/2022/04/climate-governance-reform-or-perish-the-future-of-the-unfccc/ | `theglobalobservatory-climate-governance-reform-or-perish-the-future-of` |
| 5 | Climate of consensus: managing decision making in the UN climate change negotiations (unsure) | http://scholar.google.com/scholar_lookup?title=Climate+of+consensus%3A+managing+decision+making+in+the+UN+climate+change+negotiations&journal=Rev.+Eur.+Comp.+Int.+Environ.+Law&doi=10.1111%2Freel.12093&volume=24&pages=58-68&publication_year=2015&author=Vihma%2CA | `google-scholar-lookup-d5e63b` |
| 5 | Frames of climate change in side events from Kyoto to Durban (unsure) | http://scholar.google.com/scholar_lookup?title=Frames+of+climate+change+in+side+events+from+Kyoto+to+Durban&journal=Glob.+Environ.+Polit.&volume=14&pages=102-121&publication_year=2014&author=Hjerpe%2CM&author=Buhr%2CK | `google-scholar-lookup-b678bf` |
| 5 | From collaboration to contestation? Perceptions of legitimacy and effectiveness in post-Paris climate governance (unsure) | http://scholar.google.com/scholar_lookup?title=From+collaboration+to+contestation%3F+Perceptions+of+legitimacy+and+effectiveness+in+post-Paris+climate+governance&journal=Earth+Syst.+Gov.&doi=10.1016%2Fj.esg.2021.100115&volume=9&publication_year=2021&author=B%C3%A4ckstrand%2CK&author=Kuyper%2CJ&author=Nasiritousi%2CN | `google-scholar-lookup-bf8f9a` |
| 5 | Functions of COP side-events in climate-change governance | http://scholar.google.com/scholar_lookup?title=Functions+of+COP+side-events+in+climate-change+governance&journal=Clim.+Policy&volume=10&pages=167-180&publication_year=2010&author=Hjerpe%2CM&author=Linn%C3%A9r%2CBO | `google-scholar-lookup-7de17e` |
| 5 | Future of the UNFCCC (Mistra Geopolitics) (unsure) | https://www.mistra-geopolitics.se/publications/future-of-the-unfccc | `mistra-geopolitics-future-of-the-unfccc` |
| 5 | Improving future climate meetings (unsure) | http://scholar.google.com/scholar_lookup?title=Improving+future+climate+meetings&journal=Nat.+Clim.+Change&doi=10.1038%2Fs41558-025-02293-2&volume=15&publication_year=2025&author=Hadden%2CJ&author=Prakash%2CA | `google-scholar-lookup-fe3fc9` |
| 5 | Matching supply and demand? Exploring UNFCCC reform options (unsure) | http://scholar.google.com/scholar_lookup?title=Matching+supply+and+demand%3F+Exploring+UNFCCC+reform+options&journal=Earth+Syst.+Gov.&doi=10.1016%2Fj.esg.2025.100241&volume=23&publication_year=2025&author=Nasiritousi%2CN&author=Buylova%2CA&author=Linn%C3%A9r%2CBO | `google-scholar-lookup-edc8a4` |
| 5 | NGO influence in international organizations: information, access and exchange (unsure) | http://scholar.google.com/scholar_lookup?title=NGO+influence+in+international+organizations%3A+information%2C+access+and+exchange&journal=Br.+J.+Polit.+Sci.&doi=10.1017%2FS000712341500037X&volume=48&pages=213-238&publication_year=2018&author=Tallberg%2CJ&author=Dellmuth%2CLM&author=Agn%C3%A9%2CH&author=Duit%2CA | `google-scholar-lookup-c4a84a` |
| 5 | Promoting Environmental Democracy in Multilateral Forums Through International Law: Civil Society Participation and Representation in the UN | http://urn.fi/URN:ISBN:978-952-61-6104-4 | `urn-urn-isbn-978-952-61-6104-4` |
| 5 | The calm before the storm: an assessment of the 23rd Climate Change Conference (COP 23) in Bonn (unsure) | https://hdl.handle.net/1871.1/863ab23f-d561-44a2-9e70-ca51cf919ad1 | `handle-863ab23f-d561-44a2-9e70-ca51cf919ad1` |
| 5 | The Climate Establishment and the Paris partnerships (unsure) | https://link.springer.com/doi/10.1007/s10584-024-03730-5 | `springer-s10584-024-03730-5` |
| 5 | The management of multilateral negotiations: lessons from UN climate negotiations (unsure) | http://eprints.lse.ac.uk/64534/1/Managment-of-multilateral-negotiations_Monheim_final.pdf | `ac-managment-of-multilateral-negotiations-monheim-final` |
| 5 | Transparency in global sustainability governance: to what effect? (unsure) | http://scholar.google.com/scholar_lookup?title=Transparency+in+global+sustainability+governance%3A+to+what+effect%3F&journal=J.+Environ.+Policy+Plan.&doi=10.1080%2F1523908X.2020.1709281&volume=22&pages=84-97&publication_year=2020&author=Gupta%2CA&author=Boas%2CI&author=Oosterveer%2CP | `google-scholar-lookup-df93f3` |
| 5 | What's different about the environment? Environmental INGOs in comparative perspective (unsure) | http://scholar.google.com/scholar_lookup?title=What%E2%80%99s+different+about+the+environment%3F+Environmental+INGOs+in+comparative+perspective&journal=Env.+Polit.&volume=30&pages=202-223&publication_year=2021&author=Hadden%2CJ&author=Bush%2CSS | `google-scholar-lookup-ed6db6` |

### Fossil fuel obstruction in general (38)

Role: literature review candidate. Reinforces Roberts 2025, which we hold. Mostly about national politics, not the delegations.

| Tier | Work | Address | Library id |
|---|---|---|---|
| 2 | 'The End of the Fossil Fuel Age'? Discourse Politics and Climate Change Political Economy (unsure) | https://doi.org/10.1080/13563467.2020.1810218 | `doi-10-1080-13563467-2020-1810218` |
| 2 | Anti-fossil fuel norms (unsure) | https://doi.org/10.1007/s10584-017-2134-6 | `doi-10-1007-s10584-017-2134-6` |
| 2 | Climate change and the oil industry: Common problem, varying strategies | https://doi.org/10.7765/9781526137296 | `doi-10-7765-9781526137296` |
| 2 | Climate Obstruction in Italy: From Outright Denial to Widespread Climate Delay (unsure) | https://doi.org/10.1093/oso/9780197762042.003.0011 | `doi-10-1093-oso-9780197762042-003-0011` |
| 2 | Climate Obstruction in the Netherlands (unsure) | https://doi.org/10.1093/oso/9780197762042.003.0007 | `doi-10-1093-oso-9780197762042-003-0007` |
| 2 | Climate Obstruction in the United Kingdom | https://doi.org/10.1093/oso/9780197762042.003.0002 | `doi-10-1093-oso-9780197762042-003-0002` |
| 2 | Conclusion: Ten Lessons about Climate Obstruction in Europe (unsure) | https://doi.org/10.1093/oso/9780197762042.003.0014 | `doi-10-1093-oso-9780197762042-003-0014` |
| 2 | Contention strikes back? The discursive, instrumental and institutional tactics implemented by coal sector incumbents in Colombia (unsure) | https://doi.org/10.1016/j.erss.2019.101280 | `doi-10-1016-j-erss-2019-101280` |
| 2 | Fossil fascism: the supreme form of climate obstruction? (unsure) | https://doi.org/10.1080/01419870.2026.2665720 | `doi-10-1080-01419870-2026-2665720` |
| 2 | Fossil fuel industry communication strategies and public responses: a scoping review (unsure) | https://doi.org/10.1088/2753-3751/ae854c | `doi-10-1088-2753-3751-ae854c` |
| 2 | Introduction: The First Portrait of Climate Obstruction across Europe (unsure) | https://doi.org/10.1093/oso/9780197762042.003.0001 | `doi-10-1093-oso-9780197762042-003-0001` |
| 2 | Introduction: Understanding Obstruction of Climate Action | https://doi.org/10.1093/oso/9780197787144.003.0001 | `doi-10-1093-oso-9780197787144-003-0001` |
| 2 | Lobbying and Green Transition in Fossil Fuel Sector (unsure) | https://doi.org/10.1002/bse.70475 | `doi-10-1002-bse-70475` |
| 2 | Renewable energy discourses of fossil fuel companies: obstruction and delay of climate action (unsure) | https://doi.org/10.1186/s13705-026-00565-z | `doi-10-1186-s13705-026-00565-z` |
| 2 | Risking the earth Part 2: Power politics and structural reform of the IPCC and UNFCCC (unsure) | https://doi.org/10.1016/j.crm.2020.100260 | `doi-10-1016-j-crm-2020-100260` |
| 2 | The Paris Agreement on Climate Change—Made in USA? (unsure) | https://doi.org/10.1017/s1537592719000951 | `doi-10-1017-s1537592719000951` |
| 2 | Undermining Climate Action: The Fight by European Oil Companies Against the European Carbon Tax (unsure) | https://doi.org/10.1080/07075332.2025.2583948 | `doi-10-1080-07075332-2025-2583948` |
| 2 | Weaponizing economics: Big Oil, economic consultants, and climate policy delay | https://doi.org/10.1080/09644016.2021.1947636 | `doi-10-1080-09644016-2021-1947636` |
| 5 | 1996 Economic Impacts from Proposed Emission Restrictions (GCC) (unsure) | https://www.climatefiles.com/denial-groups/global-climate-coalition-collection/1996-economic-impacts-from-proposed-emission-restrictions/ | `climatefiles-1996-economic-impacts-from-proposed-emission-restrictions` |
| 5 | A fossilized democracy: the fossil free movement's work in liberating democracy from the fossil fuel industry (unsure) | http://lup.lub.lu.se/student-papers/record/8878462 | `lu-8878462` |
| 5 | Assessing ExxonMobil's climate change communications (1977-2014) (unsure) | https://doi:10.1088/1748-9326/aa815f | `doi-10-aa815f` |
| 5 | Big Oil Reality Check 2023 (unsure) | https://priceofoil.org/2023/05/25/big-oil-reality-check-2023/ | `priceofoil-big-oil-reality-check-2023` |
| 5 | CSSN Briefing: Obstruction (unsure) | https://cssn.org/wp-content/uploads/2021/04/CSSN-Briefing_-Obstruction-2.pdf | `cssn-cssn-briefing-obstruction-2` |
| 5 | Fossil-Fueled Foolery: An Illustrated Primer on the Top 10 Manipulation Tactics of the Fossil Fuel Industry (unsure) | https://live-naacp-site.pantheonsite.io/wp-content/uploads/2019/04/Fossil-Fueled-Foolery-An-Illustrated-Primer-on-the-Top-10-Manipulation-Tactics-of-the-Fossil-Fuel-Industry-FINAL-1.pdf | `pantheonsite-fossil-fueled-foolery-an-illustrated-primer-on-the-top-10` |
| 5 | Global Climate Coalition draft primer (ClimateFiles) (unsure) | https://www.climatefiles.com/denial-groups/global-climate-coalition-collection/global-climate-coalition-draft-primer/ | `climatefiles-global-climate-coalition-draft-primer` |
| 5 | Global Climate Coalition meeting 2001 (unsure) | https://www.documentcloud.org/documents/4407192-Global-Climate-Coalition-Meeting-2001 | `documentcloud-4407192-global-climate-coalition-meeting-2001` |
| 5 | Hearing report: The role of public relations firms in preventing action on climate change (unsure) | https://democrats-naturalresources.house.gov/hearing-report-the-role-of-public-relations-firms-in-preventing-action-on-climate-change | `house-hearing-report-the-role-of-public-relations-firms-in-preventing` |
| 5 | House hearing CHRG-116hhrg38304 (unsure) | https://www.govinfo.gov/content/pkg/CHRG-116hhrg38304/html/CHRG-116hhrg38304.htm | `govinfo-chrg-116hhrg38304` |
| 5 | Is climate obstruction different in the Global South? Observations and a preliminary research agenda (unsure) | https://cssn.org/is-climate-obstruction-different-in-the-global-south-observations-and-a-preliminary-research-agenda/ | `cssn-is-climate-obstruction-different-in-the-global-south-observations` |
| 5 | Oppose, support, or hedge? Distributional effects, regulatory pressure, and business strategy in environmental politics | http://scholar.google.com/scholar_lookup?title=Oppose%2C+support%2C+or+hedge%3F+Distributional+effects%2C+regulatory+pressure%2C+and+business+strategy+in+environmental+politics&journal=Glob.+Environ.+Polit.&volume=2&pages=19-37&publication_year=2015&author=Meckling%2CJ | `google-scholar-lookup-f34dc1` |
| 5 | Polluter Watch (unsure) | http://polluterwatch.org/ | `polluterwatch-home` |
| 5 | Report from COP27: The Fossil Fuel Industry Continues to Block the Path to Climate Justice (unsure) | https://blog.ucsusa.org/delta-merner/report-from-cop27-the-fossil-fuel-industry-continues-to-block-the-path-to-climate-justice/ | `ucsusa-report-from-cop27-the-fossil-fuel-industry-continues-to-block-t` |
| 5 | Rhetoric and frame analysis of ExxonMobil's climate change communications (unsure) | http://scholar.google.com/scholar_lookup?title=Rhetoric+and+frame+analysis+of+ExxonMobil%E2%80%99s+climate+change+communications&journal=One+Earth&volume=4&pages=696-719&publication_year=2021&author=Supran%2CG&author=Oreskes%2CN | `google-scholar-lookup-624d4f` |
| 5 | Speaking Sustainability, Sustaining Extraction: Narratives of Corporate Climate Obstruction within the UNFCCC | https://scarab.bates.edu/envr_studies_theses/411 | `bates-411` |
| 5 | Using earnings calls to understand the political behavior of major polluters (unsure) | http://scholar.google.com/scholar_lookup?title=Using+earnings+calls+to+understand+the+political+behavior+of+major+polluters&journal=Glob.+Environ.+Polit.&volume=22&pages=159-174&publication_year=2022&author=Mahdavi%2CP&author=Green%2CJ&author=Hadden%2CJ&author=Hale%2CT | `google-scholar-lookup-630b4a` |
| 5 | Where You Stand Depends on What You Sell - Saudi Arabia's Obstructionism in the UNFCCC 2012-2018 (unsure) | https://hdl.handle.net/10852/69719 | `handle-69719` |
| 5 | Who delays climate action? Interest groups and coalitions in state legislative struggles in the United States (unsure) | https://doi:10.1016/j.erss.2021.102114 | `doi-10-j-erss-2021-102114` |
| 5 | Who Pays for Environmental Policy? Business Power and the Design of State-Level Climate Policies (unsure) | https://doi:10.1177/00323292231195184 | `doi-10-00323292231195184` |

### Advocacy reports, statements and news (23)

Role: earlier count or report (advocacy or news). Reinforces the counts and positions already read. Useful for a quotation, not for the review.

| Tier | Work | Address | Library id |
|---|---|---|---|
| 1 | Club of Rome: COP reform (unsure) | https://www.clubofrome.org/cop-reform/ | `clubofrome-cop-reform` |
| 1 | Fossil fuel lobbyists will have to identify themselves when registering for COP28 (Guardian) | https://www.theguardian.com/environment/2023/jun/15/fossil-fuel-lobbyists-will-have-to-identify-themselves-when-registering-for-cop28 | `theguardian-fossil-fuel-lobbyists-will-have-to-identify-themselves-whe` |
| 1 | Joint civil society submission to UNFCCC on undue influence of polluters | https://kickbigpollutersout.org/resources/joint-civil-society-submission-unfccc-undue-influence-polluters | `kickbigpollutersout-joint-civil-society-submission-unfccc-undue-influe` |
| 1 | wider civil society | https://kickbigpollutersout.org/articles/release-pressure-mounts-remove-polluters-not-just-oil-exec-un-climate-talks | `kickbigpollutersout-release-pressure-mounts-remove-polluters-not-just` |
| 2 | Fossil Fuel Narrative Tracker (InfluenceMap) (unsure) | https://cop.influencemap.org/NarrativeTracker | `influencemap-narrativetracker` |
| 2 | InfluenceMap COP: Updates & Resources (unsure) | https://cop.influencemap.org/multipage/Updates-Resources-16262 | `influencemap-updates-resources-16262` |
| 2 | InfluenceMap Japan Report, October 2017 (unsure) | https://influencemap.org/site/data/000/302/Japan_Report_October_2017.pdf | `influencemap-japan-report-october-2017` |
| 2 | Japanese Industry Groups and Climate Policy (unsure) | https://influencemap.org/presentation/Japanese-Industry-Groups-and-Climate-Policy-899704d005cb96359cc5b5e2a9b18a84 | `influencemap-japanese-industry-groups-and-climate-policy-899704d005cb9` |
| 3 | By invitation only: policy capture and the EU omnibus (unsure) | https://transparency.eu/by-invitation-only-policy-capture-and-the-eu-omnibus-i/ | `transparency-by-invitation-only-policy-capture-and-the-eu-omnibus-i` |
| 3 | COP30 next steps (Kick Big Polluters Out) | https://kickbigpollutersout.org/COP30-next-steps-KBPO | `kickbigpollutersout-cop30-next-steps-kbpo` |
| 3 | Fossil fuel lobbyists attend UN climate talks more than 7,000 times (KBPO) | https://kickbigpollutersout.org/articles/release-fossil-fuel-lobbyists-attend-un-climate-talks-more-7000-times | `kickbigpollutersout-release-fossil-fuel-lobbyists-attend-un-climate-ta` |
| 3 | Global Witness: carbon capture and the oil lobby at COP28 (unsure) | https://www.globalwitness.org/en/blog/carbon-capture-oil-lobby-cop28/ | `globalwitness-carbon-capture-oil-lobby-cop28` |
| 3 | Open letter to von der Leyen (Transparency International EU) (unsure) | https://transparency.eu/wp-content/uploads/2024/10/Open-letter-to-von-der-Leyen_final.pdf | `transparency-open-letter-to-von-der-leyen-final` |
| 3 | Reminder sent to Hoekstra ahead of climate talks (Fossil Free Politics) | https://fossilfreepolitics.org/news/reminder-sent-to-hoekstra-ahead-of-climate-talks/ | `fossilfreepolitics-reminder-sent-to-hoekstra-ahead-of-climate-talks` |
| 3 | Urgent action to safeguard integrity of COP: fossil fuel influence, Baku | https://www.transparency.org/en/press/urgent-action-to-safeguard-integrity-of-cop-fossil-fuel-influence-baku | `transparency-urgent-action-to-safeguard-integrity-of-cop-fossil-fuel-i` |
| 4 | Mapped: Big Ag's routes to influence at COP28 (unsure) | https://www.desmog.com/2023/12/01/mapped-big-ags-routes-to-influence-at-cop28/ | `desmog-mapped-big-ags-routes-to-influence-at-cop28` |
| 5 | 2023 Proxy Season: An Introduction to Climate Lobbying (unsure) | https://www.climateaction100.org/news/2023-proxy-season-an-introduction-to-climate-lobbying | `climateaction100-2023-proxy-season-an-introduction-to-climate-lobbying` |
| 5 | Business lobbies dominate secret channel (Corporate Europe Observatory) (unsure) | https://corporateeurope.org/en/2021/07/business-lobbies-dominate-secret-channel | `corporateeurope-business-lobbies-dominate-secret-channel` |
| 5 | CBC: oilsands executives at COP28 carbon capture (unsure) | https://www.cbc.ca/news/canada/calgary/oilsands-executives-cop-28-carbon-capture-1.7044163 | `cbc-oilsands-executives-cop-28-carbon-capture-1-7044163` |
| 5 | Fossil Free Politics (EU governments' fossil fuel lobbyists at COP30) (unsure) | https://fossilfreepolitics.org/ | `fossilfreepolitics-home` |
| 5 | Funding climate deniers (Corporate Europe Observatory) (unsure) | https://corporateeurope.org/sites/default/files/sites/default/files/files/article/funding_climate_deniers.pdf | `corporateeurope-funding-climate-deniers` |
| 5 | Open letter on COP reform (Club of Rome, 2024) (unsure) | https://www.clubofrome.org/cop-reform-2024/ | `clubofrome-cop-reform-2024` |
| 5 | United Call to Action: The COP We Need (unsure) | https://www.ciel.org/wp-content/uploads/2025/06/United-Call-to-Action-TheCOPWeNeed.pdf | `ciel-united-call-to-action-thecopweneed` |

### Lobbying and interest groups in the EU (19)

Role: literature review candidate. Reinforces Dür, Berkhout, Junk and the OECD, which we hold.

| Tier | Work | Address | Library id |
|---|---|---|---|
| 2 | Change and Continuity in the Composition of the Lobby Community in the European Union (unsure) | https://doi.org/10.4324/9781003075097-3 | `doi-10-4324-9781003075097-3` |
| 2 | Clean, low-carbon but corrupt? Corruption risks in the renewable energy sector (unsure) | https://doi.org/10.1016/j.esr.2021.100723 | `doi-10-1016-j-esr-2021-100723` |
| 2 | Conceptualising the policy engagement of interest groups (unsure) | https://doi.org/10.1111/1475-6765.12194 | `doi-10-1111-1475-6765-12194` |
| 2 | EESC Ad hoc Group on COP (unsure) | https://www.eesc.europa.eu/en/sections-other-bodies/other/ad-hoc-group-cop | `europa-ad-hoc-group-cop` |
| 2 | Framing in context: how interest groups employ framing to lobby the European Commission (unsure) | http://dx.doi.org/10.1080/13501763.2015.1008550 | `doi-10-1080-13501763-2015-1008550` |
| 2 | Influence, affluence and media salience: Economic resources and lobbying influence in the European Union (unsure) | https://doi.org/10.1177/1465116520944572 | `doi-10-1177-1465116520944572` |
| 2 | Institutional Context, Organizational Resources and Strategic Choices: Explaining Interest Group Access in the European Union (unsure) | https://doi.org/10.1177/1465116507079542 | `doi-10-1177-1465116507079542` |
| 2 | Legislative lobbying in context: towards a conceptual framework of interest group lobbying in the European Union (unsure) | https://doi.org/10.1080/13501763.2015.1008792 | `doi-10-1080-13501763-2015-1008792` |
| 2 | Lobbying in the European Union (unsure) | https://doi.org/10.25234/eclic/38141 | `doi-10-25234-eclic-38141` |
| 2 | Lobbying the European Union: Changing Minds, Changing Times (unsure) | https://doi.org/10.4324/9781003075097 | `doi-10-4324-9781003075097` |
| 2 | Lobbyists, Governments and Public Trust, Volume 3: Implementing the OECD Principles for Transparency and Integrity in Lobbying | https://doi.org/10.1787/9789264214224-en | `doi-10-1787-9789264214224-en` |
| 2 | OECD Recommendation on Transparency and Integrity in Lobbying (2014 report) | https://one.oecd.org/document/C(2014)7/en/pdf | `oecd-pdf-2` |
| 2 | OECD Report to Council on the Recommendation on Principles for Transparency and Integrity in Lobbying (C(2021)74) | https://one.oecd.org/document/C(2021)74/en/pdf | `oecd-pdf` |
| 2 | Prevention of Conflicts of Interest (EDPS) (unsure) | https://www.edps.europa.eu/data-protection/data-protection/reference-library/prevention-conflicts-interest_en | `europa-prevention-conflicts-interest-en` |
| 2 | Regulating lobbying activities in the European Union: A voluntary club perspective (unsure) | https://doi.org/10.1111/rego.12200 | `doi-10-1111-rego-12200` |
| 2 | Representatives of the public? Public opinion and interest group activity (unsure) | https://doi.org/10.1111/1475-6765.12036 | `doi-10-1111-1475-6765-12036` |
| 2 | Technocratic or democratic interest representation? How different types of information affect lobbying success (unsure) | https://doi.org/10.1057/s41309-019-00051-2 | `doi-10-1057-s41309-019-00051-2` |
| 2 | Whom do European corporations lobby? The domestic institutional determinants of interest group activity in the European Union (unsure) | https://doi.org/10.1515/bap-2015-0039 | `doi-10-1515-bap-2015-0039` |
| 5 | Integrity Watch EU: Commission lobby meetings (unsure) | https://www.integritywatch.eu/ecmeetings.php | `integritywatch-ecmeetings` |

### InfluenceMap sector reports (5)

Role: earlier count or report (advocacy or news). Other sectors (cars, aviation, carbon capture). Not needed unless the study widens beyond fossil fuel.

| Tier | Work | Address | Library id |
|---|---|---|---|
| 2 | Airlines and European Climate Policy (unsure) | https://influencemap.org/report/Airlines-and-European-Climate-Policy-19388 | `influencemap-airlines-and-european-climate-policy-19388` |
| 2 | Automakers and Climate Policy Advocacy: A Global Analysis (unsure) | https://influencemap.org/report/Automakers-and-Climate-Policy-Advocacy-A-Global-Analysis-27906 | `influencemap-automakers-and-climate-policy-advocacy-a-global-analysis` |
| 2 | Corporate Advocacy on Carbon Capture and Storage (CCS) (InfluenceMap) (unsure) | https://influencemap.org/report/CCS-and-Corporate-Policy-Engagement-24754 | `influencemap-ccs-and-corporate-policy-engagement-24754` |
| 2 | InfluenceMap: European Automotive Suppliers and EU Climate Policy (unsure) | https://influencemap.org/report/European-Automotive-Suppliers-EU-Climate-Policy-17388 | `influencemap-european-automotive-suppliers-eu-climate-policy-17388` |
| 2 | US Heavy-Duty Transport & Climate Change (InfluenceMap) (unsure) | https://influencemap.org/report/US-Heavy-Duty-Transport-Climate-Change-20434 | `influencemap-us-heavy-duty-transport-climate-change-20434` |

### Using language models to label text (50)

Role: method reference. Reinforces the 16 method sources we hold. The methodology needs a handful of these, not sixty.

| Tier | Work | Address | Library id |
|---|---|---|---|
| 2 | Adapting computational text analysis to social science (and vice versa) (unsure) | https://doi.org/10.1177/2053951715602908 | `doi-10-1177-2053951715602908` |
| 2 | AFaCTA: Assisting the Annotation of Factual Claim Detection with Reliable LLM Annotators | https://doi.org/10.18653/v1/2024.acl-long.104 | `doi-10-18653-v1-2024-acl-long-104` |
| 2 | Assessing the Reliability of LLMs Annotations in the Context of Demographic Bias and Model Explanation | https://doi.org/10.18653/v1/2025.gebnlp-1.9 | `doi-10-18653-v1-2025-gebnlp-1-9` |
| 2 | Automated Text Classification of News Articles: A Practical Guide | https://doi.org/10.1017/pan.2020.8 | `doi-10-1017-pan-2020-8` |
| 2 | Benchmarking LLMs in Political Content Text-Annotation | https://doi.org/10.48550/arxiv.2409.09741 | `doi-10-48550-arxiv-2409-09741` |
| 2 | Challenges in annotations by humans and LLMs: A case study of evaluative language | https://doi.org/10.48550/arxiv.2607.28119 | `doi-10-48550-arxiv-2607-28119` |
| 2 | ChatGPT Label: Comparing the Quality of Human-Generated and LLM-Generated Annotations in Low-Resource Language NLP Tasks | https://doi.org/10.1109/access.2024.3402809 | `doi-10-1109-access-2024-3402809` |
| 2 | Cheap and fast - but is it good? Evaluating non-expert annotations for natural language tasks (unsure) | https://doi.org/10.3115/1613715.1613751 | `doi-10-3115-1613715-1613751` |
| 2 | Classifying complex documents: comparing bespoke solutions to large language models | https://doi.org/10.48550/arxiv.2312.07182 | `doi-10-48550-arxiv-2312-07182` |
| 2 | Comparing large Language models and human annotators in latent content analysis | https://doi.org/10.1038/s41598-025-96508-3 | `doi-10-1038-s41598-025-96508-3` |
| 2 | Comparing Large Language Models for Text Classification: Model Selection Across Tasks, Texts, and Languages | https://doi.org/10.31219/osf.io/jvgc5_v3 | `doi-10-31219-osf-io-jvgc5-v3` |
| 2 | Crowd-sourced Text Analysis: Reproducible and Agile Production of Political Data (unsure) | https://doi.org/10.1017/S0003055416000058 | `doi-10-1017-s0003055416000058` |
| 2 | CrowdTruth: Machine-Human Computation Framework for Harnessing Disagreement in Gathering Annotated Data (unsure) | https://doi.org/10.1007/978-3-319-11915-1_31 | `doi-10-1007-978-3-319-11915-1-31` |
| 2 | General purpose computer-assisted clustering and conceptualization (unsure) | https://doi.org/10.1073/pnas.1018067108 | `doi-10-1073-pnas-1018067108` |
| 2 | GPT is an effective tool for multilingual psychological text analysis | https://doi.org/10.1073/pnas.2308950121 | `doi-10-1073-pnas-2308950121` |
| 2 | How to Use Large-Language Models for Text Analysis | https://doi.org/10.4135/9781529683707 | `doi-10-4135-9781529683707` |
| 2 | Human-LLM Collaborative Annotation Through Effective Verification of LLM Labels | https://doi.org/10.1145/3613904.3641960 | `doi-10-1145-3613904-3641960` |
| 2 | Humans vs. ChatGPT: Evaluating Annotation Methods for Financial Corpora | https://doi.org/10.1109/BigData59044.2023.10386425 | `doi-10-1109-bigdata59044-2023-10386425` |
| 2 | Instruments and Artefacts: Mapping the Adoption of Large Language Models in Social Sciences | https://doi.org/10.31235/osf.io/xe87h_v1 | `doi-10-31235-osf-io-xe87h-v1` |
| 2 | Introduction to Neural Transfer Learning With Transformers for Social Science Text Analysis (unsure) | https://doi.org/10.1177/00491241221134527 | `doi-10-1177-00491241221134527` |
| 2 | Is ChatGPT better than Human Annotators? Potential and Limitations of ChatGPT in Explaining Implicit Hate Speech (unsure) | https://doi.org/10.1145/3543873.3587368 | `doi-10-1145-3543873-3587368` |
| 2 | Just Put a Human in the Loop? Investigating LLM-Assisted Annotation for Subjective Tasks | https://doi.org/10.18653/v1/2025.findings-acl.1323 | `doi-10-18653-v1-2025-findings-acl-1323` |
| 2 | Large Language Models for Text Classification: From Zero-Shot Learning to Instruction-Tuning | https://doi.org/10.31235/osf.io/sthwk | `doi-10-31235-osf-io-sthwk` |
| 2 | Learning from Disagreement: A Survey (unsure) | https://doi.org/10.1613/JAIR.1.12752 | `doi-10-1613-jair-1-12752` |
| 2 | llmClassificR: Text Classification with Large Language Models, Network Psychometrics, and Calibrated Uncertainty in R | https://doi.org/10.31234/osf.io/259gt_v1 | `doi-10-31234-osf-io-259gt-v1` |
| 2 | LLMs instead of human judges? A large scale empirical study across 20 NLP evaluation tasks | https://doi.org/10.48550/ARXIV.2406.18403 | `doi-10-48550-arxiv-2406-18403` |
| 2 | Navigating Prompt Complexity for Zero-Shot Classification | https://doi.org/10.48550/arxiv.2305.14310 | `doi-10-48550-arxiv-2305-14310` |
| 2 | Observational Equivalence of LLM and Human Annotation | https://doi.org/10.2139/ssrn.7389359 | `doi-10-2139-ssrn-7389359` |
| 2 | Open, Closed, or Small Language Models for Text Classification? | https://doi.org/10.48550/arxiv.2308.10092 | `doi-10-48550-arxiv-2308-10092` |
| 2 | Political-LLM: Large Language Models in Political Science (unsure) | https://doi.org/10.48550/arxiv.2412.06864 | `doi-10-48550-arxiv-2412-06864` |
| 2 | PPI++: efficient prediction-powered inference (unsure) | https://doi.org/10.48550/ARXIV.2311.01453 | `doi-10-48550-arxiv-2311-01453` |
| 2 | Prediction-powered inference (unsure) | https://doi.org/10.48550/ARXIV.2301.09633 | `doi-10-48550-arxiv-2301-09633` |
| 2 | Reliable Annotations with Less Effort: Evaluating LLM-Human Collaboration in Search Clarifications | https://doi.org/10.1145/3731120.3744574 | `doi-10-1145-3731120-3744574` |
| 2 | Rolling Memory: A New Approach to Annotation with Generative LLMs in Social and Political Research | https://doi.org/10.1007/s41111-025-00327-w | `doi-10-1007-s41111-025-00327-w` |
| 2 | Text as Data (unsure) | https://doi.org/10.1257/jel.20181020 | `doi-10-1257-jel-20181020` |
| 2 | Text as Data: The Promise and Pitfalls of Automatic Content Analysis Methods for Political Texts (unsure) | https://doi.org/10.1093/pan/mps028 | `doi-10-1093-pan-mps028` |
| 2 | The effectiveness of LLMs as annotators: A comparative overview and empirical analysis of direct representation | https://doi.org/10.48550/ARXIV.2405.01299 | `doi-10-48550-arxiv-2405-01299` |
| 2 | The Problem of Human Label Variation: On Ground Truth in Data, Modeling and Evaluation (unsure) | https://doi.org/10.18653/v1/2022.emnlp-main.731 | `doi-10-18653-v1-2022-emnlp-main-731` |
| 2 | Updating "The Future of Coding": Qualitative Coding with Generative Large Language Models | https://doi.org/10.1177/00491241251339188 | `doi-10-1177-00491241251339188` |
| 2 | Using large language models to support content analysis: a case study of ChatGPT for adverse event detection (unsure) | https://doi.org/10.2196/52499 | `doi-10-2196-52499` |
| 2 | Validating the use of large language models for psychological text classification | https://doi.org/10.3389/frsps.2025.1460277 | `doi-10-3389-frsps-2025-1460277` |
| 5 | Annotated dataset creation through large language models for non-english medical nlp (unsure) | http://scholar.google.com/scholar_lookup?title=Annotated+dataset+creation+through+large+language+models+for+non-english+medical+nlp&journal=Journal+of+Biomedical+Informatics&doi=10.1016%2Fj.jbi.2023.104478&volume=145&publication_year=2023&author=Frei%2CJohann&author=Kramer%2CFrank | `google-scholar-lookup-4e504f` |
| 5 | Can Generative AI improve social science? (unsure) | https://www.pnas.org/doi/10.1073/pnas.2314021121 | `pnas-pnas-2314021121` |
| 5 | ChatGPT-4 outperforms experts and crowd workers in annotating political twitter messages with zero-shot learning | http://arxiv.org/abs/2304.06588 | `arxiv-2304-06588` |
| 5 | Fine-tuned 'small' LLMs (still) significantly outperform zero-shot generative AI models in text classification | http://arxiv.org/abs/2406.08660 | `arxiv-2406-08660` |
| 5 | Just ask for calibration: Strategies for eliciting calibrated confidence scores from language models fine-tuned with human feedback (unsure) | https://arxiv.org/abs/2305.14975 | `arxiv-2305-14975` |
| 5 | Large language models for data annotation and synthesis: A survey | https://aclanthology.org/2024.emnlp-main.54 | `aclanthology-2024-emnlp-main-54` |
| 5 | Natural Language Annotation for Machine Learning (unsure) | http://scholar.google.com/scholar_lookup?title=Natural+Language+Annotation+for+Machine+Learning&publication_year=2012&author=Pustejovsky%2CJ&author=Stubbs%2CA | `google-scholar-lookup-3d58c6` |
| 5 | Politics as Usual? Measuring Populism, Nationalism, and Authoritarianism with Neural Language Models (unsure) | http://journals.sagepub.com/doi/10.1177/00491241221122317 | `sagepub-00491241221122317` |
| 5 | The Augmented Social Scientist: Using Sequential Transfer Learning to Annotate Millions of Texts with Human-Level Accuracy | http://journals.sagepub.com/doi/10.1177/00491241221134526 | `sagepub-00491241221134526` |

### Code and data repositories (5)

Role: data or reference list. Fetch only if we reuse the code or data.

| Tier | Work | Address | Library id |
|---|---|---|---|
| 2 | Replication Data for: Reform preferences of key actors in the UNFCCC process (unsure) | https://doi.org/10.7910/DVN/ZYTBET | `doi-10-7910-dvn-zytbet` |
| 5 | Alternative Annotator Test (AltTest) code and datasets | https://github.com/nitaytech/AltTest | `github-alttest` |
| 5 | Definition sensitivity of LLM coding (code repository) (unsure) | https://github.com/octner/nips-tae-definition-sensitivity | `github-nips-tae-definition-sensitivity` |
| 5 | event-coding-reliability repository (unsure) | https://github.com/yibo-hu-lab/event-coding-reliability | `github-event-coding-reliability` |
| 5 | Replication package (datasets, notebooks) for LLM fine-tuning study, osf.io/ctgqx (unsure) | https://osf.io/ctgqx/ | `osf-ctgqx` |

### Other reference lists and method pages (10)

Role: data or reference list. Possible reference lists and scoring methods; fetch when the dataset stage needs them.

| Tier | Work | Address | Library id |
|---|---|---|---|
| 1 | LobbyMap FAQ (unsure) | https://lobbymap.org/multipage/FAQ-f9a8629330cd161eba0d9ed43ba17965-785703 | `lobbymap-faq-f9a8629330cd161eba0d9ed43ba17965-785703` |
| 2 | Banking on Climate Chaos: Oil & Gas Expansion League Tables (unsure) | http://www.bankingonclimatechaos.org/sector-tables-2026 | `bankingonclimatechaos-sector-tables-2026` |
| 2 | Caring for Climate: Executive Brief (UN Global Compact) (unsure) | http://www.unglobalcompact.org/docs/issues_doc/Environment/climate/C4C_ExecutiveBrief_Policy.pdf | `unglobalcompact-c4c-executivebrief-policy` |
| 2 | EBS Regulation (EU) 2019/2152 | https://eur-lex.europa.eu/eli/reg/2019/2152/oj/eng | `europa-eng-2` |
| 2 | EU implementing regulation 2020/1197 | https://eur-lex.europa.eu/legal-content/EN/TXT/?uri=CELEX%3A32020R1197 | `europa-txt-f77cb0` |
| 2 | European business profiling — Recommendations manual — 2020 edition - Products Manuals and Guidelines - Eurostat (europa.eu) | https://ec.europa.eu/eurostat/web/products-manuals-and-guidelines/-/ks-gq-20-002 | `europa-ks-gq-20-002` |
| 2 | LobbyMap Methodology Portal | https://lobbymap.org/Methodology-Portal | `lobbymap-methodology-portal` |
| 2 | LobbyMap Our Methodology | https://lobbymap.org/page/Our-Methodology | `lobbymap-our-methodology` |
| 5 | Carbon Majors dataset 2020 | https://climateaccountability.org/carbonmajors_dataset2020.html | `climateaccountability-carbonmajors-dataset2020` |
| 5 | The climate responsibilities of industrial carbon producers | http://scholar.google.com/scholar_lookup?title=The+climate+responsibilities+of+industrial+carbon+producers&journal=Climatic+Change&volume=132&pages=157-171&publication_year=2015&author=Frumhoff%2CPC&author=Heede%2CR&author=Oreskes%2CN | `google-scholar-lookup-47e6f1` |

## Taken out as copies of sources already held

- `transparencycdn-2506-report-behind-the-badge`: duplicate
- `arxiv-2606-06781v2`: duplicate
- `unfccc-changes-to-the-registration-system-and-process-23what-informati`: duplicate
- `climatechangenews-bigger-share-of-cop29-badges-for-global-south-ngos-u-2`: duplicate
- `google-scholar-lookup-722bac`: duplicate
- `kickbigpollutersout-home`: duplicate
- `arxiv-2306-00176`: duplicate

## Screened in from the second round, listed only (99)

On 2026-11-24 the 1,408 candidates that came from the references of the newly downloaded sources were screened on title and context. These were kept in but, under the limit of 50, none is planned for download. The reason is the screener's (sonnet), reviewed by the main session; it rests on the title and the citing sentence only.

| Topic | Tier | Address | Why kept | Library id |
|---|---|---|---|---|
| Q1 | 1 | https://carbonmajors.org/Downloads | Dataset of fossil-fuel producers, usable for company identification | `carbonmajors-downloads` |
| Q1 | 2 | http://dx.doi.org/10.1007/s10784-020-09513-4 | Study of delegation size and NGO support in climate negotiations | `doi-10-1007-s10784-020-09513-4` |
| Q1 | 2 | http://dx.doi.org/10.1038/nclimate1742 | Citation on state representation in climate negotiations | `doi-10-1038-nclimate1742` |
| Q1 | 2 | http://dx.doi.org/10.1080/17565529.2023.2298780 | Study of small island states presence at UNFCCC | `doi-10-1080-17565529-2023-2298780` |
| Q1 | 2 | http://dx.doi.org/10.32422/mv-cjir.1684 | Study of national delegation sizes at international organisations | `doi-10-32422-mv-cjir-1684` |
| Q1 | 2 | https://influencemap.org/insight/Corporate-Climate-Laggards-Outnumber-Leaders-at-COP31-40697 | Analysis of corporate attendees registered for COP31 | `influencemap-corporate-climate-laggards-outnumber-leaders-at-cop31-406` |
| Q1 | 2 | https://unfccc.int/sites/default/files/resource/COP24_observer_guide.pdf | UNFCCC observer guide on admission and access rules | `unfccc-cop24-observer-guide` |
| Q1 | 2 | https://unfccc.int/sites/default/files/resource/How-to-COP_2020.pdf | Counts delegates, parties, observers from UNFCCC participant lists | `unfccc-how-to-cop-2020` |
| Q1 | 2 | https://unfccc.int/process-and-meetings/parties-non-party-stakeholders/non-party-stakeholders/statistics-on-non-party-stakeholders/statistics-on-admission | UNFCCC statistics on admission of observer organisations | `unfccc-statistics-on-admission` |
| Q1 | 2 | https://unfccc.int/process-and-meetings/parties-non-party-stakeholders/non-party-stakeholders/statistics-on-non-party-stakeholders/statistics-on-participation-and-in-session-engagement | UNFCCC statistics on participation by delegates, observers | `unfccc-statistics-on-participation-and-in-session-engagement` |
| Q1 | 3 | https://ecbi.org/sites/default/files/Quo%20Vadis%20COP_0.pdf | Report on COP participant numbers over time | `ecbi-quo-20vadis-20cop-0` |
| Q1 | 3 | https://fossilfreepolitics.org/news/eu-floods-cop28-climate-talks-with-fossil-fuel-lobbyists/ | Counts fossil fuel lobbyists in delegations at COP28 | `fossilfreepolitics-eu-floods-cop28-climate-talks-with-fossil-fuel-lobb` |
| Q1 | 3 | https://www.globalwitness.org/en/press-releases/hundreds-fossil-fuel-lobbyists-flooding-cop26-climate-talks/ | Counts fossil fuel lobbyists at COP26 | `globalwitness-hundreds-fossil-fuel-lobbyists-flooding-cop26-climate-ta` |
| Q1 | 3 | https://www.globalwitness.org/en/press-releases/hundreds-of-fossil-fuel-lobbyists-flooding-cop26-climate-talks/ | Global Witness count of fossil fuel lobbyists at COP26 | `globalwitness-hundreds-of-fossil-fuel-lobbyists-flooding-cop26-climate` |
| Q1 | 3 | https://globalwitness.org/en/methodology/ | Methodology for COP fossil-fuel lobbyist analysis | `globalwitness-methodology` |
| Q1 | 3 | https://www.globalwitness.org/en/press-releases/over-100-more-fossil-fuel-lobbyists-last-year-flooding-crucial-cop-climate-talks/ | counts fossil lobbyists granted COP27 access | `globalwitness-over-100-more-fossil-fuel-lobbyists-last-year-flooding-c` |
| Q1 | 3 | https://kickbigpollutersout.org/big-polluters-at-cop27 | Counts fossil-fuel lobbyists at COP27 | `kickbigpollutersout-big-polluters-at-cop27` |
| Q1 | 3 | https://kickbigpollutersout.org/Release-Polluter-Free-COP30 | Reports fossil industry presence at COP30 | `kickbigpollutersout-release-polluter-free-cop30` |
| Q1 | 5 | https://cdn.cdp.net/cdp-production/cms/reports/documents/000/002/327/original/Carbon-Majors-Report-2017.pdf | Carbon Majors list used to identify fossil fuel organisations at COPs | `cdp-carbon-majors-report-2017` |
| Q1 | 5 | https://corporateeurope.org/en/2022/11/cop27-just-kick-big-polluters-out | Counts trade-association attendance at COPs | `corporateeurope-cop27-just-kick-big-polluters-out` |
| Q1 | 5 | https://corporateeurope.org/en/2024/11/cop29-hycoprisy-0 | counts fossil lobbyists in EU delegations at COP29 | `corporateeurope-cop29-hycoprisy-0` |
| Q1 | 5 | https://docs.google.com/spreadsheets/d/1irVXQGiYuiDjHm4tQjrMl0AFauuoyo1KW6jYiHW8i0I/edit?pli=1&gid=783251733 | Dataset of UNFCCC delegates and fossil fuel lobbyist list | `google-edit-cf4e30` |
| Q1 | 5 | http://scholar.google.com/scholar_lookup?title=Capital+contests%3A+National+and+transnational+channels+of+corporate+influence+on+the+climate+change+negotiations&journal=Politics+%26+Society&doi=10.1177%2F0032329298026003003&volume=26&pages=337-361&publication_year=1998&author=Levy%2CD&author=Egan%2CD | Title: corporate influence on climate negotiations | `google-scholar-lookup-426e8f` |
| Q1 | 5 | http://scholar.google.com/scholar_lookup?title=The+role+of+non-nation-state+actors+and+side+events+in+the+international+climate+negotiations&journal=Climate+Policy&doi=10.1080%2F14693062.2011.579328&volume=12&issue=1&pages=23-37&publication_year=2012&author=Schroeder%2CH&author=Lovell%2CH | Non-state actors and side events in international climate negotiations | `google-scholar-lookup-4d371d` |
| Q1 | 5 | http://scholar.google.com/scholar_lookup?title=How+many+will+attend+Paris%3F+UNFCCC+COP+participation+patterns+1995%E2%80%932015&journal=Environmental+Science+%26+Policy&doi=10.1016%2Fj.envsci.2013.04.001&volume=31&pages=157-159&publication_year=2013&author=Neeff%2CT | Title: UNFCCC COP participation patterns 1995-2015 | `google-scholar-lookup-beee62` |
| Q1 | 5 | https://d.docs.live.net/c25815a5c338d91f/Escritorio/UPDATEDNOV13-Draft%20Position_%20polluting%20industry%20obstruction%20of%20climate%20policy%20JB.docx | Framework differentiating non-Party stakeholders by interest; admission rules | `live-updatednov13-draft-20position-20polluting-20industry-20obstructio` |
| Q2 | 2 | https://transparency-register.europa.eu/document/download/0b39bbcf-231b-4d77-87d1-15b676343daf_en?filename=TR+Annual+Report+2023.pdf | EU Transparency Register annual report; lobby register source | `europa-0b39bbcf-231b-4d77-87d1-15b676343daf-en-4f180f` |
| Q2 | 2 | https://influencemap.org/file/a96828fe4ad311ed90a50629e04faa41 | Report download on corporate capture of IMO; measures corporate lobbying | `influencemap-a96828fe4ad311ed90a50629e04faa41` |
| Q2 | 2 | https://influencemap.org/Benchmarks | LobbyMap benchmarks for assessing corporate climate policy engagement | `influencemap-benchmarks` |
| Q2 | 2 | https://ca100.influencemap.org/report/ca100-disclosure-review | Methodology assessing corporate climate policy engagement disclosures | `influencemap-ca100-disclosure-review` |
| Q2 | 2 | https://ca100.influencemap.org/lobbying-disclosures | Corporate lobbying disclosure assessments with explained scoring | `influencemap-lobbying-disclosures` |
| Q2 | 2 | https://influencemap.org/LobbyMapScores | LobbyMap scores measuring corporate climate lobbying | `influencemap-lobbymapscores` |
| Q2 | 2 | https://influencemap.org/report/Pilot-Studies-Assessing-CA100-Companies-Using-the-Global-Standard-on-Responsible-Climate-Lobbying-19420 | Pilot studies measuring corporate climate lobbying against a standard | `influencemap-pilot-studies-assessing-ca100-companies-using-the-global` |
| Q2 | 2 | https://lobbymap.org/briefing/CH2 | Global Standard on Responsible Climate Lobbying briefing | `lobbymap-ch2` |
| Q2 | 5 | https://climate-lobbying.com/wp-content/uploads/2022/03/2022_global-standard-responsible-climate-lobbying_APPENDIX.pdf | Global Standard on responsible climate lobbying; defines lobbying measures | `climate-lobbying-2022-global-standard-responsible-climate-lobbying-app` |
| Q2 | 5 | https://climate-lobbying.com/ | Global Standard on Responsible Climate Lobbying indicators | `climate-lobbying-home` |
| Q2 | 5 | https://gogel.org/node/10283 | Global Oil and Gas Exit List company data; identifies fossil-fuel companies | `gogel-10283` |
| Q2 | 5 | http://scholar.google.com/scholar_lookup?title=Electric+utilities+and+American+climate+policy%3A+Lobbying+by+expected+winners+and+losers&journal=Journal+of+Public+Policy&doi=10.1017%2FS0143814X15000033&volume=36&issue=2&pages=251-275&publication_year=2015&author=Kim%2CSE&author=Urpelainen%2CJ&author=Yang%2CJ | Lobbying by winners and losers in US climate policy | `google-scholar-lookup-12d900` |
| Q2 | 5 | http://scholar.google.com/scholar_lookup?title=Disaggregating+and+explaining+corporate+political+activity%3A+domestic+and+foreign+corporations+in+national+politics&journal=Am+Polit+Sci+Rev&doi=10.2307%2F2586214&volume=94&pages=891-903&publication_year=2000&author=Hansen%2CWL&author=Mitchell%2CNJ | Title: explaining corporate political activity | `google-scholar-lookup-63eb6c` |
| Q2 | 5 | http://scholar.google.com/scholar_lookup?title=Advancing+the+empirical+research+on+lobbying&journal=Annu+Rev+Polit+Sci&doi=10.1146%2Fannurev-polisci-100711-135308&volume=17&pages=163-185&publication_year=2014&author=Figueiredo%2CJM&author=Richter%2CBK | Review of empirical lobbying research methods | `google-scholar-lookup-9f7ffd` |
| Q2 | 5 | http://scholar.google.com/scholar_lookup?title=The+climate+lobby%3A+A+sectoral+analysis+of+lobbying+spending+on+climate+change+in+the+USA%2C+2000+to+2016&journal=Climatic+Change&doi=10.1007%2Fs10584-018-2241-z&volume=149&pages=289-303&publication_year=2018&author=Brulle%2CRJ | Sectoral analysis of climate lobbying spending, measurement study | `google-scholar-lookup-bef98b` |
| Q2 | 5 | https://www.iigcc.org/resources/investor-expectations-on-corporate-lobbying | Investor expectations and methodology for assessing lobbying disclosure | `iigcc-investor-expectations-on-corporate-lobbying` |
| Q2 | 5 | https://www.oecd-ilibrary.org/governance/lobbying-in-the-21st-century_c6d8eff8-en | OECD report on lobbying transparency and integrity | `oecd-ilibrary-lobbying-in-the-21st-century-c6d8eff8-en` |
| Q2 | 5 | https://www.unpri.org/Uploads/i/k/t/Investor-Expectations-on-Corporate-Climate-Lobbying_en-GB.pdf | methodology assessing corporate climate lobbying disclosure | `unpri-investor-expectations-on-corporate-climate-lobbying-en-gb` |
| context | 1 | https://carbonmajors.org/multipage/About-Carbon-Majors-416 | Carbon Majors methodology page; company list usable to identify fossil-fuel producers | `carbonmajors-about-carbon-majors-416` |
| context | 1 | https://carbonmajors.org/Entities | Fossil entity league table; usable to identify fossil-fuel organisations | `carbonmajors-entities` |
| context | 3 | https://ecbi.org/sites/default/files/Quo%20Vadis%20COP%20December%202020.pdf | Explains named participant lists versus overflow delegates | `ecbi-quo-20vadis-20cop-20december-202020` |
| context | 5 | https://coalexit.org/ | Global Coal Exit List, company list for identifying fossil firms | `coalexit-home` |
| method | 1 | https://carbonmajors.org/FAQ | FAQ on Carbon Majors methodology; fossil producer list | `carbonmajors-faq` |
| method | 1 | https://www.coalexit.org/MCEL | Metallurgical coal company exit list; usable to identify fossil-fuel companies | `coalexit-mcel` |
| method | 1 | https://gogel.org/publications | GOGEL fossil company list update; usable to identify fossil-fuel organisations | `gogel-publications` |
| method | 2 | https://dx.doi.org/10.1017/pan.2024.31 | Method: synthetic text for supervised text classification | `doi-10-1017-pan-2024-31` |
| method | 2 | https://dx.doi.org/10.1017/psrm.2024.35 | Practical guide to classifying beliefs in text; classification method | `doi-10-1017-psrm-2024-35` |
| method | 2 | https://dx.doi.org/10.1038/s43588-023-00585-1 | Proprietary language models in research; LLM method source | `doi-10-1038-s43588-023-00585-1` |
| method | 2 | https://dx.doi.org/10.1177/20531680241231468 | LLM coding of open-text responses; method source for classification | `doi-10-1177-20531680241231468` |
| method | 2 | https://dx.doi.org/10.1177/20531680241236239 | LLMs annotating political text; classification method | `doi-10-1177-20531680241236239` |
| method | 2 | https://dx.doi.org/10.1609/icwsm.v19i1.35807 | Experiment on prompt design for LLM text annotation accuracy | `doi-10-1609-icwsm-v19i1-35807` |
| method | 2 | https://dx.doi.org/10.18653/v1/2023.emnlp-main.575 | LM annotation agreement with humans; LLM classification method | `doi-10-18653-v1-2023-emnlp-main-575` |
| method | 2 | https://dx.doi.org/10.2307/2529310 | Landis and Koch inter-rater agreement; validating classifications | `doi-10-2307-2529310` |
| method | 2 | https://dx.doi.org/10.52202/075280-3000 | LLM surrogates for downstream inference in social science; LLM classification method | `doi-10-52202-075280-3000` |
| method | 2 | https://doi.org/10.7910/DVN/NUWHQP | Replication data for LLM codebook classification paper | `doi-10-7910-dvn-nuwhqp` |
| method | 2 | https://eur-lex.europa.eu/legal-content/EN/ALL/?uri=celex%3A32006R1893 | NACE Rev. 2 industry classification regulation | `europa-all-5586ff` |
| method | 2 | https://ec.europa.eu/eurostat/web/nace/correspondence-tables | NACE industry classification correspondence tables; usable for classifying businesses | `europa-correspondence-tables` |
| method | 2 | https://transparency-register.europa.eu/index_en | EU transparency register: lobby register for identifying organisations | `europa-index-en-2` |
| method | 2 | https://ec.europa.eu/eurostat/web/products-manuals-and-guidelines/w/ks-01-26-047 | NACE industry classification, usable for classifying organisations | `europa-ks-01-26-047` |
| method | 2 | https://ec.europa.eu/eurostat/documents/3859598/21633320/KS-GQ-24-007-EN-N.pdf | NACE Rev 2.1 industry classification guidelines | `europa-ks-gq-24-007-en-n` |
| method | 2 | https://eur-lex.europa.eu/eli/reg_del/2023/137/oj | NACE Rev. 2.1 industry classification regulation; usable for classifying organisations | `europa-oj` |
| method | 2 | https://ec.europa.eu/eurostat/web/nace/transition | NACE Rev 2.1 industry classification transition | `europa-transition` |
| method | 2 | https://lobbymap.org/briefing/CH1 | Global Standard on Responsible Climate Lobbying; defines lobbying measurement | `lobbymap-ch1` |
| method | 5 | https://aclanthology.org/D18-1487 | Method paper on estimating document class prevalence | `aclanthology-d18-1487` |
| method | 5 | https://arxiv.org/abs/2306.02177 | Coding social science datasets with language models | `arxiv-2306-02177` |
| method | 5 | https://arxiv.org/abs/2409.02078 | Zero-shot and few-shot classifiers for political text | `arxiv-2409-02078` |
| method | 5 | https://climateaccountability.org/wp-content/uploads/2020/12/MRR-9.1-Apr14R.pdf | Carbon Majors methods; usable fossil company list | `climateaccountability-mrr-9-1-apr14r` |
| method | 5 | https://www.coalexit.org/methodology | methodology for fossil company exit lists | `coalexit-methodology` |
| method | 5 | https://gem.wiki/ | Global Energy Monitor, reference list of fossil fuel companies | `gem-home` |
| method | 5 | https://github.com/npangakis/gpt_annotate | Code for GPT annotation of text; LLM classification method | `github-gpt-annotate` |
| method | 5 | https://gogel.org/node/10285 | GOGEL oil and gas exit list data page; identifies fossil-fuel companies | `gogel-10285` |
| method | 5 | https://gogel.org/node/10287 | GOGEL methodology on company data sources and risk categories | `gogel-10287` |
| method | 5 | https://gogel.org/gogel-explainedinfocus | Global Oil and Gas Exit List criteria for identifying fossil companies | `gogel-gogel-explainedinfocus` |
| method | 5 | https://gogel.org/gogelexplained | GOGEL methodology and inclusion thresholds for fossil company list | `gogel-gogelexplained` |
| method | 5 | https://scholar.google.com/scholar?q=Thalken%2C+R.%2C+Stiglitz%2C+E.%2C+Mimno%2C+D.%2C+&+Wilkens%2C+M.+%282023%29.+%E2%80%9CModeling+Legal+Reasoning%3A+LM+Annotation+at+the+Edge+of+Human+Agreement.%E2%80%9D+In+H.+Bouamor%2C+J.+Pino%2C+and+K.+Bali+%28Eds.%29+EMNLP%2C+Singapore+9252%E2%80%939265.10.18653%2Fv1%2F2023.emnlp-main.575= | LM annotation of legal text; method on LLM classification | `google-scholar-02a747` |
| method | 5 | https://scholar.google.com/scholar?q=Wang%2C+X.%2C+Hu%2C+C.%2C+Ma%2C+B.%2C+R%C3%B6ttger%2C+P.%2C+and+Plank%2C+B..+2024.+%E2%80%9CLook+at+the+Text%3A+Instruction-Tuned+Language+Models+are+More+Robust+Multiple+Choice+Selectors+Than+You+Think.%E2%80%9D+In+COLM%2C+Philadephia%2C+PA%2C+USA | Instruction-tuned LMs as text classifiers | `google-scholar-499a7e` |
| method | 5 | https://scholar.google.com/scholar?q=Atreja%2C+S.%2C+Ashkinaze%2C+J.%2C+Li%2C+L.%2C+Mendelsohn%2C+J.%2C+and+Hemphill%2C+L..+2025.+%E2%80%9CWhat%27s+in+a+Prompt%3F%3A+A+Large-Scale+Experiment+to+Assess+the+Impact+of+Prompt+Design+on+the+Compliance+and+Accuracy+of+LLM-Generated+Text+Annotations.%E2%80%9D+Proceedings+of+the+International+AAAI+Conference+on+Web+and+Social+Media+19%3A+122%E2%80%93145.10.1609%2Ficwsm.v19i1.35807 | Prompt design and LLM text annotation accuracy | `google-scholar-60cb36` |
| method | 5 | https://scholar.google.com/scholar?q=Rytting%2C+C.+M.%2C+et+al.+2023.+%E2%80%9CTowards+Coding+Social+Science+Datasets+with+Language+Models.%E2%80%9D+Preprint%2C+arXiv%3A2306.02177 | Using language models to code social science datasets | `google-scholar-8ca072` |
| method | 5 | https://scholar.google.com/scholar?q=Pangakis%2C+N.%2C+and+Wolken%2C+S..+2024.+%E2%80%9CKnowledge+Distillation+in+Automated+Annotation%3A+Supervised+Text+Classification+with+LLM-Generated+Training+Labels.%E2%80%9D+In+D.+Card%2C+A.+Field%2C+D.+Hovy%2C+and+K.+Keith+%28Eds.%29+NLP+CSS+Workshop%2C+Mexico+City%2C+Mexico+113%E2%80%93131 | LLM-generated labels for text classification; method source | `google-scholar-928ab7` |
| method | 5 | https://scholar.google.com/scholar?q=Halterman%2C+A.%2C+and+Keith%2C+K.+A..+2025.+%E2%80%9CReplication+Data+for+%E2%80%9CCodebook+LLMs%3A+Evaluating+LLMs+as+Measurement+Tools+for+Political+Science+Concepts%E2%80%9D.%E2%80%9D+Harvard+Dataverse.+https%3A%2F%2Fdoi.org%2F10.7910%2FDVN%2FNUWHQP | Codebook LLMs: LLMs as measurement tools; replication data | `google-scholar-c9feed` |
| method | 5 | https://scholar.google.com/scholar?q=Egami%2C+N.%2C+Hinck%2C+M.%2C+Stewart%2C+B.%2C+and+Wei%2C+H..+2023.+%E2%80%9CUsing+Imperfect+Surrogates+for+Downstream+Inference%3A+Design-Based+Supervised+Learning+for+Social+Science+Applications+of+Large+Language+Models.%E2%80%9D+In+A.+Oh%2C+T.+Naumann%2C+A.+Globerson%2C+K.+Saenko%2C+M.+Hardt%2C+and+S.+Levine+%28Eds.%29+NeurIPS%2C+New+Orleans+36%3A+10088%E2%80%9310115 | Supervised learning with LLM annotations for social science | `google-scholar-d4a5ee` |
| method | 5 | https://scholar.google.com/scholar?q=Burnham%2C+M.%2C+Kahn%2C+K.%2C+Wang%2C+R.+Y.%2C+and+Peng%2C+R.+X..+2024.+%E2%80%9CPolitical+Debate%3A+Efficient+Zero-Shot+and+Few-Shot+Classifiers+for+Political+Text.%E2%80%9D+Preprint%2C+arXiv%3A2409.02078 | zero/few-shot classifiers for political text | `google-scholar-f2fc56` |
| method | 5 | https://scholar.google.com/scholar_lookup?title=Measurement+Validity%3A+A+Shared+Standard+for+Qualitative+and+Quantitative+Research&author=Adcock+R.&author=Collier+D.&publication+year=2001&journal=American+Political+Science+Review&volume=95&doi=10.1017%2FS0003055401003100&pages=529-546 | Measurement validity standard; validating classifications | `google-scholar-lookup-0d7b25` |
| method | 5 | https://scholar.google.com/scholar_lookup?title=Large+Language+Models+as+a+Substitute+for+Human+Experts+in+Annotating+Political+Text&author=Heseltine+M.&author=Clemm+von+Hohenberg+B.&publication+year=2024&journal=Research+%26+Politics&volume=11&doi=10.1177%2F20531680241236239 | LLMs annotating political text | `google-scholar-lookup-48b3a5` |
| method | 5 | https://scholar.google.com/scholar_lookup?title=ChatGPT+Outperforms+Crowd+Workers+for+Text-Annotation+Tasks&author=Gilardi+F.&author=Alizadeh+M.&author=Kubli+M.&publication+year=2023&journal=PNAS&volume=120&doi=10.1073%2Fpnas.2305016120 | LLM versus crowd workers for annotation | `google-scholar-lookup-a13359` |
| method | 5 | https://scholar.google.com/scholar_lookup?title=Using+Proprietary+Language+Models+in+Academic+Research+Requires+Explicit+Justification&author=Palmer+A.&author=Smith+N.+A.&author=Spirling+A.&publication+year=2024&journal=Nature+Computational+Science&volume=4&doi=10.1038%2Fs43588-023-00585-1&pages=2-3 | Using proprietary language models in academic research | `google-scholar-lookup-b3d089` |
| method | 5 | https://scholar.google.com/scholar_lookup?title=Can+Large+Language+Models+Transform+Computational+Social+Science%3F&author=Ziems+C.&author=Held+W.&author=Shaikh+O.&author=Chen+J.&author=Zhang+Z.&author=Yang+D.&publication+year=2024&journal=Computational+Linguistics&volume=50&doi=10.1162%2Fcoli_a_00502&pages=237-291 | Large language models in computational social science; LLM method source | `google-scholar-lookup-d4196d` |
| method | 5 | https://scholar.google.com/scholar_lookup?title=Do+AIs+Know+What+the+Most+Important+Issue+is%3F+Using+Language+Models+to+Code+Open-Text+Social+Survey+Responses+at+Scale&author=Mellon+J.&author=Bailey+J.&author=Scott+R.&author=Breckwoldt+J.&author=Miori+M.&author=Schmedeman+P.&publication+year=2024&journal=Research+%26+Politics&volume=11&doi=10.1177%2F20531680241231468 | Language models for coding open-text survey responses | `google-scholar-lookup-f60ff0` |
| method | 5 | https://www.ieta.org/memberships/ | Trade association membership page; identifies business organisations | `ieta-memberships` |
| method | 5 | https://www.ncbi.nlm.nih.gov/pubmed/37463210 | LLM versus crowd workers for text annotation | `nih-37463210-2` |
| method | 5 | https://www.ncbi.nlm.nih.gov/pubmed/38177494 | Proprietary language models in research; LLM method source | `nih-38177494` |
| method | 5 | https://www.ncbi.nlm.nih.gov/pubmed/843571 | observer agreement measure for categorical coding | `nih-843571` |
| method | 5 | https://www.opensecrets.org/federal-lobbying/industries/summary?cycle=2022&id=E01 | Lobbying register summary for oil and gas industry | `opensecrets-summary-3aa013` |

## Already on disk but not yet read (25)

These cost nothing to obtain. They are the cheapest next reading batch.

| Topic | Library id | Words held |
|---|---|---|
| Q1 | `doi-10-5281-zenodo-14010847` | 61 |
| Q1 | `influencemap-index` | 352 |
| Q1, Q2 | `unfccc-636674` | 21 |
| Q1, Q2 | `unfccc-644763` | 16 |
| Q2 | `doi-10-1016-j-erss-2018-11-017` | 0 |
| Q2 | `doi-10-1016-j-erss-2021-102271` | 0 |
| Q2 | `doi-10-1016-j-jfs-2022-101049` | 0 |
| Q2 | `fossilfreepolitics-112-orgs-tell-hoekstra-not-to-bring-fossil-fuel-lob` | 1140 |
| Q2 | `globalwitness-i-hope-the-younger-generations-can-forgive-us-state-oil` | 38 |
| context | `transparency-conflicts-of-interest-and-undue-influence-in-climate-acti` | 228 |
| context | `transparency-cop-co-opted-how-corruption-and-undue-influence-threaten` | 299 |
| context | `transparency-cop30-talks-at-risk-transparency-international-calls-for` | 456 |
| context | `transparency-transparency-international-partners-call-immediate-action` | 520 |
| context | `unfccc-private-sector-finance-engagement` | 0 |
| context | `unglobalcompact-501` | 91 |
| method | `bankingonclimatechaos-home` | 377 |
| method | `climatechangenews-bigger-share-of-cop29-badges-for-global-south-ngos-u` | 124 |
| method | `europa-ks-gq-20-006` | 12 |
| method | `influencemap-our-methodology` | 147 |
| method | `kickbigpollutersout-method-faqs` | 0 |
| method | `lobbymap-benchmarks` | 246 |
| method | `lobbymap-home` | 453 |
| method | `nips-d862f7f5445255090de13b825b880d59-abstract-conference` | 277 |
| method | `unfccc-changes-to-the-registration-system-and-process` | 432 |
| method | `unfccc-statistics-on-side-events-and-exhibits` | 96 |

## Could not be downloaded: to supply by hand (16)

A refusal by a publisher or by a site's robots.txt is respected, not worked round. If you have access, save the PDF and it will be added to the library.

| Library id | Address | What happened |
|---|---|---|
| `ac-ej-20goodwin-20jel-20article` | http://eprints.nottingham.ac.uk/51218/1/EJ%20Goodwin%20JEL%20Article.pdf | download failed: HTTP 404 |
| `doi-10-1073-pnas-2305016120` | https://doi.org/10.1073/pnas.2305016120 | download failed: HTTP 403 |
| `doi-10-1080-09644016-2022-2058815` | https://doi.org/10.1080/09644016.2022.2058815 | download failed: HTTP 403 |
| `doi-10-1093-jel-eqz007` | https://doi.org/10.1093/jel/eqz007 | download failed: HTTP 403 |
| `doi-10-1093-jel-eqz015` | https://doi.org/10.1093/jel/eqz015 | download failed: HTTP 403 |
| `doi-10-1093-socpro-spab040` | https://doi.org/10.1093/socpro/spab040 | download failed: HTTP 403 |
| `doi-10-1111-rego-70000` | https://doi.org/10.1111/rego.70000 | download failed: HTTP 403 |
| `doi-10-1177-08944393241286471` | https://doi.org/10.1177/08944393241286471 | download failed: HTTP 403 |
| `europa-eng` | https://eur-lex.europa.eu/eli/reg/1993/696/oj/eng | download failed: HTTP 202 |
| `google-edit-322e50` | https://docs.google.com/spreadsheets/d/1irVXQGiYuiDjHm4tQjrMl0AFauuoyo1KW6jYiHW8i0I/edit?pli=1 | download failed: HTTP 410 |
| `influencemap-corporate-captureof-the-un-international-civil-aviation-o` | https://influencemap.org/report/Corporate-Captureof-the-UN-International-Civil-Aviation-Organization-19779 | download failed: HTTP 404 |
| `transparency-businesses-lobbying-practices-2018` | https://knowledgehub.transparency.org/assets/uploads/helpdesk/Businesses-Lobbying-Practices_2018.pdf | download failed: HTTP 404 |
| `unfccc-code-of-conduct-for-unfccc-conferences-meetings-and-events` | https://unfccc.int/about-us/code-of-conduct-for-unfccc-conferences-meetings-and-events | download failed: unfccc.int returned an empty page to the automated download (the same empty page as for unfccc-private-sector-finance-engagement, so the tool wrongly called it a duplicate; corrected 2026-11-24). To be supplied by hand. |
| `unfccc-list-of-admitted-ngos` | https://unfccc.int/process/parties-non-party-stakeholders/non-party-stakeholders/admitted-ngos/list-of-admitted-ngos | download failed: the site returned an empty page |
| `unfccc-process-to-strengthen-observer-engagement-in-the-unfccc-ptsoe` | https://unfccc.int/process-and-meetings/parties-non-party-stakeholders/non-party-stakeholders/overview/process-to-strengthen-observer-engagement-in-the-unfccc-ptsoe | download failed: unfccc.int returned an empty page to the automated download (the same empty page as for unfccc-private-sector-finance-engagement, so the tool wrongly called it a duplicate; corrected 2026-11-24). To be supplied by hand. |
| `unfccc-what-are-parties-non-party-stakeholders` | https://unfccc.int/process-and-meetings/what-are-parties-non-party-stakeholders | download failed: unfccc.int returned an empty page to the automated download (the same empty page as for unfccc-private-sector-finance-engagement, so the tool wrongly called it a duplicate; corrected 2026-11-24). To be supplied by hand. |

Held but empty or only a stub, also to supply by hand: `doi-10-1016-j-erss-2018-11-017`, `doi-10-1016-j-erss-2021-102271`, `doi-10-1016-j-jfs-2022-101049`, `doi-10-1016-j-enpol-2024-114103`, `kickbigpollutersout-method-faqs`, `unfccc-private-sector-finance-engagement`, `europa-ks-gq-20-006`.

Also wanted in full text: `doi-10-1111-j-1475-6765-2004-00157-x`, `doi-10-s10584-022-03466-0`, `doi-10-1017-s0003055401003100`, `nature-s42256-023-00783-6` and `doi-10-1057-eps-2016-17` ("What is access?"), of which only the abstract could be read.
