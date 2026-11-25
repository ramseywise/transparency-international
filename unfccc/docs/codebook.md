# Codebook: organisations on the EU and Member State delegations to COP31

**Version:** 0.17 (after the review of wave 1), 2026-11-25. 0.17 answers the three questions of the wave 1 review: a founding law alone is some evidence only (S1, 5.5); every label shows where it comes from (5.5); tier 3 covers every body whose main business is banking, insurance or investing others' money (B19, section 9). On Ramsey's instruction, for the lead researcher to confirm (`decisions.md`). **Version 0.16** (run version for wave 1, after its first batch). Version 0.12 was the candidate for 1.0; 0.13 and 0.14 added test rules; 0.15 puts tier 3 in use (section 9); 0.16 corrects the labels block, makes tier 3 "not applicable" for bodies that are not financial institutions (brief, line 39), and puts the rules beside the strict line (5.5) in use for wave 1, on a simpler scale. All on Ramsey's instruction, for the lead researcher to confirm (`decisions.md`).
**Status (0.15):** Ramsey reported on 2026-11-25 that the codebook is approved for the batch run and gave the tier 3 rule in section 9 (`decisions.md`). The lead researcher's own approval of this exact version, with her name and the date, is not yet on record, so the number stays below 1.0 and every result of the batches is provisional: the batches are run so that she can review the data and confirm or redefine the rules. **Earlier status:** a draft that waits for the lead researcher's answers to the choices in section 9; the version that follows them goes to her for approval. It binds nothing until she approves it; the number becomes 1.0 on approval, and the classification script refuses any version below 1.0.
**Source:** research proposal v7, sections 4, 6 and 8 (`docs/research-proposal.md`), approved 2026-11-25 with questions 1 to 4 answered as recommended (`decisions.md`, "Research proposal approved"). It does not draw on the feasibility test's results. Decision numbers are the tags in the proposal's text; the study has no separate numbered register yet.
**Tested:** on 20 awkward organisations from the data (2026-11-25), drawn apart from the 20 of the feasibility test and kept out of the pilot and the fixed test set; the rules that gave no single answer were rewritten (change log). The test's labels are provisional and are not findings.
**Checked:** versions 0.10 and 0.11, on 2026-11-25, by methods reviews (Claude Opus) and, for 0.10, a citation check (Claude Sonnet); the record is `docs/archived/reviews/codebook-v0.10-review-2026-11-25.md`. This version answers the second review and has not itself been checked. No numbers check: the codebook reports no results.

## 1. What this codebook does

It sets out how each organisation on the delegation lists is described: what kind of body it is, whether it is a business, who owns it, and whether and how it is linked to fossil fuels. Each is a separate attribute. No label carries two of them.

Every attribute has three possible outcomes: a positive value, a negative value, and "unknown" with a reason. A search that finds nothing gives "unknown", never a negative.

Three general rules hold throughout:

- **G1. Organisation level.** The organisation is classified, never the person. A delegate's title, department and relation to the delegation decide no attribute. Counted together for one entry, they may help to show which body the entry means (rule I4), and nothing more.
- **G2. Where a delegate is registered is not evidence.** The delegation, the badge type (party or overflow), and whether a body attends inside a delegation or as an observer say nothing about its ownership, its business status or a fossil fuel link (lead researcher's comment, 2026-11-25: such bodies can sit anywhere).
- **G3. The name is not evidence.** A name may guide a search. It decides no attribute.

Section 9 lists what this version cannot yet decide, and the choices carried at the proposal's recommended value for the lead researcher to confirm.

## 2. Order of decisions

For each organisation, in this order:

1. **Identity** (rule I1). Is the entry an organisation, and which one? If not settled, every attribute is "unknown", class "identity unresolved" (section 7): "generic text" where the entry names no particular body, "could be several entities" where it names one and more than one body bears that name. The nominating country may guide a search and decides nothing. Where a brand covers several related legal entities, the one whose registered name matches the entry is taken; where none matches, "could be several entities", for a person to settle (proposal 6.1). A unit, programme or initiative with no legal form of its own is classified as the body that hosts it, where a source names the host; otherwise "not an organisation". The exception is a municipal utility run inside a local authority: rule B10 applies and its kind is K2, with the host recorded. The proposal (6.1) foresees nine identity rules; those for branches, mergers, joint ventures and a body named in two delegations are not yet written, and such a case is "unknown", reason "not covered by the codebook".
   - **"i.A." (I2).** "X i.A. Y" (*im Auftrag*, on behalf of) names the delegate's employer X and the body Y it acts for. The organisation is X; Y is kept in the field "acting for" and decides no attribute of X. A bare "i.A. Y" names no employer: identity unresolved, reason "not an organisation", with Y recorded as acting for. It is never read as Y. Cleaning splits the value before matching.
   - **Acronyms (I3).** A match that rests on an acronym alone settles neither identity nor kind. A source must give the full name, in the context of the nominating country, before an acronym is taken as that body; otherwise "could be several entities", and rule I4 may then apply.
   - **The list's own context (I4).** *Test rule, 0.14 draft; Ramsey's instruction of 2026-11-25, not approved.* Where the organisation search leaves an entry "could be several entities" or "generic text", the job titles, departments, places and stated relation to the delegation of all delegates under that entry, counted together and never one person's alone, may point to one body. This is allowed in two cases: the context chooses one among candidate bodies that a source has already named; or it shows that every body the entry could mean is of one type under one parent (for example the embassies of the nominating country), so that their attributes are the same. The strict line does not change: identity stays unresolved and every strict label stays "unknown" with its reason. The attributes of the body pointed to are recorded beside it as inferred values, basis proxy, rule I4, low confidence, each citing a stored source about that body or its parent (5.5). The counts used are kept in the evidence record under `list_context`, without names.
   - **Order of search (I5).** *Test rule, 0.14 draft.* The same four steps for every entry, in this order, stopping at the first that settles identity: (1) the organisation's name as written, in Roman letters and, where a source gives it, in the script of the nominating country; (2) the list's own context (I4); (3) a lookup of the delegates under the entry (rule 8 of the workspace: public pages only, employer and source only), started by the main session for every delegate under the entry and never for a chosen few; (4) a question to the delegation, which is the researcher's step. The evidence record keeps the step at which the search stopped (`stopped_at`) and why.
   - **Name in the original script (I6).** *Test rule, 0.14 draft.* Where a source gives the body's name in the script of the nominating country, it is stored beside the Roman-letter name (`name_native`) and both are used in searches. It is a search aid and decides no attribute (G3).
2. **Kind** (3.1).
3. **Legal form**, **commercial activity** and **represents commercial interests** (3.2).
4. **Hard case.** If the organisation matches a row of the table in section 4, that row decides business status. "None" where the kind is settled and no row fits; "unknown" where the evidence cannot show whether a row fits.
5. **Business status and type** (3.2).
6. **Sector** (3.3).
7. **State ownership** (3.4).
8. **Kind of fossil fuel link**, then each **tier flag** (section 5), after the same checks for every organisation (F10, section 5.6). Tiers do not depend on business status: a public body may meet a tier, and is then reported on its own line, outside the fossil fuel-linked share of business.
9. **Confidence** (6.3).

## 3. Attributes

### 3.1 Kind (rules K1–K5)

One kind per organisation. The body's own description may set the kind, at low confidence. A think tank is a body whose main activity is policy research published in its own name, not for members or clients. What a delegate does (adviser, support staff, guest) is a role, kept in a separate field, and is never a kind.

| Value | Rule | Covers | Looks similar, but is not |
|---|---|---|---|
| Public sector | K1 | ministries, agencies, parliaments, regional and local government, public development banks, chambers under public law | a company owned by the state (K2, with ownership recorded) |
| Business and commercial | K2 | companies, trade and industry associations, consultancies, law firms, financial institutions, cooperatives, municipal utilities | a foundation set up by a company (K3 unless it trades) |
| Civil society and other non-state | K3 | non-profit organisations, trade unions, universities and research bodies, think tanks, foundations that do not trade | an association whose members are mostly companies (K2) |
| Media | K4 | media organisations, for-profit or not | a company's communications department (its company's kind) |
| Other | K5 | bodies that fit none of the above, with the reason recorded | an entry that is not an organisation ("unknown", section 7) |

Basis: proposal 4.1 (decision 1).

### 3.2 Business

**Legal form** is stored as found, in the source's words (for example "GmbH", "association under the 1901 law"). It is a record, not a label.

**Commercial activity** (rule C1; yes, no, unknown). Yes where one of these holds, tried in this order; the first that is found decides, and a conflict with a lower one is recorded:

1. its legal form, by a register or its filings, is a for-profit one. A non-profit form (a gGmbH, or a company limited by guarantee with charitable status, for example) decides nothing by itself: tests 2 and 3 are then tried;
2. its statutes or membership page show an association whose members are companies;
3. an official register, or the body itself, describes it as a company, firm or bank. Self-description alone gives low confidence.

"No" needs a source that states the legal form or purpose (for example a register entry as a public body or a charity). The EU definition of an enterprise is the starting point for "company" (decision 26).

**Represents commercial interests** (rule C2; yes, no, not applicable, unknown), for every body that is not a company. Yes where it exists to speak for companies or an industry (decision 25). "No" needs a source that states its purpose, mandate or membership; its own description alone gives low confidence. Not applicable to a company acting for itself.

**Business status** (rule C3; business, not business, unknown) is derived, in this order (decision 19):

1. a public sector body (K1), media organisation, university, think tank, trade union or legislature is not business, whatever its legal form or commercial activity; so is a non-profit organisation or a foundation that does not trade (K3, commercial activity "no");
2. a hard case takes the status in its row (section 4); where the hard case is "unknown", so is business status;
3. otherwise business where the kind is "business and commercial" (K2) and commercial activity or represents commercial interests is "yes", or the kind is K3 or K5 and commercial activity is "yes"; not business where both are established as "no" or "not applicable"; unknown in every other case.

**Business type** (rule C4; company, trade or industry association, consultancy, law firm, financial institution, not a business, unknown) follows business status: "not a business" wherever the status is "not business", even for a body that trades (a for-profit broadcaster, for example). Among businesses: a financial institution's main activity is banking, insurance or investing others' money, venture capital included; a consultancy's is advice for a fee; a law firm's is legal services; a trade or industry association is a membership body of companies (B2 to B4); any other is a company. Where a body does two of these, the larger by its register entry or filings decides; where that is not documented, "unknown". State ownership is an attribute (3.4), not a type.

### 3.3 Sector

The structure is fixed: one primary sector and further sectors as tags (decision 31). The list of sectors is not: the proposal chooses it once the NACE classification has been read in full, and that source is not yet in the library (section 9). Until then:

- **Sector as found**: the organisation's main activity in the source's own words, with the source. A record, not a label.
- **Utility** (yes, no, unknown), rule S1: the body generates or supplies electricity, gas or heat to others. This is the only sector the tiers need, because the agreed list for tier 2 holds utilities only (question 2). "Yes" needs any such supply, however small. "No" needs a source of level A or B that gives a full description of the body's activities (5.4), none of it such supply. From 0.17, a founding law or a register's activity code alone leaves the strict label "unknown", reason "description partial", with "no" beside it under P1 (some evidence, medium at most); this replaces "a register's activity code or a founding law is enough" and ends the clash with 5.4. Whether a "no" also settles the tier 2 flags is in 5.2. A body that makes equipment for utilities, or sells to them, is not one.
- **Sector** label: "unknown" only.

### 3.4 State ownership (rules O1–O5)

| Value | Rule | Meaning |
|---|---|---|
| Majority state | O1 | a state holds a majority of the voting rights, directly or along a chain in which every link is a majority |
| Wider variant only | O2 | no majority, but a golden share or practical control (decision 3) |
| Not state-owned | O3 | the voting rights are documented, and no state holds a majority or control |
| Not applicable | O4 | the body is itself part of the state (kind K1), or has no owners (an association, a foundation, a university) |
| Unknown | O5 | ownership is not documented, or a link in the chain cannot be traced (reason "ownership chain incomplete") |

Holdings are not multiplied along a chain. Ownership is taken as at the date of the conference; a sale announced and not completed by then changes nothing, and where completion cannot be dated the value is "unknown". "State" includes regional and local government. State-owned bodies are reported as a group of their own (rule R1), apart from both public sector and business: code sets the reporting group from the labels, and the classifier does not fill it.

| Reporting group (R1) | Set by code where |
|---|---|
| Public sector | kind is public sector and state ownership is not "majority state" in a body with its own legal form outside the administration |
| State-owned enterprise or non-profit | state ownership is "majority state" and kind is not public sector (a state-owned company, or a state-owned non-profit such as a development or energy agency) |
| Business | kind is business and state ownership is not "majority state" |
| Civil society, media, other | kind is civil society, media or other, and state ownership is not "majority state" |
| Unknown | kind is unknown, or kind is business or civil society and state ownership is unknown |

Business status (3.2) is unchanged: a state-owned company is still business under B1, and the fossil fuel-linked share of business can be shown with and without this group.

## 4. Hard cases (rules B1–B19)

The lead researcher accepted these sides (question 1). Each case marked "own line" is counted on a line of its own, so that a total can be recalculated the other way; the alternatives are in proposal 4.2.

| Rule | Case | Business status | Also recorded |
|---|---|---|---|
| B1 | company: private, state-owned or mixed | business | ownership (3.4) |
| B2 | trade or industry association of companies | business | own line |
| B3 | association of companies and other bodies | business where statutes or membership show a majority of companies; not business where they show a minority; otherwise unknown | |
| B4 | chamber of commerce under private law | business | |
| B5 | chamber under public law, compulsory membership | not business | own line |
| B6 | cooperative | business | |
| B7 | public development bank | not business | own line; the owning state, in the notes |
| B8 | development agency that does not lend commercially | not business | one that a source shows lending commercially has no rule yet: "unknown", reason "not covered by the codebook" (section 9) |
| B9 | foundation set up by a company | not business, unless commercial activity (C1) is "yes" | the founder |
| B10 | municipal utility | business | public ownership |
| B11 | consultancy or law firm | business | own line |
| B12 | self-employed consultant | business where a register or business page shows trading; otherwise unknown | |
| B13 | trade union | not business | |
| B14 | parliament, one of its committees, or a political group or national delegation within it | not business; kind is public sector | |
| B15 | media company, including for-profit | not business | own line |
| B16 | university, public or private | not business | |
| B17 | think tank | not business | funders, where published |
| B18 | standing conference or coordination body of governments or ministers, with no legal form, whose members are all public bodies | not business; kind is public sector | the members, where published |
| B19 | public pension fund, sovereign wealth fund, or other body whose main business is investing others' money (from 0.17) | not business, unless it is a company; kind as for its owner | the owner; tier 3 treats it as a financial institution (section 9, step 0) |

Where an organisation has several roles, the role under which a register lists it decides, and the others are recorded in the notes. A mixed association with no published membership stays "unknown" under B3. Subsidiaries and holding companies: section 5.3.

## 5. Fossil fuel link (rules F1–F10, N1)

### 5.1 Kind of link

Recorded apart from the tiers, which express its strength (decision 27). One value; where several apply, the first in this order, with the others in the notes:

| Value | Rule | Belongs | Looks similar, but is not |
|---|---|---|---|
| Own operations | F1 | exploring for, extracting, refining, wholesale trading or transporting oil, gas or coal; petrochemicals; pipelines, terminals, storage | a maker of equipment used by such companies; a supplier of gas to end customers (F3) |
| Electricity from fossil fuels | F2 | a utility with gas, coal or oil-fired plants | a utility with renewable plants only |
| Other commercial dependence | F3 | a utility whose own operations depend on fossil fuels in another way, for example a gas supplier | a body in a sector not on the agreed list: this row is closed to it, and it is assessed under F1, F2, F5 and N1 as any other (its activity is kept in "sector as found") |
| Financing, insuring or owning | F4 | from 0.15, in use for the run rule in section 9: a bank among the twelve of the published table. Any other financial institution with no other link is "unknown" (reason "for review: on the bank table" or "not covered by the bank table"), never "none established" | |
| Representing fossil fuel interests | F5 | an association of one fossil fuel sector | an association across many sectors |
| None established | N1 | a full description of activities, none of them a link (5.4) | a search that found nothing ("unknown") |
| Unknown | | | |

### 5.2 Tier flags

Each flag is met, not met or unknown, and an organisation may meet several. Any current activity counts; past activity is recorded and does not set a flag (decision 21).

| Flag | Rule | Met where |
|---|---|---|
| Tier 1 | F6 | the tier 1 activities (F1) are the organisation's core business: its largest segment by revenue in its filings. Without filings, its main activity by its own account, at low confidence; its own account can give "met" only, never "not met" |
| Tier 1, any activity | F6 | it carries out any tier 1 activity, however small. The variant beside the headline |
| Tier 1 fuel | F6 | which fuels meet tier 1: oil, gas or petrochemicals; coal only; both. "Not applicable" where "tier 1, any activity" is not met; "unknown" where that flag is unknown or the fuel is not stated. Counts can then be shown with and without coal (decision 32) |
| Tier 2A | F7 | it is a utility (S1) and any of what it generates or supplies comes from fossil fuels |
| Tier 2B-O | F8 | it is in a sector on the agreed list, and a source of level A to C documents that its own operations depend on fossil fuels. The headline for 2B |
| Tier 2B-S | F8 | it is a utility (S1 is "yes") and that supply is its main activity by its register entry or filings (the proposal's "primary sector", 4.5), whether or not dependence is documented; "unknown" where the main activity is not documented. The wider variant |
| Tier 3 | | from 0.15: "met" for a bank among the twelve largest fossil fuel financiers of the published table; otherwise "unknown" with its reason and, for a bank on the table of 65, the scale of its financing (section 9, "Tier 3 run rule"). From 0.16: "not applicable" for a body that is not a financial institution (the brief defines tier 3 as banks, insurers and asset managers); "unknown", reason "description partial", where whether it is a financial institution is not settled |

The agreed list holds utilities only. A utility with renewable sources only, whose main activity is that supply, meets 2B-S and no other flag. Where utility is "no" on evidence that meets 5.4, tiers 2A, 2B-O and 2B-S are "not met", since they apply to utilities alone; where it is "no" on a register code or founding law only, they stay "unknown", reason "description partial" (section 9). Making equipment for, or selling services to, fossil fuel companies is not a tier 1 activity (F1). No percentage threshold applies.

Code, not the classifier, derives two further values: the highest tier met, and the headline tier, which is the first met in the order 1, 2A, 2B-O, 3 (a second version uses 2B-S in place of 2B-O; decision 35).

### 5.3 Particular organisations (F9)

- **Associations.** One that represents a single sector (its statutes or membership page show members in one sector) takes the flags its typical member would meet, at no more than medium confidence; this rule decides, though the association is not itself a utility under S1. One that spans several takes none: its flags and kind of link are "unknown", reason "not assessed by rule". All are reported on their own line (decisions 7 and 33).
- **Subsidiaries, joint ventures and holding companies** are classified on their own activity. Every parent found is recorded, and the parent's tier is run as a variant (decision 8). A parent's filing is evidence about the subsidiary only where it describes the subsidiary's own activity. A company's foundation (B9) is treated the same way, with the founder as parent.
- **Consultancies and law firms** are business with no tier, reported on their own line (decisions 9 and 34): every flag and the kind of link are "unknown", reason "not assessed by rule". A link that a source shows is recorded in the notes and is not counted under this version. They are never counted as shown to have no link.

### 5.4 "Not met" and "none established" (N1)

A negative is given only where both hold:

1. a source of level A or B gives a full description of the organisation's activities, and none of them meets the flag;
2. where that source is the organisation's own report, a source of level B or C that is independent of the organisation (decision 22) confirms it.

A partial description, publicity material or a climate pledge gives "unknown", reason "description partial". A register's activity code, a founding law or the type of body (a university, a broadcaster) is not by itself a full description under this version (section 9).

### 5.5 Beside the strict line: limited evidence and proxy (P1–P3)

*Test rule, 0.13 draft, for the Germany test (Ramsey's Germany-test instruction, decisions.md 2026-11-25; not proposal decision 44). From 0.16 in use for wave 1 too, on Ramsey's instruction; not approved by the lead researcher.* The classifier applies P1 to P3 wherever their conditions hold; they are not optional. Where the strict label is "unknown", the classifier may record an inferred value beside it, never in its place (rule 5 of the workspace). The strict label, its reason and its count do not change. Each inferred value names its basis, rule, confidence and source. No inferred value is given where identity is unresolved, except under rule I4 (section 2), where the list's own context points to one body.

| Rule | Basis | Gives | Ceiling |
|---|---|---|---|
| P1 | **limited evidence**: the law or government act that sets up a public body or fixes its remit, or a government register's activity code, where it leaves no room for a fossil fuel activity | "none established" for the kind of link; "not met" for tiers 1, 2A, 2B-O, 2B-S; utility "no". Never "tier 1, any activity", which a register code cannot show | medium |
| P2 | **proxy, type of body**: kind public sector set at high confidence, as a ministry, parliament, court, embassy, central bank or authority with commercial activity "no". Not for a public development bank, a chamber, a state-owned body, or a body whose own sources show it holds shares in companies; those stay unknown | as P1, citing the kind attribute | low |
| P3 | **proxy, own account**: the body's description of itself, or a field of interest it declares in a register, naming a fossil fuel activity or interest | the kind of link the account names, as a *possible* link | low |

Reporting keeps four lines for each attribute, and the fossil fuel question is reported by them. In plain words (from 0.16):

| Line | Plain words | Comes from |
|---|---|---|
| **Evidence** | a source settles it | the strict label, not "unknown" |
| **Some evidence, to be verified** | a law, decree or register code points one way | P1, medium at most |
| **By proxy** | only the type of body, or its own account, points one way | P2, P3, I4, low |
| **No evidence either way** | nothing points either way | "unknown" with no inferred value |

**Where each label comes from (from 0.17).** Every attribute is reported with a column naming the source its label rests on: the `source_type` and level of the stored evidence item it cites (a register or filing, a law, a government publication, a dataset, journalism, an encyclopaedia, the body's own description). A type of body that rests only on an encyclopaedia or the body's own description (level E) stays in the main tables, at low confidence, and the column shows it. Code, not the classifier, fills the column from the evidence record (`analysis.wave_review.label_basis`).

The same lines in the earlier wording are **definitive evidence**, **some evidence**, **by proxy**, and **no evidence either way**. Each of the first three is shown twice, for "fits a tier" and for "no link found". An inferred value is never added to the established count. A possible link (P3) is reported only as a count, and no organisation is named as fossil-linked on it (rule 7 of the workspace).

### 5.6 The same checks for every organisation (F10)

*Test rule, 0.14 draft.* For every organisation whose identity is settled, the finding step looks in the same five places and records for each one of: found, not found, not reached, not applicable. It is never applied to a chosen subset.

1. the organisation's own site: what it says it does;
2. the company register or, for a public body, the government register or founding act;
3. the latest annual report or filings: segments and activities;
4. ownership: parents and, for a state-owned body, the owner;
5. for a financial institution, the published tables of fossil fuel financing held in the library (section 9).

"Not found" in all five is still "unknown", never a negative (5.4). The record of the five shows whether an "unknown" means "looked everywhere" or "could not look".

## 6. Evidence and confidence

### 6.1 Levels of evidence

| Level | In the script | Sources | Used for |
|---|---|---|---|
| A | 1 | the organisation's official filings and annual reports; government registers, lobby and transparency registers included; the law that sets up a public body | identity, legal form, ownership, activities |
| B | 2 | filings with regulators; government publications; established industry databases, the global legal entity identifier (LEI) record included | independent confirmation |
| C | 3 | established research organisations; specialist datasets | sector and fossil fuel exposure |
| D | 4 | journalism from established outlets | support and context only; decides no label |
| E | 5 | the organisation's description of itself; general web pages; encyclopaedias; sites that copy register data | first identification; weak for anything else |

For a claim an organisation has reason to understate, a level B or C source ranks above its own account. Whether a source is independent of the organisation is recorded apart from its level (decision 22). A document the organisation wrote is its own account wherever it is filed, and is never the independent source 5.4 asks for. A news item copied from a press release counts as the press release. What a body declares about itself in a register (its fields of interest in a lobby register, for example) is level A for the fact that it is registered and its legal form, and level E for the rest.

**What is not evidence (E1).** An address block, an imprint, a page footer, navigation, a logo or its alternative text, and a list of funders' logos show that a name appears on a page. They are evidence of no activity, no relationship and no label. **A mandate is partial (E2).** A statement of a body's mission or remit, wherever published, is a partial description of its activities: it can set the kind, and it cannot by itself give a negative or a "no" above low confidence on the strict line.

### 6.2 Status of the evidence

The finding step gives each organisation's evidence one status:

| Status | Meaning |
|---|---|
| Confident | the organisation is identified beyond doubt, and at least one item states what it is |
| Uncertain | evidence was found, but the match to the name is in doubt or sources disagree |
| Abstained | the search ran and could not settle it |
| Confirmed negative | a source meeting 5.4 was found |
| Failed | the search or a page could not be completed |

### 6.3 Confidence

Each attribute's label carries its own confidence, set from the item cited for it. An "unknown" label carries a reason and no confidence. For the kind of link, confidence is recorded for three claims (rule Q1): that the organisation is the one meant (identity), that it does what the label says (activity), and that this meets the rule (rule); the overall confidence is the lowest of the three (decision 36). Identity confidence is high where the evidence status is confident, medium where it is uncertain, and low where the match rests on the name alone; the level of the source does not lower it. Activity and rule confidence are "not applicable" where the kind of link is "unknown", and identity confidence where the identity is unresolved. Code sets confidence from the level and status of the evidence cited:

| Level of the item cited | Evidence confident or confirmed negative | Evidence uncertain |
|---|---|---|
| A or B | high | medium |
| C | medium | low |
| D or E | low (a negative cannot rest on these levels) | low |

Where the evidence status is abstained, an attribute still settled from a cited item takes the "uncertain" column; where it is failed, every attribute is "unknown", reason "lookup failed".

The classified record then takes one status, which describes the kind of link only; the other attributes may be settled when it is "abstained", and the review sheet shows each with its own confidence. The status is **confident** where the overall confidence of the kind of link is high; **uncertain** where it is medium or low; **abstained** where the kind of link is "unknown" for any reason other than a failed look-up; **failed** where the look-up failed; **confirmed negative** where the kind of link is "none established", whatever its confidence.

## 7. "Unknown" and its reasons

Every "unknown" carries one of twelve reasons, in four classes, recorded for each attribute (rule U1). From 0.15 tier 3 adds two more, both of class "not assessed": "for review: on the bank table" and "not covered by the bank table" (section 9). "Not applicable" is a label, not an unknown, and carries no reason.

| Class | Reason | Example |
|---|---|---|
| Identity unresolved | field blank | no organisation given |
| | generic text | "Private sector" |
| | not an organisation | a role, or a description of a person |
| | could be several entities | an acronym used by several bodies |
| Evidence insufficient | nothing found | the recorded searches found no source that states the deciding fact |
| | description partial | a source describes some of the activities, short of what 5.4 asks |
| | ownership chain incomplete | a parent is named, and a link above it cannot be traced (O5) |
| | sources conflict | sources disagree, and the order of evidence (6.1) does not settle it |
| | not covered by the codebook | no rule fits the case |
| Not assessed | not yet defined | sector, for every organisation (section 9). Tier 3 until 0.14; from 0.15 see the run rule in section 9 |
| | not assessed by rule | the flags and kind of link of a consultancy, a law firm or a cross-sector association (5.3) |
| Technical | lookup failed | a search was refused, or a page did not load |

Technical unknowns are run again before any count and reported apart. An unknown of the second or third class is not evidence of absence.

## 8. Where the codebook and the script differ

The classification script reads the labels block in section 10. It does not yet do everything above, and each gap is closed, or its effect measured on the fixed test set, before the pilot (item 4 is closed, not measured):

1. **One evidence item per record.** The codebook asks for the item behind each attribute.
2. **One "unknown" reason per record**, for the kind of link only.
3. **Overall confidence** is set from one cited item, not as the lowest of three claims.
4. **Negatives.** Rule 5.4 is enforced for "none established" only, not for each "not met", and its second condition is not checked by code. Before the pilot, code turns any negative without evidence that meets 5.4 into "unknown". The finding step's "confirmed negative" counts only once code has confirmed it.
5. **Derived values.** Business status, highest tier and headline tier are not yet derived by code; the classifier fills business status by rule C3. The record status "confirmed negative" is likewise not yet set by code.
6. **Worked examples** with real organisations come from the fixed test set, once the expert has labelled it. The examples here are generic.
7. **Fields not yet in the labels block:** each attribute's own reason and confidence, legal form, sector as found, the delegate's role, and parents. Until added they are kept in the record's notes.

## 9. What this version leaves open

**Cannot be decided yet.** Each stays "unknown" for every organisation until settled:

| Item | Waits for | Effect |
|---|---|---|
| Tier 3 and link kind F4 | the lead researcher's written definition, from the COP30 criteria if they can be supplied (question 3) | no bank, insurer or asset manager can be counted as fossil fuel-linked |
| Sector label | NACE read in full, then the choice in proposal 4.3 (decision 2) | sectors cannot be tabulated; "sector as found" is kept so no new search is needed |

**Draft for tier 3, not in use (2026-11-25).** Offered for her decision, taken from a methodology drafted independently from the brief. Tier 3A: a bank, insurer, asset manager or public development bank whose financing, insuring or holding of tier 1 activity is documented, for that organisation, by a source of level A to C. Tier 3B: a wider or less direct financial exposure, for example a holding in a fund or a parent with such a link. Being a financial institution is not enough for either. Open points: a minimum amount or share (recommendation below: none, show the scale), the period counted, and whether a public development bank's mandate places it here or in the public sector. Until she decides, tier 3 stays "unknown".

**A test of the draft on one published table (0.14).** The library holds the sector tables of *Banking on Climate Chaos 2026* (`bankingonclimatechaos-sector-tables-2026`, level C): financing by the 65 largest banks to companies expanding oil and gas, by sector, 2021 to 2025 (upstream page 2, midstream page 5, gas power page 8). Code, not the classifier, compares each organisation classified as a financial institution with the bank names in that table. A bank named there would meet draft tier 3A; it is shown on its own line marked "draft, not approved" and is added to no tier count. A financial institution not named there stays "unknown": the table covers 65 banks only, and no insurer or asset manager, so absence from it shows nothing. The strict label for tier 3 does not change.

**Recommended for the amount: show the scale, set no cut-off (Ramsey's instruction of 2026-11-25, for her decision; not approved).** The table has no threshold of its own: banks are in it because they are the 65 largest by assets, not because of how much they finance, and the methodology we hold (`bankingonclimatechaos-methodology-2026`, pages 2, 5 and 8) names no amount or share above which a bank counts as a fossil fuel financier. Each deal is already scaled to the financed company's fossil fuel business; the bank's fossil share of all its financing cannot be worked out from the table. Any cut-off would therefore be ours. So a bank named in the table is not sorted into "linked" or "not linked" by amount. Beside its name the output gives: its 2021 to 2025 total in each sector, the three added together, its rank among the 65 on that sum, and the quarter of the table it falls in (`cleaning.sample_references`, columns `usd_bn_2021_2025_three_sectors`, `bank_rank_in_table`, `bank_quarter_of_table`). The nine banks found among the EU party badges range from USD 1.2bn to 158.7bn (`data/processed/sample_references_stats.json`; provisional, not checked). Checked on 2026-11-25 (record: `docs/archived/reviews/bank-unit-checks-2026-11-25.md`). The report's executive summary (`bankingonclimatechaos-executive-summary-2026`, p.6) names one group of banks, the "Dirty Dozen": the twelve largest financiers of all fossil fuels from 2021 to 2025. It is a ranking with no amount to reach, so it is shown as the report gives it (column `in_report_top_12_2021_2025`) and is not a threshold of ours. Two of the nine banks are in it: JPMorgan Chase, and SMBC Group, which is in the sample only through an aircraft leasing unit. Limits: (a) the three sector tables overlap (over all 65 banks they add up to USD 2,611.2bn, more than the report's "$2.1 trillion" for all expansion financing, p.5), so the sum orders banks and must not be quoted as a bank's total; (b) the rank compares a bank only with the other 64, and by the summary (p.3 and p.7) these 65 provide about 74% of 2025 financing among almost 2,000 banks, so a low rank is low among the largest financiers; (c) the full report could not be read, so a further grouping cannot be ruled out; (d) five of the twelve matched organisations are a unit or possible relative of a bank: for the three asset managers the legal entity identifier (LEI) register, level B, names the bank as parent of the company we take the badge to mean; the business division and the leasing unit rest on own descriptions only (uncertain); and the bank's figures do not cover asset management or leasing, so whether a unit is shown with its parent's figures is her decision. Considered and not recommended, all after the figures were seen (rule 9): any amount above zero, a floor of about USD 1bn, a cut at a percentile.

**Tier 3 run rule (0.15; Ramsey's instruction of 2026-11-25, for the lead researcher to confirm or redefine after she has seen the batches).** It replaces "unknown only" above and uses the table test already described.

0. **Not a financial institution** (from 0.16; scope widened in 0.17). Tier 3 applies to banks, insurers and asset managers, and to any body whose main business is banking, insurance or investing others' money: public development banks (B7), public pension funds and sovereign wealth funds (B19). It is "not applicable" for any other body whose business type is settled as anything other than "financial institution". The brief (line 39) names banks, insurers and asset managers; the wider scope is Ramsey's instruction of 2026-11-25, for the lead researcher to confirm. A central bank is not included. It is counted apart, not as an unknown. Where it is not settled whether the body is a financial institution, tier 3 is "unknown", reason "description partial". Code, not the classifier, applies this step from the business type and kind (`analysis.tier3_draft.tier3_run`), so the line is the same for every record.
1. **Met.** The organisation is one of the twelve banks the report names as the largest financiers of all fossil fuels, 2021 to 2025 (`bankingonclimatechaos-executive-summary-2026`, p.6, level C; table `bankingonclimatechaos-top12-2026.csv`). Code makes the match on the name; a person confirms it is the same legal entity before it is counted. Link kind F4, confidence as for level C.
2. **For review, scale shown.** A bank on the table of 65 but outside the twelve stays "unknown" on tier 3, reason "for review: on the bank table". Its 2021 to 2025 amounts by sector, their sum, its rank among the 65 and its quarter of the table are shown beside it, as for the twelve. No amount decides a label: the researcher reads the scale and may move the line.
3. **Not covered.** A financial institution not on the table stays "unknown", reason "not covered by the bank table": the table holds 65 banks and no insurer or asset manager, so absence from it shows nothing.
4. **A unit of a bank** (an asset manager, a leasing unit, a division) is shown with its parent's figures, marked "parent's figures", and is not counted as met until the lead researcher decides whether a unit takes its parent's place.

Tier 3 "not met" is not given by this rule. Counts of tier 3 are reported twice: the twelve only, and every bank on the table, so the effect of the line is visible. Names stay as case codes until each is signed off.

**The strictness of a negative.** Under 5.4 as written, none of the 20 test organisations could be given "no link", including a state weather service, two universities and a photography firm, because no full description of activities was found for any of them. The alternative is to accept a register's activity code, a founding law, or the type of body as enough for "none established" where it leaves no room for a fossil fuel activity. The same choice decides whether a body shown by a register code not to be a utility is "not met" on tier 2 (5.2). This version keeps the strict rule. **Recommended:** accept the law that sets up a public body, or a government register's activity code, where it leaves no room for a fossil fuel activity, at medium confidence and on a line of its own ("no link, on limited evidence"); the type of body alone stays "unknown". A register code records the main activity only, so "tier 1, any activity" would stay "unknown". This changes proposal 4.6 and needs her approval of that point, before the fixed test set.

If tier 3 has no approved definition when the pilot is due, the pilot waits, unless she chooses to run it with tier 3 "unknown".

**Choices for the lead researcher to confirm.** The first four are the proposal's recommended values; the rest are readings made in writing this codebook. All are needed before approval of the codebook.

| Choice | Value here | Alternative | Moves |
|---|---|---|---|
| Coal (5.2) | counts in tier 1, with its own fuel field | left out | tier 1 count |
| Subsidiaries (5.3) | own activity; parent's tier as a variant | parent's tier | tier counts |
| Tier 1 headline (5.2) | core business | any activity | tier 1 count |
| Order of evidence (6.1) | as in the proposal | | confidence |
| Consultancies, law firms, cross-sector associations (5.3) | business; link "unknown, not assessed"; a link a source shows is noted, not counted | assess them like any body | linked share of business |
| Single-sector association (5.3) | its typical member's flags, at most medium confidence | no flags | tier counts |
| Gas supply to end customers (5.1) | "other commercial dependence" | tier 1 trading | tier 1 count |
| Tier 2B-S (5.2) | supply is the main activity | any supply | wider variant of 2B |
| Non-profits (3.2) | not business unless they trade; a non-profit legal form decides nothing by itself | business where registered as a company | business total |
| Think tank; kind from own description (3.1) | defined in 3.1; allowed at low confidence | needs an outside source | business total |
| Development agency that lends commercially (B8) | "unknown": no rule | business, or not business | business total |
| Chambers under public law, public development banks (3.1) | kind "public sector" | business and commercial | business total |
| Universities, think tanks (3.1) | civil society, whoever funds them | public sector where state-funded | kinds |
| "State" (3.4) | includes regional and local government | national only | state-owned line |
| Group or national delegation in a parliament (B14) | treated as the parliament | a body of its own | kinds |
| Unit with no legal form; shared brand (section 2) | host body's labels; matching registered name, else a person | "unknown" | unknown share |
| Company foundation (5.3) | own activity; founder's tier as a variant | founder's tier | tier counts |
| Lobby register entry (6.1) | level A for legal form only | level A throughout | confidence |
| Reasons for "unknown" (section 7) | twelve in four classes | the proposal's eight in three (4.6) | how unknowns are reported |

Not a codebook rule, and still open before the report: whether the EU's own delegation is reported with the Member States (decision 10).

## 10. Labels for the script

```json
{
  "version": "0.17",
  "label_field": "fossil_link_kind",
  "fields": {
    "kind": ["public_sector", "business_and_commercial", "civil_society_and_other_non_state", "media", "other", "unknown"],
    "commercial_activity": ["yes", "no", "unknown"],
    "represents_commercial_interests": ["yes", "no", "not_applicable", "unknown"],
    "hard_case": ["none", "company", "trade_association", "mixed_association", "private_law_chamber", "public_law_chamber", "cooperative", "public_development_bank", "development_agency", "company_foundation", "municipal_utility", "consultancy_or_law_firm", "self_employed_consultant", "trade_union", "parliament", "media_company", "university", "think_tank", "coordination_body", "public_investment_fund", "unknown"],
    "business_status": ["business", "not_business", "unknown"],
    "business_type": ["company", "trade_or_industry_association", "consultancy", "law_firm", "financial_institution", "not_business", "unknown"],
    "utility": ["yes", "no", "unknown"],
    "sector": ["unknown"],
    "state_ownership": ["majority_state", "wider_variant_only", "not_state_owned", "not_applicable", "unknown"],
    "fossil_link_kind": ["own_operations", "fossil_electricity", "other_commercial_dependence", "financing_insuring_owning", "representing_fossil_interests", "none_established", "unknown"],
    "tier_1": ["met", "not_met", "unknown"],
    "tier_1_any_activity": ["met", "not_met", "unknown"],
    "tier_1_fuel": ["oil_gas_petrochemicals", "coal_only", "both", "not_applicable", "unknown"],
    "tier_2A": ["met", "not_met", "unknown"],
    "tier_2B_O": ["met", "not_met", "unknown"],
    "tier_2B_S": ["met", "not_met", "unknown"],
    "tier_3": ["met", "not_applicable", "unknown"],
    "unknown_class": ["identity_unresolved", "evidence_insufficient", "not_assessed", "technical", "none"],
    "identity_confidence": ["high", "medium", "low", "not_applicable"],
    "activity_confidence": ["high", "medium", "low", "not_applicable"],
    "rule_confidence": ["high", "medium", "low", "not_applicable"]
  },
  "rules": ["G1", "G2", "G3", "I1", "I2", "I3", "I4", "I5", "I6", "K1", "K2", "K3", "K4", "K5", "C1", "C2", "C3", "C4", "S1", "B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8", "B9", "B10", "B11", "B12", "B13", "B14", "B15", "B16", "B17", "B18", "B19", "O1", "O2", "O3", "O4", "O5", "R1", "F1", "F2", "F3", "F4", "F5", "F6", "F7", "F8", "F9", "F10", "N1", "P1", "P2", "P3", "Q1", "E1", "E2", "U1"],
  "negative_labels": ["none_established"],
  "confidence_by_level": {
    "1": {"confident": "high", "uncertain": "medium", "abstained": "medium", "confirmed negative": "high"},
    "2": {"confident": "high", "uncertain": "medium", "abstained": "medium", "confirmed negative": "high"},
    "3": {"confident": "medium", "uncertain": "low", "abstained": "low", "confirmed negative": "medium"},
    "4": {"confident": "low", "uncertain": "low", "abstained": "low"},
    "5": {"confident": "low", "uncertain": "low", "abstained": "low"}
  },
  "status_by_confidence": {"high": "confident", "medium": "uncertain", "low": "uncertain"},
  "unknown_reasons": ["field blank", "generic text", "not an organisation", "could be several entities", "nothing found", "description partial", "ownership chain incomplete", "sources conflict", "not covered by the codebook", "not yet defined", "not assessed by rule", "lookup failed", "for review: on the bank table", "not covered by the bank table"],
  "inference_bases": {
    "limited_evidence": "medium",
    "proxy": "low"
  }
}
```

## Change log

| Version | Date | Change |
|---|---|---|
| 0.1 | 2026-11-24 | First draft, from proposal v4 section 4, before approval. Client Claude Code, model Claude Opus 5.5. |
| 0.9 | 2026-11-25 | Rewritten from the approved proposal v7. Title corrected to COP31. Added: rules G1 to G3 (G2 from the lead researcher's comment); legal form; the derivation of business status; hard cases B15 to B17; the utility attribute S1; tier 1 by core business with an "any activity" variant and a fuel field in place of the coal flag; tier 2B-S in use; the second condition for a negative; the "technical" class of unknown; the status of a classified record. Removed: tier 2B-M and the hard-case alternatives column (accepted under question 1). Client Claude Code, model Claude Fable 5.2. |
| 0.10 | 2026-11-25 | After the test on 20 organisations (`data/processed/draft-codebook/codebook-test/`; evidence by `evidence-finder`, labels by `org-classifier`, both Claude Sonnet; 120 notes of unclear rules). No label was changed by hand; the rules were. Added: rule numbers I1, C1 to C4, O4, Q1, U1; the identity rules for brands, units and shared names; "none" against "unknown" for the hard case; public bodies as not business; the definitions of business type; the standard for utility "no" and its effect on tier 2; ownership during a sale; four reasons for unknown and the class "not assessed"; confidence for each attribute, and identity confidence apart from the level of the source; where lobby registers, LEI records, laws and encyclopaedias sit in the order of evidence. Opened for the lead researcher: how strict a negative must be (section 9). Client Claude Code, model Claude Fable 5.2. |
| 0.11 | 2026-11-25 | After the independent check of 0.10 (methods review, Claude Opus; citation check, Claude Sonnet). Corrected: an unmatched brand goes to a person; non-profits that do not trade are not business; tier 2B-S follows the utility attribute; consultancies and law firms are "unknown, not assessed by rule" on every flag; a financial institution cannot be "none established" before tier 3 is defined; gas supply to end customers is F3; utility "no" on a register code no longer sets tier 2 to "not met"; ownership rules renumbered O1 to O5; definitions added; the labels block aligned. The proposal (4.6) gives eight reasons for unknown in three classes; this codebook has twelve in four, a change for the lead researcher to confirm with it. Client Claude Code, model Claude Fable 5.2. |
| 0.12 | 2026-11-25 | After the methods review of 0.11 (Claude Opus; 12 findings and what was done, in the review record). Changes: cross-sector associations and consultancies are "unknown, not assessed by rule"; tier 2B-S needs supply as the main activity (proposal 4.5); business status for K3 and K5 bodies and unknown hard cases; a body's own account cannot give "not met", and the second source for a negative must be independent; confidence where evidence is abstained; section 9 as a table, with a recommendation on negatives. Not checked again. Client Claude Code, model Claude Fable 5.2. |
| 0.13 | 2026-11-25 | Draft for the Germany test (`data/processed/draft-codebook/germany-test/`), after its citation check. Added: "i.A." (I2) and acronyms (I3); coordination bodies with no legal form (B18); what is not evidence (E1) and a mandate as partial (E2); inferred values beside the strict label, on limited evidence (P1, the option recommended in section 9) or proxy (P2, P3), as a test rule (5.5); a reporting group for state-owned bodies, set by code (R1), in place of reporting them inside business. User decisions of 2026-11-25 (decision 44), not yet confirmed by the lead researcher. Client Claude Code, model Claude Opus 5.5. |
| 0.14 | 2026-11-25 | Draft for the country tests, after the comparison of three delegations showed where nothing could be said. Added, all as test rules on Ramsey's instruction of 2026-11-25 (`decisions.md`), none approved: the list's own context as supporting evidence of which body an entry means, beside the strict line and at low confidence (I4; G1 and 5.5 amended to allow it); one order of search with the stopping point recorded (I5); the name in the original script (I6); the same five checks for the fossil question for every organisation (F10, 5.6); the four reporting lines named by strength of evidence (5.5); a test of the tier 3 draft against one published table, by code (section 9). No label list changed; tier 3 stays "unknown". Not checked by a methods review. Client Claude Code, model Claude Fable 5.2. |
| 0.14, section 9 amended | 2026-11-25 | Recommendation added on the amount for tier 3: no cut-off, the scale of each bank's financing shown beside its name (Ramsey's instruction, `decisions.md`; for the lead researcher's decision). Written after the table's figures were seen. No rule, label or version number changed, so records made under 0.14 stay valid. Not checked. Client Claude Code, model Claude Fable 5.2. |
| 0.14, section 9 amended again | 2026-11-25 | Limits of that recommendation checked and rewritten: the report's one named group of banks (a top-twelve ranking, no threshold) added as a column; the three-sector sum shown to overlap and not to be read as a total; the rank placed in the wider set of banks; the five unit matches looked up, all uncertain. Full report not read. No rule, label or version number changed. Not checked. Client Claude Code, model Claude Fable 5.2. |
| 0.15 | 2026-11-25 | Tier 3 put in use as a run rule for the first batches (wave 1 and France), on Ramsey's instruction (`decisions.md`): met for the twelve largest fossil fuel financiers of the published table; the scale shown for every bank on the table of 65; all other financial institutions stay unknown. No other rule changed. Not checked by `/check-work`; the lead researcher's approval of this version is not on record. |
| 0.16 | 2026-11-25 | After batch 1 of wave 1 (10 organisations; 7 records flagged by the code check), on Ramsey's instruction (`decisions.md`, "Wave 1 setup fixed after batch 1"), for the lead researcher to confirm. Labels block corrected to match the text of 0.15: link kind F4 (`financing_insuring_owning`) and rule F4 added; tier 3 takes "met", "not applicable" and "unknown"; the two tier 3 reasons added. Tier 3 "not applicable" for bodies that are not financial institutions (brief, line 39; section 9, step 0). Rules P1 to P3 put in use for wave 1, with the four reporting lines in plain words (5.5). Written after batch 1's results were seen (rule 9); batch 1 is run again under 0.16 and its first run kept apart. Client Claude Code, model Claude Opus 5.5. |
| 0.17 | 2026-11-25 | After the wave 1 review, on Ramsey's instruction (`decisions.md`, "Wave 1 review answered"), for the lead researcher to confirm. A founding law or register code alone no longer settles utility "no": the strict label stays unknown with "no" beside it under P1 (S1). Every label is reported with the source it rests on (5.5). Tier 3 covers public development banks, public pension funds and sovereign wealth funds (B19; section 9, step 0). Written after wave 1's results were seen (rule 9); wave 1 is classified again under 0.17 from its stored evidence and the 0.16 run kept apart. Client Claude Code, model Claude Opus 5.5. |
