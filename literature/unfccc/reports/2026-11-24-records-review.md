# Independent check of reading records, 2026-11-24

**What was checked:** 30 reading records in `literature/records/`, against the extracted text of each source in `literature/text/`. Sample drawn with seed 20261124: the 22 records written or changed since the 18:05 export, plus 8 drawn at random from the older ones.

**Reviewers:** three independent checkers (10 records each), each following `.claude/agents/citation-checker.md`, model sonnet. They were given the records and the sources only, not the reader's reasoning. Main session: Claude Code, model claude-fable-5-2 (verification of findings), then claude-opus-5-5 (applying the last fixes and this record). All records were backed up before any change.

**Records in the sample:** `doi-10-1111-j-1475-6765-2004-00157-x`, `doi-10-s10584-022-03466-0`, `desmog-big-meat-dairy-delegates-triple-cop28`, `peio-102-80-1443623897416-kaya-schofield-09302015`, `transparencycdn-fossil-fuel-linked-entities`, `doi-10-1017-pan-2025-10017`, `github-unfccc-cop-analysis`, `kickbigpollutersout-demands`, `globalwitness-636-fossil-fuel-lobbyists-granted-access-cop27`, `influencemap-corporate-capture-of-the-imo-902bf81c05a0591c551f96502062`, `doi-10-14324-111-444-ucloe-3116`, `transparency-embargoed-ti-eu-pipelines-of-power-report`, `arxiv-2306-00176-2`, `transparency-conflict-of-interests`, `doi-10-s11077-023-09517-2`, `influencemap-corporateinfluencedatabase`, `climateinvestigations-thousands-of-fossil-fuel-observers-attended-clim`, `lobbymap-lobbymap-methodology-24422`, `carbonmajors-methodology`, `climatenetwork-can-position-on-conflicts-of-interest-2`, `doi-10-1371-journal-pclm-0000370`, `nature-s42256-023-00783-6`, `globalwitness-record-number-fossil-fuel-lobbyists-granted-access-cop28`, `bankingonclimatechaos-methodology-2026`, `doi-10-1017-sus-2020-13`, `google-scholar-lookup-b4b729`, `gogel-about-data`, `nips-d862f7f5445255090de13b825b880d59-paper-conference`, `kickbigpollutersout-release-record-number-fossil-fuel-lobbyists-attend`, `doi-10-1017-s0003055401003100`.

**Headline:** no quote was missing or altered in any of the 30. The problems were in the reader's own wording around the quotes: summaries that went further than the source. Every finding below was checked against the source text before anything was changed. Quotes were never edited except where a quote was replaced by a better one copied exactly from the source.

## Must fix (1), fixed

- `doi-10-s11077-023-09517-2` (Vormedal and Meckling): the citation had no authors and no journal, although the page's own citation line gives them. Set to Irja Vormedal and Jonas Meckling, *Policy Sciences* 57, 101–124 (2024), published online 16 November 2023, issue March 2024; ledger entry updated to match; the limitation "author names are not in the file" removed.

## Should fix (8), fixed

- `influencemap-corporateinfluencedatabase`: the size "over 1000 companies and 330 industry groups" was given for this table; the source gives it for InfluenceMap's whole database. Corrected.
- `climatenetwork-can-position-on-conflicts-of-interest-2`: "has no conflict-of-interest procedures" corrected to "no adequate" procedures, as the source says; a gloss "(polluting industries)" not in the source removed.
- `transparencycdn-fossil-fuel-linked-entities`: sectors (banks, insurer, utilities, plastics firms) were added by the reader; the list gives names only. Now lists names and says the list does not state sectors (APIP's plastics link kept, as its full name in the list says so). A sentence on a US bank under the French delegation and an explanation of the asterisk, neither in the source, removed.
- `climateinvestigations-thousands-of-fossil-fuel-observers-attended-clim`: "the authors compared badge with employer" is not in the source; replaced with "the page does not describe how the employer was established".
- `google-scholar-lookup-b4b729` (Nasiritousi and Linnér): two claims not in the source removed or reworded ("Parties know which groups follow which issues"; the registration system "caps" numbers, now "restricts" as the source says); the reader's remark that the evidence is old for COP31 marked as the reader's, not the authors'.
- `transparency-embargoed-ti-eu-pipelines-of-power-report`: the quote supporting the network count was a footnote about budgets; replaced with the page 5 sentence that gives the count of 52 networks. A limitation marked as the reader's inference; a finding completed with the rest of the source's sentence.
- `doi-10-1017-pan-2025-10017`: "models passed Tests I–III" corrected: most did well, one model (OLMo-7B) did very poorly and was dropped.
- `doi-10-1371-journal-pclm-0000370`: the counts of 14 and 152 apply to a filtered set (407 accounts linked to at least two of the nine organisations and mentioned at least 3 times); now said.

## Minor, fixed

- `nips-d862f7f5445255090de13b825b880d59-paper-conference`: the 10K bills were drawn at random, not from "three topic groups".
- `github-unfccc-cop-analysis`: "side-events database" and "public participant list" were the reader's words; changed to the source's.
- `arxiv-2306-00176-2`: "the LLM tended to over-label positives" marked as the reader's inference.
- `carbonmajors-methodology`: peer review "no" changed to "unknown" (the page does not say).
- `doi-10-1017-sus-2020-13`: limitation added that the author names and article number are not in the extracted text and their source is not recorded.
- `globalwitness-record-number-fossil-fuel-lobbyists-granted-access-cop28`: "a large share" changed to the page's "a vast number" (no share given); a gloss on the coalition's call corrected to "an accountability framework".
- `globalwitness-636-fossil-fuel-lobbyists-granted-access-cop27`: "12 from Oxy" now as the source puts it (the chief executive and 11 colleagues).
- `kickbigpollutersout-release-record-number-fossil-fuel-lobbyists-attend`: the three pre-COP lists were "prepared by KBPO" in the record; the source says only that they were prepared in the months before COP. Corrected.
- `bankingonclimatechaos-methodology-2026`: an empty quote set to null.
- Ledger: `lobbymap-lobbymap-methodology-24422` had no file or text recorded although both are held; set.

## Downgraded or dropped, and why

- `doi-10-s10584-022-03466-0`: a checker called the data-availability limitation contradicted. Downgraded to minor: the record already said the data are available on request; it now uses the source's wording (on request to the lead author, at publication).
- `bankingonclimatechaos-methodology-2026`, one quote "not found": a false alarm; the quote runs across pages 7 and 8 and is found by the quote check.

## Noted, not changed (minor or not verifiable)

`peio-102-80-1443623897416-kaya-schofield-09302015` does not give both sample sizes (1,120 and 2,700); `doi-10-1111-j-1475-6765-2004-00157-x` "about 47 items" is the reader's count; `influencemap-corporate-capture-of-the-imo-…` one gloss; `arxiv-2306-00176-2` page of the cost finding; `carbonmajors-methodology` framing of one proxy; `doi-10-14324-111-444-ucloe-3116` one named site; `nips-…` "100 to 1000"; `lobbymap-lobbymap-methodology-24422` some "stated by authors" flags, and "1000 companies" is also a 2025 goal; `bankingonclimatechaos-methodology-2026` page spans and title; `gogel-about-data` ">90%" is a design target, not a measured result; `doi-10-1017-s0003055401003100` read from the abstract only, as the record says; `desmog-big-meat-dairy-delegates-triple-cop28` one proxy is inference; `doi-10-1371-journal-pclm-0000370` one definition and one limitation loosely worded; `globalwitness-636-…` "manual review" and "at least 636"; `climateinvestigations-…` "three individuals" and "1995 onward" not found in the text and not changed. `doi-10-1017-pan-2025-10017`: the ledger gives 2026 (issue April 2026), the record 2025 (online 19 September 2025); both are true; cite with both dates.

## After the fixes

Quote check: 1,373 quotes in 83 records, all found on the stated page. Index rebuilt (105 sources, 6,828 passages); export rebuilt.

## What was not checked

- The 54 records outside the sample, among them `transparencycdn-transparency-international-behind-the-badge` (written after the sample was drawn).
- Tables and figures inside PDFs, beyond what the text extraction holds; the raw PDF and HTML files themselves.
- Documents linked from a source and figures a source quotes from elsewhere.
- Sources held only as an abstract, preview or landing page: what the full text says.
- Whether the reader's choice of what to record was complete (a checker tests what is written, not what was left out).
