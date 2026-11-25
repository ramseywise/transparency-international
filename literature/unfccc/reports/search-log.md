# Search log

## 1. Business and fossil fuel presence in COP delegations (study: unfccc)

### Questions the literature should answer

- Q1: how have earlier studies counted and defined business presence in COP delegations?
- Q2: how have they identified fossil fuel-linked participants, and with which lists or data?
- Method: how do registration and badge types (Party, Party overflow) work?
- Context: how are lobbying, undue influence and conflict of interest defined for the UN climate process?

### Scope agreed so far

Sources of any type (papers, NGO reports, official documents, datasets, news), any year, in English. Not yet agreed with the lead researcher: a year limit, and other languages.

### Search 1: the three sources named in the brief, 2026-11-24

| Source | How obtained | Result |
|---|---|---|
| ti-2025-trade-fair (web article) | downloaded from transparency.org | 42 paragraphs |
| ti-2026-formal-delegations (web article) | downloaded from transparency.org | 50 paragraphs |
| ti-2025-fuelling-delay (PDF report) | file supplied by the researcher | 37 pages |

Downloads: 2 of 2 succeeded. All three are extracted and indexed (221 passages).

### Search 2: references inside those three sources, 2026-11-24

Where: every link in the body text of the two articles, and every link and endnote reference in the report. No database or web search has been run yet.

| Stage | Count |
|---|---|
| References found | 134 |
| Screened in | 51 |
| Screened out | 83 |
| Downloaded (approved by Ramsey, 2026-11-24) | 31 |
| Download failed | 12 (9 refused by the publisher, 1 page not found, 2 the site asks automated tools not to fetch) |
| Duplicate of a source already held | 1 |
| No web address in the citing source | 7 |
| Read into a record | 15 (the three seed sources and 12 of the downloads) |
| Quotes in those 15 records checked against the source text | 274 of 274 found, on the page given |

Screening was done from the title, the link text and the sentence each reference was cited in, not from the reference itself. The decision and a one-line reason are in `ledger.jsonl` for every item.

**Kept if** the reference does one of these: counts or analyses who attends COPs; counts, defines or classifies fossil fuel-linked participants; is a data source or method for deciding whether an organisation is fossil-linked; explains registration and badges; defines lobbying, business engagement, policy capture, undue influence or conflict of interest in the UN climate process; covers business influence on climate policy in Europe.

**Screened out**, with counts:

| Reason | Count |
|---|---|
| General climate science, targets or pledges, not about who attends or how they are classified | 19 |
| Evidence about one company only (kept on file for the organisation research stage) | 23 |
| News about a single example | 12 |
| Conduct of oil-producing states or a COP presidency, not delegation composition | 10 |
| Off topic (for example solar geoengineering, disinformation, general corruption theory) | 10 |
| Apparent duplicate of a kept source (reopen if the kept one differs) | 4 |
| Not a source (home page, donation page) or already held | 5 |

Screened in, by question: Q1 and Q2 together 3, Q1 6, Q2 12, method 7, context 23.

Screened in, by tier: primary 13, core 22, supporting 15, news 1. Tiers describe how often and by what kind of publisher a reference is cited; they do not decide relevance.

Seven screened-in references have no web address in the source and need to be located by hand. Two are known only by their DOI and their title will be confirmed on download.

Of the downloads, 14 hold fewer than 400 words: they are landing pages whose content sits in a file the site does not allow automated tools to fetch, or pages that load their content only in a browser. These count as held but cannot be used until the file is supplied by hand. The list is in `screening.json` (`"thin": true`). Downloads that failed were not retried by another route.

### Search 3: OpenAlex, 2026-11-24

Where: OpenAlex (openalex.org), an open catalogue of scholarly work. Scope: works published from 2015, any language, the 25 best matches per query by the catalogue's own relevance order. Only the search words were sent. A hit becomes a candidate, never a source, until screened.

| Query | Matches | New candidates |
|---|---|---|
| fossil fuel lobbyists UNFCCC climate negotiations delegations | 111 | 24 |
| business non-state actors national delegations climate conference COP | 1,597 | 23 |
| conflict of interest UNFCCC observers polluting industry | 782 | 21 |
| corporate capture climate negotiations fossil fuel industry influence | 8,209 | 23 |
| climate obstruction fossil fuel industry Europe lobbying | 607 | 21 |
| measuring interest group access lobbying European Union business | 45,843 | 25 |
| delegation size composition UNFCCC climate negotiations participants | 265 | 20 |
| state-owned oil companies delegations climate negotiations | 6,179 | 17 |
| large language models text classification validation social science | 259,234 | 25 |
| LLM annotation reliability human coders political science | 5,833 | 25 |
| classifying organisations by sector using language models accuracy | 29,707 | 25 |
| fossil fuel financing banks asset managers classification database | 3,318 | 25 |

Total: 274 new candidates (2 further hits were already cited by our sources).

| Stage | Count |
|---|---|
| Screened in, from title and journal only | 33 |
| Left as candidates, not yet judged | 241 |
| Download approved by Ramsey, 2026-11-24 | 33 |
| Full text obtained and read into a record | 8 |
| Only a summary or an empty page obtained (not usable) | 6 |
| Refused by the publisher's site (HTTP 403), to be supplied by hand | 19 |

The 8 read: 1 on the study's subject (a survey of reform preferences in the UNFCCC process, *Nature Climate Change* 2026) and 7 on method (classification by language models checked against human coders). The 6 not usable: four Elsevier pages that arrive empty (`doi-10-1016-j-enpol-2022-112950`, `doi-10-1016-j-erss-2021-102271`, `doi-10-1016-j-jfs-2022-101049`, `doi-10-1016-j-enpol-2024-114103`) and two pages holding only a summary (`doi-10-14512-oew310112`, `doi-10-4995-carma2024-2024-17830`). The 19 refused are at Oxford University Press, Wiley, Taylor & Francis, Sage, MIT Press and ResearchGate; they are listed in `screening.json` with the outcome "download failed". A refusal was not worked around. Most of the subject literature for Q1 and Q2 is among the 19, so the literature review still rests mainly on NGO and TI sources.

Screened in, by question: Q1 8 (who sits in national delegations, and business access), Q2 10 (vested interests and obstruction in the UNFCCC and Europe 8, fossil fuel financing 2), method 15 (measuring interest-group access in the EU 4, reliability of language-model classification against human coders 11).

Worldwide citation counts were also fetched from OpenAlex for every ledger source with a DOI: found for 262 of 265. They are recorded as a signal for ordering the reading; they measure attention, not fit.

**What the search did not find.** No hit, judged by title, counts business delegates inside EU Party delegations or sorts them by sector. The query on classifying organisations by sector with language models returned mostly unrelated work; three titles look relevant. The query on fossil fuel financing returned two usable titles. These are statements about 25 results per query in one catalogue, not about the whole literature.

**Limits of this search.** One catalogue; 25 results per query; relevance judged by title; NGO and official reports are poorly covered by OpenAlex; peer-review status is not given by the catalogue and is left empty.

### Not yet done

- Work that cites the three seed sources (forward citations).
- Web search for NGO and official reports not cited by the three sources.
- Published lists of fossil-linked companies and financiers beyond those cited.
- Judging the 241 remaining candidates from search 3.
- Leads named by the readers and not yet located: Climate Action Network's 2020 position on conflicts of interest, a TI EU report on fossil fuel lobbying, CIEL's "COP We Need".

## 2026-11-24: three sources supplied by hand

Ramsey downloaded three documents that the tool could not fetch and placed them in `literature/pdfs/`: "Behind the Badge", the list of fossil fuel-linked entities across three tiers, and the InfluenceMap methodology note for Transparency International. Each was added to the ledger, read into a record and indexed. No new search was run.

Counts after this step, from `literature/screening.json`: 1,309 considered; 87 screened in; 84 screened out; 1,138 candidates; 26 read; 61 screened in and not yet read (30 held but too thin or not yet read, 29 download failed, 7 without a web address, with some overlap). Quote check: 520 of 520 found on the stated page.

## 2026-11-24: fifteen sources supplied by hand

Ramsey downloaded fifteen documents that the tool could not fetch (publisher pages that refuse automated downloads) and placed them in `literature/pdfs/`. Each matched a source already screened in. Each was added to the ledger, its text extracted, read into a record by `source-reader` (sonnet) and indexed. No new search was run.

The links and references printed inside the fifteen files were added to the ledger as candidates, as for every source. This is why the number of sources considered rose from 1,309 to 2,445: most of the new candidates come from the reference lists of one book. None has been downloaded; they are ranked into tiers and wait for screening.

Two corrections to the ledger, both logged in `unfccc/docs/decisions.md`:

- 24 candidate links taken from the book ended in a full stop printed after the address. The stop was removed; one of the 24 was then the same address as an existing candidate and was merged into it; seven that had received a one-word identifier (for example `globalwitness`) were given a proper one. The tool now drops such a stop itself.
- The separate entry for chapter 10 of the book (download failed) is now screened out as a duplicate, because the chapter is inside the book file and was read there.

Counts after this step, from `literature/screening.json`: 2,445 considered; 86 screened in; 85 screened out; 2,274 candidates. Of the 86 screened in: 41 read; 45 not read (22 held but a landing page, a summary or not yet read; 16 download failed; 7 without a web address). Quote check: 772 of 772 quotes in 41 records found on the stated page.

Read in part: the book (introduction, chapter 10, chapter 13 and a sample of chapter 3; 9 chapters not read). Not the publisher's final version: Dür, Bernhagen and Marshall (authors' manuscript), Lin and Zhang (arXiv version 2), the paper on delegation size and equity (accepted version). Page numbers in those records are the file's own.

## 2026-11-24: all candidates screened; three method sources added

**Asked for by** Ramsey ("screen the candidates"). Client: Claude Code. Models: twelve sonnet agents judged the candidates in batches; Claude Fable 5.2 reviewed every screened-in decision and applied corrections. No download followed: the screened-in list waits for Ramsey's approval (`literature/screened-in-2026-11-24.md`).

**Starting point.** Until today only 171 sources had a screening decision (87 in, 84 out, later 86 and 85). Every other entry was an undecided candidate.

**Criteria** (unchanged, from the `/find-sources` skill). In, if the work defines or counts business or fossil fuel presence at UNFCCC meetings (Q1, Q2); describes a method for classifying organisations or delegates, or for checking such a classification; or gives rules and context (badges, registration, conflicts of interest, lobbying standards). Out, with one of five fixed reasons. When unsure, in.

**Steps.** (1) 52 links that are plainly not sources (share buttons, citation exports, licence and permission links, author profiles) were screened out by rule. (2) Titles for bare DOIs were looked up in OpenAlex; about 40 could not be looked up (one request was refused) and were judged on the address and the citing sentence. (3) 2,363 candidates were judged by the agents on title, address, the sentence that cites them and who cites them: 369 in, 1,994 out. (4) Review of the 369: 96 moved to out (duplicate 38, off topic 40, news item 8, navigation 8, cannot identify 2); one moved from out to in (a DeSmog report on fossil fuel executives on EU Party badges at COP28). (5) 25 links found inside the Eurostat and GOGEL sources after the batches were built were judged by the reviewer: 7 in, 18 out. One candidate had already been screened in by hand (the UN Global Compact guide).

**Result: 2,439 decisions.** In 280: context 111, method 83, Q1 46, Q2 40. By tier: primary 16, core 155, supporting 14, news 7, low signal 88. 152 of the 280 were marked unsure by the screener and kept in under the rule. Out 2,159: off topic 1,289; navigation or non-source link 422; news item, not a study 204; cannot identify the work 186; duplicate 58. No candidate is left.

**Three method sources added on request of the proposal work:** `kbpo-2025-lobbyist-method-faq`, `urgewald-2024-gogel-methodology`, `eurostat-2024-business-registers-metadata`. Downloaded, read by `source-reader` (sonnet), indexed. Two further ones were not obtained: the UN Global Compact guide (robots.txt does not allow automated access; not worked around) and the LobbyMap methodology portal (timed out twice).

**Counts after this step,** from `literature/screening.json`: 2,614 considered; 370 screened in; 2,244 screened out; 0 candidates. Of the 370: 44 read; 280 screened in today and not downloaded; 22 held but a landing page, a summary or not yet read; 17 download failed; 7 without a web address. Quote check: 851 of 851 quotes in 44 records found. Index: 60 sources, 5,045 passages.

**Change to the tool.** The export listed a link only if a held source mentions it, or it was screened in, or a file is held. 141 screened-out links are no longer mentioned by any held source (the page that linked them was replaced by the full text), so the export dropped them and its check failed. The export now lists every entry that has a decision (`literature/src/rag/screening.py`, test added). This is why "considered" is 2,614 and not 2,473.

**Limits.** Screening was on title, address and citing sentence, not on the text. Works that could not be identified from those (186) are out and may include relevant ones; two malformed links to Nature journals are among them (`doi-articles-s41598-025-23798-y`, `doi-articles-s41558-026-02723-9`). More than half of the screened-in list is marked unsure. The screening has not been through `/check-work`.

## 2026-11-24: relevance, the limit of 50, first reading batch of 25, files by topic

**Asked for by** Ramsey. Client: Claude Code. Models: Claude Fable 5.2 (relevance assessment, review, tool changes); `source-reader` on sonnet (the 17 reading records). No new search was run.

**Decisions by Ramsey, 2026-11-24** (logged in `unfccc/docs/decisions.md`): the screened-in sources may be downloaded where the tool can; reading goes in batches of 25; the literature review holds no more than 50 papers.

**Relevance.** `literature/screened-in-2026-11-24.md` was rewritten. Each screened-in source now has a role (literature review candidate, TI's own publication, earlier count or report, data or reference list, official rule, method reference) and a note on whether it adds to what we hold or repeats it. Batch 1 is judged from reading; everything else from title, address and screening reason only. Batches 2 and 3 (25 each) are named; the rest is a reserve, grouped by what it would repeat.

**Batch 1 (25).** 17 obtained and read into records; 8 not obtained (two publisher refusals, 403; one page not found, 404; one spreadsheet removed, 410; one EU law page not returned; two TI documents behind a robots.txt refusal; one empty UNFCCC page). Refusals were not worked round. Of the 17 read: four are landing pages only (`influencemap-corporateinfluencedatabase`, `europa-overview-2`, `carbonmajors-index`, `gogel-home`), one an abstract only (`doi-10-1057-eps-2016-17`), one a summary page (`influencemap-corporate-capture-of-the-imo-…`), one a conference draft marked not for citation (`peio-…kaya-schofield…`). The readers could not view figures.

**Ledger corrections.** Seven screened-in entries were found to be copies of sources already held and were screened out as duplicates: `transparencycdn-2506-report-behind-the-badge`, `arxiv-2606-06781v2`, `unfccc-changes-to-the-registration-system-and-process-23what-informati`, `climatechangenews-bigger-share-of-cop29-badges-for-global-south-ngos-u-2`, `google-scholar-lookup-722bac`, `kickbigpollutersout-home`, `arxiv-2306-00176`. One entry was wrongly matched as a duplicate (`unfccc-list-of-admitted-ngos`: the site returned an empty page, the same as another empty UNFCCC page) and was put back to screened in. Two addresses were replaced by a better one for the same work: Hanegraaff 2015 (DOI checked with Crossref: `doi-10-1162-glep-a-00273`) and the Kick Big Polluters Out COP30 release (found by web search: `kickbigpollutersout-release-kick-out-the-suits-cop30`).

**New candidates.** The links inside the 17 sources added 277 candidates. They are ranked into tiers and not screened.

**Record corrections after the quote check.** `bankingonclimatechaos-methodology-2026`: page of one quote corrected from 8 to 7. `arxiv-2306-00176-2`: one quote replaced by the wording in the source (page 15). `gogel-home` and `europa-overview-2`: missing fields filled (topic; date and reader).

**Changes to the tools** (shared; tests added; reasons also in `unfccc/docs/decisions.md`):

- Quote check (`literature/src/rag/quotes.py`): invisible zero-width characters are ignored when a quote is compared with the source. One PDF (the Banking on Climate Chaos company list) has such a character round every group of words, so true quotes were reported as not found. Wording is still compared exactly.
- Files by topic (`literature/src/rag/views.py`, run by `rag export`): `literature/by-topic/` now shows the held files by topic and by read or to-read. It holds links only. The files stay in `pdfs/` and `pages/`, because the ledger, the records and the index address them there and raw files never move.

**Counts after this step,** from `literature/screening.json`: 2,894 considered; 366 screened in; 2,251 screened out; 277 candidates. 61 read (44 before, 17 today). Quote check: 1,082 of 1,082 quotes in 61 records found on the stated page. Index: 78 sources, 5,685 passages. By-topic view: 85 links (read 61, to read 24; two sources are listed under two topics).

**Limits.** What the 17 new records say is retrieved by a reader agent and has not been independently verified. The relevance of every source outside batch 1 is judged without reading it. Three files in `literature/pages/` are not referred to by any ledger entry (`doi-10-1016-j-enpol-2022-112950.html`, `doi-10-14512-oew310112.html`, `doi-10-4995-carma2024-2024-17830.html`); they were left untouched and need a look. This step has not been through `/check-work`.

## 2026-11-24: batch 2, the four kept from batch 3, second screening round, independent check

**Asked for by** Ramsey. Client: Claude Code. Models: Claude Fable 5.2, then Claude Opus 5.5 (main session: review, verification of the checkers' findings, corrections); `source-reader`, the screeners and `citation-checker` on sonnet.

**Decisions by Ramsey, 2026-11-24** (logged in `unfccc/docs/decisions.md`): the 44 sources read before batch 1 are kept; batches 1 and 2 are read; from batch 3 only four works are kept (Bäckstrand et al. 2017, `google-scholar-lookup-859b9e`; Nasiritousi and Linnér 2016, `google-scholar-lookup-b4b729`; Schroeder and Lovell 2012, `google-scholar-lookup-52c8dc`; *Laggards to Leaders*, `doi-10-1163-9789004372887-004`); the rest of batch 3 and the reserve are not planned and stay screened in, so the decision can be revisited.

**Batch 2 (25).** 18 read into records, 7 not (not obtained, or only an empty or landing page). Of those read, four are an abstract or preview only and one a landing page. Most of the academic works were filed by the reader under context, not Q1 or Q2.

**The four kept from batch 3.** One obtained and read (Nasiritousi and Linnér). Three refused by the publisher or the search engine (403); not worked round; to be supplied by hand. Of the rest of batch 3, `lobbymap-lobbymap-methodology-24422` was already on disk and has been read; the other 20 are listed as not planned in `literature/screened-in-2026-11-24.md`.

**Second screening round.** 1,408 candidates from the references of the newly read sources were screened on title and citing sentence by screener agents (sonnet), reviewed by the main session: 99 in, 1,046 out, 263 left undecided. The 99 are listed only, not planned for download (limit of 50).

**Independent check.** 30 reading records were checked against their sources by three `citation-checker` agents (sonnet), not shown the reader's reasoning. No quote was missing or altered; 1 must-fix, 8 should-fix and a set of minor findings were each verified against the source and corrected. The full record, including what was not checked, is `literature/records-review-2026-11-24.md`. Backups of the records as they were before the corrections are kept outside the library.

**Ledger corrections.** `lobbymap-lobbymap-methodology-24422`: file and text were held but not recorded in the ledger; set. `doi-10-s11077-023-09517-2`: authors set (Vormedal and Meckling), from the page's own citation line.

**Loose ends settled.**

- The three files in `literature/pages/` not referred to by the ledger (`doi-10-1016-j-enpol-2022-112950.html`, `doi-10-14512-oew310112.html`, `doi-10-4995-carma2024-2024-17830.html`) are earlier landing-page downloads of works for which Ramsey has since supplied the PDF; the ledger points at the PDF. They are raw files and stay untouched.
- `literature/screened-in-2026-11-24.md`: the InfluenceMap database size is now given as the whole database's, as in the corrected record.

**Known weaknesses, not fixed.**

- The duplicate check in `rag fetch` treats two empty pages as the same document. This once marked a real source as a copy (put right by hand, see the batch 1 entry). Any empty page should be looked at by hand until the tool is changed.
- Two malformed Nature links among the screened-out rows carry the reason "DOI confirmed"; the reason is wrong, the decision (out, cannot identify) stands.
- `transparency-embargoed-ti-eu-pipelines-of-power-report`: the file name says "embargoed". Whether it may be cited is for TI to confirm.
- `transparencycdn-transparency-international-behind-the-badge` is about COP29, and gives 1,770 and 1,773 in different places; it was written after the check's sample was drawn and is unchecked.
- `peio-…kaya-schofield…` is a conference draft marked not for citation.
- Two records have no reader or date (`eurostat-2024-business-registers-metadata`, `urgewald-2024-gogel-methodology`); left as they are, since the reader and date are not recorded anywhere else.

**Counts after this step,** from `literature/screening.json`: 4,031 considered; 471 screened in; 3,297 screened out; 263 candidates. Outcomes: read 84; held, not read 33; download failed 31; no web address 7; duplicate 72; not downloaded 3,804. Quote check: 1,373 of 1,373 quotes in 83 records found on the stated page. Index: 105 sources, 6,828 passages. By topic, read / to read: Q1 15 / 4; Q2 23 / 8; context 14 / 6; method 30 / 10; topic not set 3 read.

**Limits.** The check covered 30 of 84 records; the other 54 are unchecked. Relevance of everything outside batches 1 and 2 rests on title and address only. 34 screened-in works could not be downloaded and are listed for supply by hand in `literature/screened-in-2026-11-24.md`.

## 2026-11-25: four sources supplied by the researcher; their references screened

**Asked for by** Ramsey ("integrate these other four sources … have a look at their references … no duplicates"). Client: Claude Code. Model: Claude Opus 5.5 (main session: matching, screening, ledger edits). No search was run and nothing was downloaded: the screened-in list waits for Ramsey's approval.

**Sources added** (from `literature/pdfs/TI Lit/`, status in): `ti-2024-jetps`, `ti-2026-high-integrity-talks`, `ti-2025-corruption-undermines-climate`, `gverdtsiteli-maslen-undue-influence-draft`. The draft chapter is a Word file, which the tool cannot read; a copy converted to HTML with macOS `textutil` is in `literature/pages/`. Its bibliography has no links, so its 71 entries were matched against the ledger by title, DOI and address, and the new ones added by hand (link kind "reference"). None of the four has been read into a record or indexed: `source-reader` was not available in this session.

**Criteria** unchanged (as in the 2026-11-24 screening). When unsure, in.

**Overlap with earlier screening.**

| | Total | Already in the ledger | New, screened today |
|---|---|---|---|
| Links in the three TI PDFs | 109 | 12 (7 out, 4 in, 1 candidate) | 98 |
| Draft chapter bibliography | 71 | 33 (tagged as also cited by the draft) | 38 |

**Result: 136 decisions.** In 13; out 123.

| Out, reason | Count |
|---|---|
| Just Energy Transition Partnerships (finance and country news) | 46 |
| Corruption in climate finance, or crime in general | 29 |
| General climate science, targets or decisions | 13 |
| Off topic for delegation make-up | 11 |
| News about a single example | 8 |
| Not a source (home or index page) | 8 |
| Conduct of a COP presidency or host | 7 |
| Duplicate (2014 edition of a guide whose 2015 edition is held) | 1 |

In, by question: Q1 3; method 1; context 9. Five of the 13 have no web address and must be found by hand.

**Ledger corrections.** 11 hand-added rows had a source type the ranking does not know (`ngo`); four TI or U4 works were set to `ti`, the rest to `report`.

**Counts after this step,** from `literature/screening.json`: 6,469 considered; 441 screened in; 3,467 screened out; 2,561 candidates (from earlier rounds, not touched today). Outcomes: read 124; held 68; download failed 32; no web address 7; duplicate 74.

**Limits.** Screening was on title, address and the citing sentence. The four new sources are not yet read, indexed or quote-checked. Not through `/check-work`.

## 2026-11-25: download of the 13 screened in from the researcher's four sources

`rag fetch --screened-in` fetches every screened-in source without a file, not only today's 13. It downloaded 138 sources in all, most from the earlier backlog (download failed or not yet fetched); the rest failed (123), had no web address (12) or were duplicates (15). Files kept as downloaded; `fetch-log.jsonl` has each result. `openaccess` was run for three refused papers and `literature/open-access.md` regenerated.

Of the 13: five held with text (observer status guide; Rasmussen and Reher 2023; COP31 Presidency modalities; UNFCCC Partnerships 2024; the regulatory capture article, submitted version, so page numbers may differ from the journal). Eight need supplying by hand: one book with no open copy, two papers refused (403), five with no web address.

**Not done.** Chunks were made for the five, but the `source-reader` agent was not available in this session (Claude Code was not opened in this folder), so none was read into a record, indexed or quote-checked. The 133 or so backlog downloads are also unread.

## 2026-11-25: seven sources without a topic put under context

Seven sources supplied by the researcher were screened in with no topic and showed as `topic-not-set` in the catalogue: `ti-2025-trade-fair`, `ti-2026-formal-delegations`, `ti-2025-fuelling-delay`, `ti-2024-jetps`, `ti-2026-high-integrity-talks`, `ti-2025-corruption-undermines-climate` and `gverdtsiteli-maslen-undue-influence-draft`. All are TI's own publications or drafts on undue influence in the UN climate process, which is what the context topic covers. At Ramsey's suggestion the topic of each was set to `context` in `ledger.jsonl`. Nothing else in their rows changed, and no screening decision changed. (Claude Code, Claude Fable 5.2.)

## 2026-11-25: raw files downloaded again and sorted into topic folders

The raw files were lost from disk and downloaded again from their recorded addresses: 136 identical to the original, 134 different (133 are live web pages), one supplied file found again, 49 sources still without a file. Detail and the list of missing files: `recovery-2026-11-25.md`. The download log has a new entry for each file that differs and a note on each one not recovered; the ledger's file path is emptied for the 49.

The files were then moved from the top of `data/raw/pdfs/` and `data/raw/pages/` into one folder per topic (Q1, Q2, method, context, and `not-screened-in`) by `rag export`: 271 files, content unchanged, stored paths in the ledger, download log and text files updated. Three pages are the file of two ledger rows (one screened in, one screened out); each sits in the folder of the row screened in. The search index was rebuilt (282 sources, 19,566 passages) and `open-access.md` remade. Claude Code, Claude Fable 5.2.

## 2026-11-25: library cleaned up before publication

Asked by Ramsey: keep only relevant sources, make them searchable, then publish the literature folder (raw files, text and index) in the public repository so the MCP server can search it from any machine.

- **Web pages.** A page was kept if it is TI's (transparency.org, transparency.eu), is cited in a study document, or has a reading record. The other 120 pages were removed: file and text deleted, the ledger row set to screened out with the reason and date. The 20 pages that are read but not cited were all kept; nine of them hold only a landing page, an abstract or a preview.
- **PDFs.** Of 14 PDFs held but not read, three were judged not relevant or duplicate and removed (`ac-managment-of-multilateral-negotiations-monheim-final`, `unfccc-sbi2025-inf06`, `ecbi-quo-20vadis-20cop-0`, an earlier copy of a report that is kept). Eleven were read into records by `source-reader` (Sonnet). Their 153 quotes were checked against the text with `rag check-quotes`: 151 found; two corrected (a quote shortened where a footnote mark broke the wording; one page number), then all found. Several of these records cover only part of a long document (the selected passages), not the whole.
- **Files of sources not screened in** (`not-screened-in` folders) were deleted.
- **Unpublished draft.** The text of `gverdtsiteli-maslen-undue-influence-draft` was moved to `data/private/`, which is not in git, so it is not published and not in the index. Later the same day, at Ramsey's request, that folder was deleted: no copy of the draft's text is left in the library. Its ledger row says so.
- **Counts after the clean-up** (`data/processed/screening.json`): 9,534 considered; 302 screened in, 3,608 screened out, 5,624 not yet judged. Of the 302: 145 read into a record, 7 held and not read (TI pages), 119 could not be obtained, 10 with no web address, 21 not downloaded. The search index was rebuilt: 157 sources, 17,889 passages.
- **Limits.** 145 screened-in sources have no text and cannot be searched; 49 of them once had a file that was lost (`recovery-2026-11-25.md`). Proposal v7 section 3.1 still prints the counts from before the clean-up (`unfccc/docs/archived/numbers.md` has both). Relevance of the removed pages was judged by rule (not TI's, not cited, not read), not page by page. This work has not been through `/check-work`.

Claude Code, Claude Fable 5.2; reading by `source-reader` on Sonnet.
