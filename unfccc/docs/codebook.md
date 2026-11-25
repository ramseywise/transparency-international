# Codebook: organisations on the EU and Member State delegations to COP31

**Version:** 0.12, 2026-11-25. The candidate for version 1.0.
**Status:** a draft that waits for the lead researcher's answers to the choices in section 9; the version that follows them goes to her for approval. It binds nothing until she approves it; the number becomes 1.0 on approval, and the classification script refuses any version below 1.0.
**Source:** research proposal v7, sections 4, 6 and 8 (`docs/research-proposal.md`), approved 2026-11-25 with questions 1 to 4 answered as recommended (`decisions.md`, "Research proposal approved"). It does not draw on the feasibility test's results. Decision numbers are the tags in the proposal's text; the study has no separate numbered register yet.
**Tested:** on 20 awkward organisations from the data (2026-11-25), drawn apart from the 20 of the feasibility test and kept out of the pilot and the fixed test set; the rules that gave no single answer were rewritten (change log). The test's labels are provisional and are not findings.
**Checked:** versions 0.10 and 0.11, on 2026-11-25, by methods reviews (Claude Opus) and, for 0.10, a citation check (Claude Sonnet); the record is `docs/archived/reviews/codebook-v0.10-review-2026-11-25.md`. This version answers the second review and has not itself been checked. No numbers check: the codebook reports no results.

## 1. What this codebook does

It sets out how each organisation on the delegation lists is described: what kind of body it is, whether it is a business, who owns it, and whether and how it is linked to fossil fuels. Each is a separate attribute. No label carries two of them.

Every attribute has three possible outcomes: a positive value, a negative value, and "unknown" with a reason. A search that finds nothing gives "unknown", never a negative.

Three general rules hold throughout:

- **G1. Organisation level.** The organisation is classified, never the person. A delegate's title, department and relation to the delegation are not used.
- **G2. Where a delegate is registered is not evidence.** The delegation, the badge type (party or overflow), and whether a body attends inside a delegation or as an observer say nothing about its ownership, its business status or a fossil fuel link (lead researcher's comment, 2026-11-25: such bodies can sit anywhere).
- **G3. The name is not evidence.** A name may guide a search. It decides no attribute.

Section 9 lists what this version cannot yet decide, and the choices carried at the proposal's recommended value for the lead researcher to confirm.

## 2. Order of decisions

For each organisation, in this order:

1. **Identity** (rule I1). Is the entry an organisation, and which one? If not settled, every attribute is "unknown", class "identity unresolved" (section 7): "generic text" where the entry names no particular body, "could be several entities" where it names one and more than one body bears that name. The nominating country may guide a search and decides nothing. Where a brand covers several related legal entities, the one whose registered name matches the entry is taken; where none matches, "could be several entities", for a person to settle (proposal 6.1). A unit, programme or initiative with no legal form of its own is classified as the body that hosts it, where a source names the host; otherwise "not an organisation". The exception is a municipal utility run inside a local authority: rule B10 applies and its kind is K2, with the host recorded. The proposal (6.1) foresees nine identity rules; those for branches, mergers, joint ventures and a body named in two delegations are not yet written, and such a case is "unknown", reason "not covered by the codebook".
2. **Kind** (3.1).
3. **Legal form**, **commercial activity** and **represents commercial interests** (3.2).
4. **Hard case.** If the organisation matches a row of the table in section 4, that row decides business status. "None" where the kind is settled and no row fits; "unknown" where the evidence cannot show whether a row fits.
5. **Business status and type** (3.2).
6. **Sector** (3.3).
7. **State ownership** (3.4).
8. **Kind of fossil fuel link**, then each **tier flag** (section 5). Tiers do not depend on business status: a public body may meet a tier, and is then reported on its own line, outside the fossil fuel-linked share of business.
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
- **Utility** (yes, no, unknown), rule S1: the body generates or supplies electricity, gas or heat to others. This is the only sector the tiers need, because the agreed list for tier 2 holds utilities only (question 2). "Yes" needs any such supply, however small. "No" needs a source of level A or B that states the body's activity (a register's activity code or a founding law is enough), and none of it is such supply; whether that also settles the tier 2 flags is in 5.2. A body that makes equipment for utilities, or sells to them, is not one.
- **Sector** label: "unknown" only.

### 3.4 State ownership (rules O1–O5)

| Value | Rule | Meaning |
|---|---|---|
| Majority state | O1 | a state holds a majority of the voting rights, directly or along a chain in which every link is a majority |
| Wider variant only | O2 | no majority, but a golden share or practical control (decision 3) |
| Not state-owned | O3 | the voting rights are documented, and no state holds a majority or control |
| Not applicable | O4 | the body is itself part of the state (kind K1), or has no owners (an association, a foundation, a university) |
| Unknown | O5 | ownership is not documented, or a link in the chain cannot be traced (reason "ownership chain incomplete") |

Holdings are not multiplied along a chain. Ownership is taken as at the date of the conference; a sale announced and not completed by then changes nothing, and where completion cannot be dated the value is "unknown". "State" includes regional and local government. State-owned enterprises stay in the business totals and are also reported on their own line.

## 4. Hard cases (rules B1–B17)

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

Where an organisation has several roles, the role under which a register lists it decides, and the others are recorded in the notes. A mixed association with no published membership stays "unknown" under B3. Subsidiaries and holding companies: section 5.3.

## 5. Fossil fuel link (rules F1–F9, N1)

### 5.1 Kind of link

Recorded apart from the tiers, which express its strength (decision 27). One value; where several apply, the first in this order, with the others in the notes:

| Value | Rule | Belongs | Looks similar, but is not |
|---|---|---|---|
| Own operations | F1 | exploring for, extracting, refining, wholesale trading or transporting oil, gas or coal; petrochemicals; pipelines, terminals, storage | a maker of equipment used by such companies; a supplier of gas to end customers (F3) |
| Electricity from fossil fuels | F2 | a utility with gas, coal or oil-fired plants | a utility with renewable plants only |
| Other commercial dependence | F3 | a utility whose own operations depend on fossil fuels in another way, for example a gas supplier | a body in a sector not on the agreed list: this row is closed to it, and it is assessed under F1, F2, F5 and N1 as any other (its activity is kept in "sector as found") |
| Financing, insuring or owning | F4 | not in use until tier 3 is defined (section 9). Until then a financial institution with no other link is "unknown", reason "not yet defined", never "none established" | |
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
| Tier 3 | | "unknown" only, until a written definition is approved (section 9) |

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

Every "unknown" carries one of twelve reasons, in four classes, recorded for each attribute (rule U1).

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
| Not assessed | not yet defined | sector and tier 3, for every organisation (section 9) |
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
  "version": "0.12",
  "label_field": "fossil_link_kind",
  "fields": {
    "kind": ["public_sector", "business_and_commercial", "civil_society_and_other_non_state", "media", "other", "unknown"],
    "commercial_activity": ["yes", "no", "unknown"],
    "represents_commercial_interests": ["yes", "no", "not_applicable", "unknown"],
    "hard_case": ["none", "company", "trade_association", "mixed_association", "private_law_chamber", "public_law_chamber", "cooperative", "public_development_bank", "development_agency", "company_foundation", "municipal_utility", "consultancy_or_law_firm", "self_employed_consultant", "trade_union", "parliament", "media_company", "university", "think_tank", "unknown"],
    "business_status": ["business", "not_business", "unknown"],
    "business_type": ["company", "trade_or_industry_association", "consultancy", "law_firm", "financial_institution", "not_business", "unknown"],
    "utility": ["yes", "no", "unknown"],
    "sector": ["unknown"],
    "state_ownership": ["majority_state", "wider_variant_only", "not_state_owned", "not_applicable", "unknown"],
    "fossil_link_kind": ["own_operations", "fossil_electricity", "other_commercial_dependence", "representing_fossil_interests", "none_established", "unknown"],
    "tier_1": ["met", "not_met", "unknown"],
    "tier_1_any_activity": ["met", "not_met", "unknown"],
    "tier_1_fuel": ["oil_gas_petrochemicals", "coal_only", "both", "not_applicable", "unknown"],
    "tier_2A": ["met", "not_met", "unknown"],
    "tier_2B_O": ["met", "not_met", "unknown"],
    "tier_2B_S": ["met", "not_met", "unknown"],
    "tier_3": ["unknown"],
    "unknown_class": ["identity_unresolved", "evidence_insufficient", "not_assessed", "technical", "none"],
    "identity_confidence": ["high", "medium", "low", "not_applicable"],
    "activity_confidence": ["high", "medium", "low", "not_applicable"],
    "rule_confidence": ["high", "medium", "low", "not_applicable"]
  },
  "rules": ["G1", "G2", "G3", "I1", "K1", "K2", "K3", "K4", "K5", "C1", "C2", "C3", "C4", "S1", "B1", "B2", "B3", "B4", "B5", "B6", "B7", "B8", "B9", "B10", "B11", "B12", "B13", "B14", "B15", "B16", "B17", "O1", "O2", "O3", "O4", "O5", "F1", "F2", "F3", "F5", "F6", "F7", "F8", "F9", "N1", "Q1", "U1"],
  "negative_labels": ["none_established"],
  "confidence_by_level": {
    "1": {"confident": "high", "uncertain": "medium", "abstained": "medium", "confirmed negative": "high"},
    "2": {"confident": "high", "uncertain": "medium", "abstained": "medium", "confirmed negative": "high"},
    "3": {"confident": "medium", "uncertain": "low", "abstained": "low", "confirmed negative": "medium"},
    "4": {"confident": "low", "uncertain": "low", "abstained": "low"},
    "5": {"confident": "low", "uncertain": "low", "abstained": "low"}
  },
  "status_by_confidence": {"high": "confident", "medium": "uncertain", "low": "uncertain"},
  "unknown_reasons": ["field blank", "generic text", "not an organisation", "could be several entities", "nothing found", "description partial", "ownership chain incomplete", "sources conflict", "not covered by the codebook", "not yet defined", "not assessed by rule", "lookup failed"]
}
```

## Change log

| Version | Date | Change |
|---|---|---|
| 0.1 | 2026-11-24 | First draft, from proposal v4 section 4, before approval. Client Claude Code, model Claude Opus 5.5. |
| 0.9 | 2026-11-25 | Rewritten from the approved proposal v7. Title corrected to COP31. Added: rules G1 to G3 (G2 from the lead researcher's comment); legal form; the derivation of business status; hard cases B15 to B17; the utility attribute S1; tier 1 by core business with an "any activity" variant and a fuel field in place of the coal flag; tier 2B-S in use; the second condition for a negative; the "technical" class of unknown; the status of a classified record. Removed: tier 2B-M and the hard-case alternatives column (accepted under question 1). Client Claude Code, model Claude Fable 5.2. |
| 0.10 | 2026-11-25 | After the test on 20 organisations (`data/derived/draft-codebook/codebook-test/`; evidence by `evidence-finder`, labels by `org-classifier`, both Claude Sonnet; 120 notes of unclear rules). No label was changed by hand; the rules were. Added: rule numbers I1, C1 to C4, O4, Q1, U1; the identity rules for brands, units and shared names; "none" against "unknown" for the hard case; public bodies as not business; the definitions of business type; the standard for utility "no" and its effect on tier 2; ownership during a sale; four reasons for unknown and the class "not assessed"; confidence for each attribute, and identity confidence apart from the level of the source; where lobby registers, LEI records, laws and encyclopaedias sit in the order of evidence. Opened for the lead researcher: how strict a negative must be (section 9). Client Claude Code, model Claude Fable 5.2. |
| 0.11 | 2026-11-25 | After the independent check of 0.10 (methods review, Claude Opus; citation check, Claude Sonnet). Corrected: an unmatched brand goes to a person; non-profits that do not trade are not business; tier 2B-S follows the utility attribute; consultancies and law firms are "unknown, not assessed by rule" on every flag; a financial institution cannot be "none established" before tier 3 is defined; gas supply to end customers is F3; utility "no" on a register code no longer sets tier 2 to "not met"; ownership rules renumbered O1 to O5; definitions added; the labels block aligned. The proposal (4.6) gives eight reasons for unknown in three classes; this codebook has twelve in four, a change for the lead researcher to confirm with it. Client Claude Code, model Claude Fable 5.2. |
| 0.12 | 2026-11-25 | After the methods review of 0.11 (Claude Opus; 12 findings and what was done, in the review record). Changes: cross-sector associations and consultancies are "unknown, not assessed by rule"; tier 2B-S needs supply as the main activity (proposal 4.5); business status for K3 and K5 bodies and unknown hard cases; a body's own account cannot give "not met", and the second source for a negative must be independent; confidence where evidence is abstained; section 9 as a table, with a recommendation on negatives. Not checked again. Client Claude Code, model Claude Fable 5.2. |
