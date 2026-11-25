# Research proposal: Business and fossil fuel presence in government delegations at COP31

Drafted 25 November 2026 (version 7)

*Status: draft for comments, version 7, 25 November 2026. Version 6 went to the lead researcher on 25 November 2026; this version corrects the faults the study's independent check found in it, and the lead researcher's comments on version 6 will be merged in when they return. It is not approved. Decision numbers refer to the study's decision register; each change from version 6 is listed in the study's decision log.*

## 1. Summary

The study asks two questions of the delegations of the European Union and its Member States at COP31: how many delegates are affiliated with business, and how many of those are linked to the fossil fuel industry. Of the 34,809 registrations on Party and Party overflow badges, 3,821 are on the delegations of the EU and its Member States. They name about 1,500 organisations in self-declared free text, with no organisation type. The list records registrations, not people, and the study counts registrations.

Earlier counts, including Transparency International's for COP30, differ in what they count (3.4); no source read defines "business" for this purpose, so the definition here is the study's own (4.2).

The method classifies organisations, not people. Each organisation is identified, then given separate attributes (kind, commercial activity, sector, state ownership, a flag for each kind of fossil fuel link), from which a fixed table gives business status. A language model finds the evidence for each organisation and, in a separate step, applies the written rules to it; subsamples of its labels are checked by people who do not see them (6.5).

Section 8 sets out five questions and the further choices that need approval; no classification starts before the lead researcher replies.

## 2. Background and research questions

The brief is the document that commissions this study. It is not a published source, so quotations from it carry no endnote. The purpose, in its words:

> "This research should measure how much of the government-nominated presence at COP31 (UN climate conference 2026) comes from business, and how much of that is linked to the fossil fuel industry. Governments decide who gets the conference badges, with no UN eligibility rules or screening, so they are a key route for industry access to the negotiations."

The brief distinguishes two badge types. A Party badge is "the official national delegation, normally officials, negotiators and ministers". A Party overflow badge is one of the "extra badges a government hands out at its own discretion, often to business, NGOs, academics and guests. Holders get access to the Blue Zone (the official, UN-run conference area), and can observe negotiating rooms at times."

**Question 1: "How many delegates come from business, and from which sectors?"**

For the EU and each of its 27 Member States, the brief asks for a count of Party and Party overflow delegates whose home organisation is a business, by sector, with the two badge types shown separately, as a number and as a share of each delegation. Across all countries, "we could repeat the count if feasible", with priority to business on full Party badges.

The brief defines business as "for-profit companies, industry and trade associations, consultancies, law firms, and financial institutions". It adds: "Could be interesting to count state-owned enterprises separately rather than as public sector. Exclude NGOs, universities, think tanks and media."

**Question 2: "How many fossil fuel-linked delegates did EU countries invite?"**

The brief sets three tiers:

- Tier 1 (direct fossil fuel interests): oil, gas and petrochemical companies, as well as fossil fuel infrastructure operators.
- Tier 2 (partial fossil fuel exposure): utilities and companies operating in sectors with ongoing fossil fuel activities or dependencies.
- Tier 3 (financial exposure): banks, insurers and asset managers with documented fossil fuel financing exposure.

The wording of both questions is kept as given. Sections 4 and 8 mark each point at which this proposal would narrow or extend it.

## 3. What the literature says

### 3.1 The sources

As at 25 November 2026, the library search had considered 9,534 records and screened in 426: 134 read in full, with quotations and pages; 161 held but not read, 79 of them only a landing page, summary or empty page; 119 that failed to download; 10 with no web address; and 2 not yet downloaded. No statement rests on an unread source; the 121 endnotes cite 87 distinct works, nine of them read for this version.

Sixteen cited works were read as preprints or authors' manuscripts.[42][48][49][53][67][71][92][98][99][100][102][103][104][107][108][121] A model-assisted reader recorded each quotation with its page; quotations were checked automatically against the source text but not by a second reader, figures were not seen, and pages are positions in the file.

### 3.2 Who is on a party delegation

Before COP28, overflow participants could be nominated "without their names appearing on their official lists";[1][2] the COP28 list was the first to give each participant's nominating body, affiliation and badge type,[3] and a rule requiring an affiliation took effect at COP28.[4] The affiliation is self-declared free text that the secretariat cannot verify.[46] Overflow delegates "cannot negotiate or speak on a country's behalf",[5] yet are "officially part of the state delegation"[6] and not subject to the disclosure rules for observers.[7] Party badges too have been given to civil society, youth groups and the private sector,[8] and to NGOs.[9] At COP30, "more than 95% of non-state actors who entered through EU Member State delegations did so on Party Overflow badges".[10] A non-state actor on a delegation "becomes part of the government delegation" and is "often restricted in what they can say".[85] A negotiators' handbook notes that domestic industry "might be willing to finance its own participation" in a delegation and advises vetting potential members "carefully".[114] Delegations "can (and in many cases do) include actors from different sectors",[51] while observers are accredited through nine constituencies, business and industry among them.[52] For-profit companies "are not eligible for admission" as observers, though their representatives "can be nominated through already admitted NGOs";[113][46] among the ten largest oil and gas companies, staff of state-owned ones sit in delegations while those of investor-owned ones attend as observers,[87] one reason ownership is recorded (4.4). The list gives no type of organisation (section 5). Delegation size has been called "a crude measure" of a delegation's capacity.[84]

### 3.3 What "business" has meant

Transparency International's analysis of COP30 sorted non-state participants into five categories, using AI assistance.[11] It counted 885 non-state delegates in the EU delegations, of whom 526 were from business and commercial organisations and 359 from civil society and other organisations.[12] Other counts match 466 companies and associations against a database of corporate climate policy engagement,[13] which labels key associations by sector without saying how sectors are assigned,[14] count attendances rather than people,[78] or count one sector.[79] One Transparency International office labels itself an NGO, and an OECD recommendation on lobbying does not define business.[15][16] An academic study of organisations on delegations and among observers finds, in a descriptive figure for 72 countries, business at 26 per cent of observer organisations and 58 per cent of those on delegations; organisations were coded from their websites, and the study counts organisations, not registrations, and does not identify fossil fuel organisations.[88] Interest-group studies count business associations and firms together as business,[89][53][54] and survey work lists business associations and firms beside NGOs, trade unions and think tanks as kinds of interest group.[120] Where these studies assign sectors, they use industry classifications (ISIC, or SIC codes found by web search), and one leaves out organisations that the classification does not cover.[89][55][42] The European business register defines an enterprise by what it produces, "which benefits from a certain degree of autonomy", not by whether it represents commercial interests.[56] None defines a business delegate, so the definition in 4.2 is the study's own.

### 3.4 What "fossil fuel-linked" has meant

The counts most cited differ in what they count. A campaign coalition reports 2,456 fossil fuel lobbyists at COP28 and 1,773 at COP29. Its definition turns on intent: a person counts where it "can be reasonably assumed" they represent fossil fuel interests; a company counts where fossil fuels are a "significant" part of its business, meaning publicly declared; a trade association counts on any one of three criteria; finance, agribusiness and transport are not counted.[17][18][19][20][21] A related count finds 84 such delegates brought by nine EU governments to COP30,[22] and another 113 in the EU national delegations at COP29.[77] A peer-reviewed study took 2,347 delegates from the coalition's COP28 list, 3 per cent of 69,999, and checked them against its own sources.[25] Of the 339 people on the coalition's list who sat in national delegations at COP29, about 74 per cent (252) were affiliated with fully or partly state-owned companies and 23 per cent (81) with private companies or independent associations.[44] Trade associations are said to have a "lowest common denominator effect" on members' positions.[27] Consultancies are counted only where fossil fuel clients are "the overwhelming majority", with no figure given;[59] Transparency International's own declaration lists ties through "consultancy firms contracted by such industries", which a badge does not show.[28] Transparency International's count for COP30 found 63 delegates from 21 entities in the EU delegations,[23] and excluded steel and shipping.[24] The 84 and the 63 are not directly comparable: definitions, organisations and coverage all differ.[22][23] The UN secretariat's own partnership rules exclude, with conditional exceptions, entities "including but not limited to entities whose core products or core related services include fossil fuels"; they apply to the secretariat's partners, not to delegations.[115] Which criteria Transparency International applied at COP30 is a question for the lead researcher (section 8, question 3).

### 3.5 Methods of earlier counts and their limits

The closest precedent to this study's method is the coalition's COP29 count: clean the list, match names against lists and registers, search the web for each organisation, have a language model judge with references, then fact-check by hand.[30] Its COP28 count matched by script and then checked line by line.[29] Transparency International's COP30 count used "AI assistance", and 12 of its 21 entities were in a database of corporate policy engagement[31] that leaves out think tanks and consultancies, cannot see undisclosed lobbying and reports no agreement between scorers.[86] Other counts describe their own sources and searches.[32] None of the counts cited here reports its accuracy.[72][73][74][75][76][77] At COP29 nearly 15 per cent of participants (over 6,200) gave no affiliation, more than 90 per cent of them on Party or overflow badges,[36] and about 10 per cent of Party badge holders were listed as unpaid advisers.[8] Registers miss part of what they record: the EU Transparency Register "is not legally binding" and in 2013 was estimated to cover "75 percent for business organizations and 60 percent for non-governmental organizations (NGOs)";[117] a study of US regulation warns that unreported contacts pose, in its words, "significant methodological problems for those who rely on lobbying registrations".[121] significant methodological problems for those who rely on lobbying registrations".[121] Further limits are stated by the authors or their critics: counts may run too high[34] or, by the coalition's own account, too low,[33] seven COP30 delegates could not be classified,[35] the lists rely on self-description,[46] and presence is not influence.[37][38][43][60][63]

### 3.6 Influence and integrity

The literature on influence at the conferences, and on conflicts of interest in delegations, gives the reason for the count but not its method.[39][40][41][83][82][64][65][66] Influence by interest groups "is not a corrupt or illegitimate activity per se", but a "disproportionate influence of business groups" can become undue influence or state capture;[116] undue influence includes "soft tactics" that "capture the social, cultural, intellectual or scientific environment of the decision-maker".[119] Citizens in three countries judge policy-making less legitimate when interest groups are unequally involved, and are less concerned when cause groups, rather than business, are the over-represented side.[120] In 2017, conflict-of-interest rules in UN partnerships "are not in place".[118] Whether fossil fuel companies should be allowed at the conferences is itself under discussion.[114] An integrity checklist for delegations uses the phrase "core business" that tier 1 adopts (4.5);[90] an open letter on the subject is context only.[91] Non-state actors "do not have a formal role" under the convention[93] and must be accredited "if not on a party delegation";[92] that a delegation seat is therefore a route of access outside accreditation is this study's inference, not a finding of either source. Work on fossil fuels in conference texts[94] and on industry strategy[95][96][97][98] is background only. A preprint finds that one oil major "partners with almost half of INGOs in the climate establishment";[99] the attributes in 4.5 and 4.7 therefore record ties that run through bodies that are not businesses, without counting the partner as business.

### 3.7 Gaps, and who closes them

| Gap | Kind | Closed by |
|---|---|---|
| No operational definition of business in a delegation; no scheme of sectors applied to a participant list (3.3) | Decision on method | Section 4, approved by the lead researcher |
| No threshold for partial exposure or documented financing; no rule for subsidiaries; no definition of a state-owned company (3.4) | Decision on method | Section 4, approved by the lead researcher |
| No earlier count reports its accuracy (3.5) | Empirical | Human-checked subsamples (6.5) and the validation stage |
| No study counts business registrations inside EU party delegations by sector[88] | Knowledge | The literature search, continuing |
| A name on the list does not always identify one body (section 5) | Decision and empirical | Identity rules (6.1); names they do not settle stay unknown |

The study claims no priority while the search is unfinished. The method literature gives precedents for correcting estimates made from model labels,[69][102][68] testing models against detailed coding rules[70][49] and comparing model and human labels.[71][50] It calls validation against human coding "essential",[100][106] finds that instruction wording changes labels and conclusions,[101][109] recommends results "robust to synonymous prompts",[110] and notes that one run cannot show whether it is typical.[105] Models are least reliable where people disagree;[103][110][112] one agreed with expert coders as often as they agreed with each other,[111] and two manuscripts report patterns the coders "had not accounted for".[107][108] None tests classifying organisations by sector or fossil fuel link. A guide on responsible corporate engagement was not obtained and NACE has not been read in full; no definition rests on either.

## 4. Proposed definitions

### 4.1 Organisation type

Transparency International's COP30 analysis used five categories: public sector; business and commercial; civil society and other non-state; media and support staff; and others.[11] This study keeps the five as kinds of organisation, with one change (decision 1): support staff is a role, not a kind of organisation, so what a delegate does (adviser, support staff) is recorded in a separate field, and the fourth kind is media only.

### 4.2 Business

The indicators of business are: an entry in a company register, or a legal form, showing a for-profit entity; an association whose members are companies, according to its statutes or membership page; or a description as a company, firm or bank by an official register or by the organisation itself. The types of business are company, trade or industry association, consultancy, law firm and financial institution. State ownership is an attribute, not a type (4.4). The European definition of an enterprise is proposed as the starting point for "company" (decision 26).[56]

Alternatives: (a) self-description alone, simpler but less reliable; (b) companies only, leaving out associations, which departs from the brief.[11]

Legal form and activity are recorded apart: the legal form, as found, is stored in a field of its own, and each body that is not a company also receives a yes-or-no attribute, "represents commercial interests" (decision 25). The rules apply in a fixed order. First, a kind the table below places outside business (media, universities, think tanks, trade unions, legislatures) is not business whatever its legal form. Then a register entry or legal form decides; where there is none, an association's statutes or membership decide; self-description decides only where neither is found, and then at low confidence. Where indicators conflict, the higher one decides and the conflict is recorded (decision 30).

| Case | Business status proposed | Alternative |
|---|---|---|
| Company, private, state-owned or mixed | Business; ownership recorded apart (4.4) | None |
| Trade or industry association of companies | Business, as in the brief; also on its own line | Only on its own line |
| Association of companies and other bodies | Business where statutes or membership show a majority of companies; otherwise not, or unknown | Business wherever any member is a company |
| Chamber of commerce under private law | Business | None |
| Chamber under public law, compulsory membership | Not business; own line, so it can be added | Business |
| Cooperative | Business | Not business where it does not trade on its own account |
| Public development bank | Not business; own line, with ownership | Business |
| Development agency not lending commercially | Not business | None |
| Foundation set up by a company | Not business unless it trades; founder recorded | Business where the founder controls it |
| Municipal utility | Business; public ownership recorded | Other public body |
| Consultancy or law firm | Business, as in the brief; own line (4.5) | None |
| Self-employed consultant | Business where a register or business page shows trading; otherwise unknown | Not business |
| Trade union | Not business | None |
| Parliament or its committees | Not business; a legislature is a public body, not a commercial one | Other public body |
| Media company, including for-profit | Not business, as the brief excludes media; own line | Business where for-profit |
| University, public or private | Not business, as the brief excludes universities | None |
| Think tank | Not business, as the brief excludes think tanks; funders recorded where published | Business where a company funds or controls it |

### 4.3 Sector

The structure is fixed now: each organisation receives one primary sector, with further sectors as tags (decision 31). Three taxonomies are open: (a) a list of about 10 to 15 sectors written for this study; (b) the sector labels of a database of corporate climate policy engagement;[14] or (c) the ISIC classification or its European form, NACE.[55][89] The choice is made before the pilot, once NACE has been read in full: if NACE shows the distinctions within energy that the tiers need, it should be adopted; otherwise option (a), mapped to NACE (decision 2).

### 4.4 Ownership

A state-owned enterprise is a commercial entity in which a state holds a controlling interest. Two sources report state ownership beside their totals;[44][26] no source gives a threshold. The headline test proposed is a majority of the voting rights. A wider variant also counts golden shares and practical control (decision 3). State-owned enterprises are reported on their own line, inside the business totals.

Control may be held directly or through one or more intermediate companies. Along a chain of ownership, control passes where each link is a majority; holdings are not multiplied along the chain. This rule is the study's own. Where a link cannot be traced, the record says "chain incomplete" and the attribute is unknown. Ownership is taken as at the date of the conference.

### 4.5 Fossil fuel link

The tier is independent of business status; the kind of link is recorded apart from the tier, which expresses its strength (decision 27). The kinds proposed are own fossil fuel operations; electricity from fossil fuels; other commercial dependence, in sectors to be agreed; financing, insuring or owning fossil fuel activities; representing fossil fuel interests; none established; and unknown.

| Tier (the brief's wording, shortened) | Proposed indicators | Source |
|---|---|---|
| 1: oil, gas and petrochemical companies, infrastructure operators | The organisation explores for, extracts, refines, trades or transports oil, gas or coal, produces petrochemicals, or operates pipelines, terminals or storage for them. Headline: this is its core business (its largest segment by revenue in its filings; without filings, its main activity by its own account, at low confidence). Variant: any such activity, however small | Adapted from an earlier count;[19] "core business" from an integrity checklist;[90] adding coal is this study's proposal (decision 32) |
| 2: utilities and sectors with fossil fuel activities or dependencies | 2A: a utility, meaning a body that generates or supplies electricity, gas or heat to others, any of it from fossil fuels. 2B: other dependence on fossil fuels, in a sector on an agreed list, in two variants (below) | Own proposal; no threshold found in the literature |
| 3: banks, insurers and asset managers with documented financing exposure | Meets a written definition of documented exposure; an approved list is evidence for it, not the definition | Own proposal; the COP30 entity list gives no criteria (3.4) |

Tier 2B is measured in two variants, run side by side (decision 20):

| Variant | What it measures | Role |
|---|---|---|
| 2B-O | An organisation in a sector on the agreed list for which a source of level A to C (4.7) documents that its own operations depend on fossil fuels | Headline for 2B |
| 2B-S | An organisation whose primary sector is on the agreed list, whether or not that dependence is documented | Wider variant, reported beside the headline |

Other dependent sectors have no agreed boundary (steel and shipping were excluded at COP30[24]), so the list holds utilities only, as the brief names them, until a wider one is approved (decision 5). A renewable-only utility meets no 2A; only 2B-S counts it. No percentage threshold is set before the pilot;[57][59][61] any threshold later needed is a new decision. Earlier counts treat coal separately;[61][62][80][81] here it carries its own flag within tier 1, so counts can be shown with and without it (decision 32).

A single-sector trade association takes the tier of its sector; a cross-sector association takes none; all trade associations are reported on their own line (decisions 7 and 33).[20][58] Subsidiaries, joint ventures and holding companies are classified on their own activity, every parent is recorded, and the parent's tier is shown as a variant (decision 8).[23][45] Consultancies and law firms are business with no tier, reported on their own line (decisions 9 and 34), because their fossil fuel clients may not be visible from public sources;[28][59] that inference is this study's, drawn from consultants' work "often portrayed to the public as independent".[97]

Any current activity counts; past activity is recorded, not counted (decision 21). Each tier is an independent flag, met, not met or unknown, so that an organisation may carry several; every flag met is recorded, and so is the highest. A headline figure assigns each organisation to its first tier met in the order 1, 2A, 2B-O, 3; a second version uses 2B-S in place of 2B-O (decision 35). A news item copied from a press release counts as the same source. The kind of exposure, threshold, period and sources for tier 3 are for the lead researcher (decision 6).

### 4.6 Unknown

"Unknown" is given for one of eight recorded reasons, in three classes:

- **Identity unresolved:** the field is blank; the text is generic (for example "Private sector"); the text is not an organisation; or the name could refer to several bodies.
- **Evidence insufficient:** nothing was found; the sources conflict; or the agreed rules do not cover the case.
- **Technical:** the lookup failed (a search or page could not be completed). These are run again before any count and reported apart.

An unknown of the second class is not evidence of absence. The rule for establishing a negative is that "not met" may be given only on a source of level A or B (4.7) that gives a full description of the organisation's activities, and, since an organisation has reason to understate fossil fuel activity, its own reports must be confirmed by a source of level B or C; publicity material is not enough, and otherwise the answer is unknown. Confidence is recorded for each of the three claims (identity, activity and rule met), and the overall confidence of a label is the lowest of the three (decision 36).

### 4.7 Dimensions and how they relate

Ten fields are stored independently, and no label carries two. Eight are dimensions of the organisation: kind, legal form, commercial activity, represents commercial interests, sector, state ownership, kind of link and tier flags. Two are metadata about the classification, not attributes of the organisation: the class of any unknown (4.6) and confidence. Business status follows from kind, legal form, commercial activity and represents commercial interests (decision 19). A public body may hold a tier; it is reported on its own line, outside the fossil fuel-linked share of business (decision 15).

For each claim, sources are ranked from A to E.

| Level | Kind of source | Used for |
|---|---|---|
| A | The organisation's official filings and annual reports; government registers | Identity, legal form, ownership and activities |
| B | Filings with regulators; government publications; established industry databases | Independent confirmation |
| C | Established research organisations and specialist datasets | Sector and fossil fuel exposure |
| D | Journalism from established outlets | Supporting or contextual evidence only |
| E | The organisation's description of itself; general web pages | First identification; weak evidence for anything else |

For a claim that an organisation has reason to understate, an independent source of level B or C ranks above the organisation's own account. The authority of a source and its independence from the organisation are recorded separately (decision 22).

## 5. Data

The registration list holds 34,809 registrations: 18,812 on party badges and 15,997 on overflow badges. The EU and its Member States form 28 delegations, with 3,821 registrations: 1,381 party and 2,440 overflow. Delegations range from 15 to 607 registrations; the EU's own has 271. These and the figures below come from the study's data profile and its list of numbers.

Of the 3,821 registrations, 3,799 name an organisation; the other 22 are blank, a placeholder, a generic term, a country or a person (6.3). The organisation names are typed in 1,599 different ways. Fixed cleaning rules reduce these to 1,582; matching names that are identical once cleaned gives 1,507; and six automatic merges give 1,501 organisations, government bodies included, of which 840 have a single registration.

Two problems of identity remain, measured in registrations, as shares of the 3,799 that name an organisation. There are 108 pairs of similar names awaiting review, involving 137 organisations and 529 registrations (13.9 per cent); if every pair were accepted, 1,421 organisations would remain and 146 registrations would change organisation. There are 122 acronyms, covering 390 registrations (10.3 per cent). Together the two problems touch 919 registrations (24.2 per cent), in 23 of the 28 delegations. The number to classify is therefore between 1,421 and 1,501 before government bodies are set aside; the figure of about 1,250 used for planning leaves them out and is an estimate, not a count.

One person is listed twice on the same badge type, and no person holds both badge types for one country; all 3,821 rows are counted as registrations, not as distinct people. Title, department and relation fields are not used to classify.

## 6. Method

### 6.1 Preparing the data and resolving identity

Cleaning is done by code, logged, and keeps the original text. Identity is a step of its own, under nine written rules (decision 37) covering legal entities, parents, brands, branches and subsidiaries, joint ventures, holding companies, mergers, shared acronyms and bodies in two delegations. Ambiguous cases are reviewed by a person, the largest first. Each organisation receives a stable identifier, and the unresolved share is reported for each delegation.

### 6.2 Evidence

Each organisation goes through six steps, one at a time. The first four find and store evidence; the last two classify it.

1. **Search.** The search is given only the organisation's name as written, its country and its variant spellings. It starts from a fixed list of sources (the national company register, open registers of companies, annual reports and the EU Transparency Register), then searches the web in the language of the nominating country and in English, to a stated minimum (decision 44). The financing databases for tier 3 are approved by the lead researcher (decision 6). Each search, its language, and each source tried, reached or refused is logged, and unknowns are reported by language.
2. **Store.** Each page used is saved with its address, the time it was retrieved and an archived copy with a hash, so that anyone can later see exactly what was read.
3. **Quote.** The model reads the stored pages and copies the passages that show what the organisation is, who controls it and what it does, with the claim each supports, the evidence level (A to E), its independence, language and any translation (decision 38).
4. **Check the quotes.** Code checks that each quotation appears word for word in the stored page. A further check asks whether the quotation states the claim, about the matched organisation, for the required period; a claim that fails goes to unknown.
5. **Classify.** A separate step with no web access reads only the stored evidence, applies the written rules (the codebook) and names the rule and the evidence behind each label. Code sets the confidence from the evidence level.
6. **Check the labels.** A second, smaller model flags labels the evidence may not support, for a person to review. It never changes a label, and its own error rate is not yet measured.

Steps 1 to 3 and step 5 are separate runs of one model; the model and version actually used are recorded with every result. A hand-run feasibility test on 20 organisations gives provisional results only; none of them was used to set a definition.

### 6.3 Missing organisations

The 22 registrations that name no organisation stay in the total. The proposed procedure, for a blank or generic affiliation only, searches public pages for the person's employer and records only the employer and the source address, in a column of its own beside the original; it uses no logged-in pages, and a match needs two agreeing details. Whether it is used is a decision for the lead researcher, after Transparency International's data-protection lead has reviewed it (decisions 41 and 11).

### 6.4 Checks

Automatic checks confirm that each address opens, each quotation appears in the archived copy and the page concerns the organisation; they detect errors of process, not of classification. A repeat run on 10 per cent of organisations, half searching again and half reusing the stored evidence, measures repeatability;[47][48] it is reported as a rate of agreement, apart from accuracy. Cases where the runs disagree are reviewed by a person and kept out of the accuracy estimates. Measuring repeatability apart from validity follows the method literature (3.7);[111][105] one source could ensure reproducible output only with open models run locally at the lowest temperature.[104] The share of 10 per cent is this study's proposal.

### 6.5 Human-checked subsamples and reporting

People check the model's work on four sets. The pilot and the fixed test set are drawn at random before the model runs and do not overlap; the other two come from the model's output and are checked because of it:

| Set | What it is | What it is for |
|---|---|---|
| Pilot | 50 organisations drawn at random; a sector expert labels them without seeing the model's labels | The pilot standard (section 8, question 4), cost, the share of unknowns and the expert's time per organisation |
| Fixed test set | 50 other organisations, labelled by the sector expert before tuning | Run again after any change to the rules, the wording or the model; the instructions are tuned on it, never on the pilot |
| Named organisations | Every organisation named in a report as fossil fuel-linked, whatever its confidence | A person checks it and signs off on the exact record; if the record changes, the sign-off lapses |
| Disagreements | Cases where the two runs in 6.4 disagree | Reviewed by a person, kept out of the estimates |

The full validation design, which measures accuracy on the whole run (its sample, weights and intervals), is approved separately at the validation stage, before any result is published.

Shares are out of all registrations (decision 14); unknowns stay in the total, with bounds never called a confidence interval. Classification error, coverage and sampling are reported as three separate uncertainties. Coverage, meaning the share of organisations resolved, is reported by delegation, by language and by badge type. Tier 2B is shown in both variants side by side (decision 35), with associations, consultancies and the EU delegation on lines of their own (decisions 33, 34 and 10). A leave-one-delegation-out check shows whether one delegation drives the result.

The study produces one table with a row per organisation, to which registrations join, so the count can be re-run under another definition without new searches; its publication belongs with decision 18.

## 7. Use of a language model

A language model reads sources, looks up and classifies organisations, and drafts text from the tables; counting, matching, sampling and statistics are ordinary code. It is used because of scale (between 1,421 and 1,501 organisations, no type in the data, no labelled list from an earlier conference) and treated as an assistant whose work is measured, not as an authority.

- **Finding evidence is kept apart from classifying it:** a step with no web access classifies from the stored evidence (6.2, step 5) and cites the rule it applies, so the two kinds of error can be told apart.
- **Code decides what a fixed rule can:** exact name matches, precedence between flags, overall confidence.
- **Every run is recorded:** model and version, instructions, searches, pages, settings, date, retries and manual fixes; one version throughout.
- **Repeatability, validity and coverage are measured separately** (6.4, 6.5). Instructions are tuned on the fixed test set of 50 (one source suggests 100 to 200[67]), never on the pilot or the validation sample.

The risks that arise from the model itself, and the control for each:

| Risk | Control |
|---|---|
| Invented facts or sources | No label without a source; every address and quotation is checked automatically (6.4) |
| A claim the evidence does not make | A separate step checks each claim against its quotation, in the original language (6.2, step 4) |
| Instructions hidden in web pages | Retrieved content is treated as untrusted; the classifying step sees only stored evidence; the fixed test set includes pages with planted instructions |
| Sensitivity to wording | A second wording of the same rules is run on the fixed test set and the labels compared. This tests sensitivity to wording, not repeatability, which 6.4 measures.[101][109][110] |
| Failure on cases people also dispute | Cases where two runs disagree are reviewed by a person and kept out of the estimates[103][112] |
| The expert defers to the model | The expert never sees the model's label or reasoning (6.5) |

## 8. Questions for the lead researcher

Questions 1 to 4 are needed before the pilot, question 5 only before publication; the section named holds the detail.

1. **Which borderline organisations count as business?** The brief settles the clear cases (4.2). For the rest, the table in 4.2 proposes a side for each case, such as public-law chambers, public development banks and cooperatives, and counts each on its own line, so the total can be recalculated. *Question:* does any fall on the wrong side for Transparency International? *Recommendation:* accept them; 4.2 gives the alternative for each.

2. **Which sectors besides those of tier 1 (oil, gas, petrochemicals and their infrastructure; coal is an open choice) count as dependent on fossil fuels (tier 2)?** The brief names utilities and "sectors with fossil fuel activities or dependencies" without a list; the COP30 count left out steel and shipping. The options are utilities only, or a longer list. An organisation in a listed sector counts only where a source shows its own operations depend on fossil fuels; the sector total is shown beside it. *Recommendation:* utilities only for the pilot; a sector can be added later without new searches, as every sector is stored (4.5).

3. **What makes a bank, insurer or asset manager fossil fuel-linked (tier 3)?** The brief speaks of "documented financing exposure", but no source read gives criteria or a threshold, and the COP30 list of entities does not say how they were chosen (3.4). *Question:* which criteria were used at COP30; does any documented financing, insurance or ownership count, or only above a size; over which years; from which databases? *Recommendation:* a written definition before the pilot, based on the COP30 criteria if they can be supplied; a listing in a database is then evidence, not the definition.

4. **How accurate must the pilot be before the full run?** In the pilot, a sector expert classifies 50 organisations drawn at random, without seeing the model's answers (6.5). The proposed standard, for business and for any fossil fuel tier: at least 90 per cent of the model's labels agree with the expert; the model finds at least 80 per cent of the cases the expert identifies; and no more than 20 per cent of the 50 are unknown. Figures by tier are indicative. If the pilot falls short, the codebook is revised and re-run on a new random sample. *Question:* are these levels right? *Recommendation:* as proposed; they are this study's own, as no earlier count reports its accuracy (3.5).

5. **Will organisations be named?** Whether organisations classified as fossil fuel-linked are named in the report, and if so whether each is first offered the chance to respond. No recommendation is made; this is a matter of Transparency International's practice.

**Further choices that need the lead researcher's approval,** each with a recommendation in the section named: the sector scheme (4.3); whether coal counts in tier 1 (4.5, decision 32); the rule for subsidiaries (4.5, decision 8); whether the EU's own delegation is reported with the Member States (decision 10); the order in which evidence is ranked (4.7); the variant of tier 1 used for the headline (4.5); and, at the validation stage, the design of the validation sample.

**What the study needs from the lead researcher before the pilot:**

- the documents that could not be obtained automatically (the counts are in 3.1), and the guide on responsible corporate engagement named in 3.7;
- rulings on the organisation names that the identity rules do not settle;
- the names of the statistician and of the data protection contact.

None of these choices is fixed until the lead researcher agrees it. The lead researcher may rewrite any part of this proposal; a rewritten version becomes the basis of the work, and each change of substance is recorded as a decision.

## Endnotes

Each note gives the full reference and the page, section or paragraph.

1. Carbon Brief Staff (McSweeney, R. and Viisainen, V.), 2024, "Analysis: Which countries have sent the most delegates to COP29?", *Carbon Brief*, https://www.carbonbrief.org/analysis-which-countries-have-sent-the-most-delegates-to-cop29/, section "All aboard to Baku". [carbonbrief-analysis-which-countries-have-sent-the-most-delegates-to-c]
2. Same source, section "All aboard to Baku".
3. Xie, L., Escher, R., Dunn, M. and others, 2025, "Tracing inclusivity at UNFCCC conferences through side events and interest group dynamics", *Nature Climate Change* 15, 270–278, https://doi.org/10.1038/s41558-025-02254-9, section "COP28 delegation". [doi-10-1038-s41558-025-02254-9]
4. Kick Big Polluters Out coalition, 2024, "Release: Fossil fuel lobbyists eclipse delegations from most climate vulnerable nations at COP29 climate talks", https://kickbigpollutersout.org/COP29FossilFuelLobbyists, para. 14. See also Global Witness, 2024, "COP29 is for oil deals", https://globalwitness.org/en/campaigns/fossil-fuels/cop29-is-for-oil-deals/, section "Keep your enemies closer". [kickbigpollutersout-cop29fossilfuellobbyists] [globalwitness-cop29-is-for-oil-deals]
5. Transparency International, 14 September 2026, "COP Talks: Formal Delegations, Informal Access", https://www.transparency.org/en/news/cop30-formal-delegations-informal-access, section "What is a Party Overflow badge?". See also Gverdtsiteli, G., 2025, *Fuelling Delay: How fossil fuel interests shape global climate negotiations*, Transparency International, https://files.transparencycdn.org/images/TI_FuellingDelay_FINAL.pdf, p. 9. [ti-2026-formal-delegations] [ti-2025-fuelling-delay]
6. Transparency International, 15 October 2025, "Climate Summit or Industry Trade Fair?", https://www.transparency.org/en/news/climate-summit-or-industry-trade-fair, section "JBS". [ti-2025-trade-fair]
7. Transparency International 2026, "COP Talks", section "What is a Party Overflow badge?".
8. Gverdtsiteli, G., 2025, *Fuelling Delay: How fossil fuel interests shape global climate negotiations*, Transparency International, https://files.transparencycdn.org/images/TI_FuellingDelay_FINAL.pdf, p. 21. [ti-2025-fuelling-delay]
9. McSweeney and Viisainen 2024, section "Host lead".
10. Transparency International 2026, "COP Talks", section "What is a Party Overflow badge?".
11. Transparency International 2026, "COP Talks", section "Methodology".
12. Transparency International 2026, "COP Talks", section "Business speaks louder than civil society in the EU member state delegations".
13. Transparency International 2025, "Climate Summit or Industry Trade Fair?", section "Tracking business influence at COPs".
14. InfluenceMap, 2025, "European Industry and the EU's Climate Policy 2024-29", https://influencemap.org/briefing/European-Industry-and-the-European-Union-s-Climate-Policy-in-2024-29-32272, table "How Europe's Key Industry Associations Compare on Climate Policy Engagement", and Introduction. [influencemap-european-industry-and-the-european-union-s-climate-policy]
15. Kergueno, R., 10 April 2025, "New data, more corporate access? Integrity Watch EU update shows Commission leaves civil society in the dark", Transparency International EU, https://transparency.eu/new-data-more-corporate-access-integrity-watch-eu-update-shows-commission-leaves-civil-society-in-the-dark/, para. 10. [transparency-new-data-more-corporate-access-integrity-watch-eu-update]
16. OECD, 2025 edition, *Recommendation of the Council on Transparency and Integrity in Lobbying and Influence*, OECD/LEGAL/0379, https://legalinstruments.oecd.org/public/doc/256/256.en.pdf, p. 9. [oecd-256-en]
17. Kick Big Polluters Out coalition, 5 December 2023, "Release: Record number of fossil fuel lobbyists at COP28", https://kickbigpollutersout.org/articles/release-record-number-fossil-fuel-lobbyists-attend-cop28, para. 3; Kick Big Polluters Out 2024, para. 1. [kickbigpollutersout-release-record-number-fossil-fuel-lobbyists-attend]
18. Kick Big Polluters Out 2024, para. 31. See also Kick Big Polluters Out 2023, para. 41.
19. Kick Big Polluters Out 2023, paras 48 and 49.
20. Same source, para. 50.
21. Same source, para. 17; Kick Big Polluters Out 2024, para. 12.
22. Fossil Free Politics, 14 November 2025, "EU Commission keeps oil and gas lobbyists away from COP30, but France and Italy roll out red carpet", https://fossilfreepolitics.org/news/eu-brings-84-fossil-fuel-lobbyists-to-cop/, paras 2 and 22. [fossilfreepolitics-eu-brings-84-fossil-fuel-lobbyists-to-cop]
23. Transparency International 2026, "COP Talks", Summary and section "Methodology".
24. Transparency International 2026, "COP Talks", section "Methodology".
25. Xie and others 2025, sections "COP28 delegation", "Paths of interest group access to COP28" and "Interest group identification". The 3 per cent is the source's own rounding.
26. Gverdtsiteli 2025, *Fuelling Delay*, p. 8.
27. InfluenceMap 2025, "European Industry", Executive Summary ("lowest common denominator effect"); section "Corporate Climate Policy Engagement in the EU from 2019-2025" ("most negative voices"); table "How Europe's Key Industry Associations Compare on Climate Policy Engagement" (sector labels).
28. Transparency International 2025, "Climate Summit or Industry Trade Fair?", para. 27, section "Petrobras".
29. Kick Big Polluters Out 2023, paras 44 to 46.
30. Kick Big Polluters Out 2024, paras 28 to 35.
31. Transparency International 2026, "COP Talks", Summary and section "Methodology".
32. Kick Big Polluters Out 2024, para. 27; Xie and others 2025, "Data availability"; Fossil Free Politics 2025, para. 14. For COP28: Kick Big Polluters Out 2023.
33. Kick Big Polluters Out 2023, paras 18 and 47.
34. Xie and others 2025, Discussion.
35. Transparency International 2026, "COP Talks", section "Methodology".
36. Gverdtsiteli, G., June 2025, *Behind the Badge: Understanding the roles, reach, and risks of fossil fuel industry participation in UN climate talks*, Transparency International working paper, https://images.transparencycdn.org/images/Transparency-International_Behind-the-Badge.pdf, pp. 5 and 6; reported in Gverdtsiteli 2025, *Fuelling Delay*, pp. 10 and 21. [transparencycdn-transparency-international-behind-the-badge]
37. Transparency International 2026, "COP Talks", Summary.
38. Kergueno 2025, para. 12.
39. Gverdtsiteli 2025, *Fuelling Delay*, p. 10; Kick Big Polluters Out, 2025, "Letter: 225+ organizations demand COP30 center people, not polluters", https://kickbigpollutersout.org/Polluter-Free-COP30, para. 4; Transparency International 2025, "Climate Summit or Industry Trade Fair?", section "Tracking business influence at COPs". [kickbigpollutersout-polluter-free-cop30]
40. DCJ-ENGO, YOUNGO, CAN, WGC and TUNGO constituencies, 17 August 2022, "Joint civil society submission on establishing a UNFCCC Accountability Framework to protect against undue influence of polluting interests", hosted by Corporate Accountability, https://corporateaccountability.org/wp-content/uploads/2022/08/Joint-civil-society-submission-on-COI-Aug-17-2022_.pdf, p. 5 (definition), p. 6 (contrast), Annex 1, pp. 10 to 13 (endorsing organisations; Transparency International on p. 13). [corporateaccountability-joint-civil-society-submission-on-coi-aug-17-2]
41. OECD 2025, p. 8; not legally binding, p. 12.
42. Jiang, T. and others, 2023, "Classifying organizations for food system ontologies using natural language processing", arXiv preprint 2309.10880, https://doi.org/10.48550/arxiv.2309.10880, p. 5. [doi-10-48550-arxiv-2309-10880]
43. Gverdtsiteli 2025, *Behind the Badge*, p. 5 (working definition), pp. 6 and 7.
44. Same source, p. 11.
45. Transparency International, 2026, "Fossil fuel-linked entities across three tiers", attachment to the COP30 analysis, https://images.transparencycdn.org/images/Fossil-Fuel-Linked-entities.pdf, pp. 1 and 2. [transparencycdn-fossil-fuel-linked-entities]
46. Gverdtsiteli 2025, *Behind the Badge*, pp. 5 and 6, 12 and 14.
47. Bermejo, V. J., Gago, A., Gálvez, R. H. and Harari, N., 2025, "LLMs outperform outsourced human coders on complex textual analysis", *Scientific Reports*, https://doi.org/10.1038/s41598-025-23798-y, sections "LLMs as coders", "Internal consistency" and "Limitations and future work". [doi-10-1038-s41598-025-23798-y]
48. Alizadeh, M., Kubli, M., Samei, Z., Dehghani, S., Zahedivafa, M., Bermeo, J. D., Korobeynikova, M. and Gilardi, F., 2025, "Open-source LLMs for text annotation: a practical guide for model setting and fine-tuning", *Journal of Computational Social Science* 8, 17, https://doi.org/10.1007/s42001-024-00345-9, section "Choosing the training approach". See also Cheng, X., Mayya, R. and Sedoc, J., 2024, "To err is human; to annotate, SILICON? Reducing measurement error in LLM annotation", arXiv preprint 2412.14461, version 4, May 2026, https://doi.org/10.48550/arxiv.2412.14461, p. 33. [doi-10-1007-s42001-024-00345-9] [doi-10-48550-arxiv-2412-14461]
49. He, Murugesan, Brandt and Hu, 2026, "When better codebooks are not enough", arXiv preprint 2606.06781v2, https://doi.org/10.48550/arxiv.2606.06781, pp. 6 and 7. [doi-10-48550-arxiv-2606-06781]
50. Jiang and others 2023 (preprint), pp. 9 and 10.
51. Nasiritousi, N., Buylova, A., Fridahl, M. and Reischl, G., 2024, "Making the UNFCCC fit for purpose: a research agenda on vested interests and green spiralling", *Global Policy* 15, 487–494, https://doi.org/10.1111/1758-5899.13356, p. 4. [doi-10-1111-1758-5899-13356]
52. Kuyper, J. W., Bäckstrand, K. and Schroeder, H., 2016, "Institutional accountability of nonstate actors in the UNFCCC: exit, voice, and loyalty", *Review of Policy Research*, https://doi.org/10.1111/ropr.12213, pp. 1 and 8; Roberts, J. T., Milani, C. R. S., Jacquet, J. and Downie, C. (eds), 2025, *Climate Obstruction: A Global Assessment*, Oxford University Press, read in part, https://doi.org/10.1093/oso/9780197787144.001.0001, p. 311. [doi-10-1111-ropr-12213] [doi-10-1093-oso-9780197787144-001-0001]
53. Dür, A., Bernhagen, P. and Marshall, D., 2015, "Interest group success in the European Union: when (and why) does business lose?", *Comparative Political Studies*, authors' manuscript, https://doi.org/10.1177/0010414014565890, pp. 19 and 29. [doi-10-1177-0010414014565890]
54. Junk, W. M., Crepaz, M., Hanegraaff, M., Berkhout, J. and Aizenberg, E., 2022, "Changes in interest group access in times of crisis: no pain, no (lobby) gain", *Journal of European Public Policy* 29(9), 1374–1394, https://doi.org/10.1080/13501763.2021.1968936, pp. 11 and 12. [doi-10-1080-13501763-2021-1968936]
55. Berkhout, J., Carroll, B. J., Braun, C., Chalmers, A. W., Destrooper, T., Lowery, D., Otjes, S. and Rasmussen, A., 2015, "Interest organizations across economic sectors: explaining interest group density in the European Union", *Journal of European Public Policy* 22(4), 462–480, https://doi.org/10.1080/13501763.2015.1008549, pp. 9, 10 and 17. [doi-10-1080-13501763-2015-1008549]
56. Eurostat, 2024, "European Union business registers metadata 2024", European business statistics manual for business registers, https://ec.europa.eu/eurostat/cache/website/business-registers/metadata/european-union-business-registers-metadata-2024.htm, section 3.1 para. 20, section 3.5 paras 77 to 79, section 3.6 paras 88 and 89. [eurostat-2024-business-registers-metadata]
57. Kick Big Polluters Out, November 2025, "KBPO's fossil fuel lobbyist research: Method and FAQs", https://kickbigpollutersout.org/sites/default/files/2025-11/KBPO%E2%80%99s%20fossil%20fuel%20lobbyist%20research-%20Method%20and%20FAQ%E2%80%99s.pdf, p. 1. [kbpo-2025-lobbyist-method-faq]
58. Kick Big Polluters Out 2025, "Method and FAQs", p. 3.
59. Kick Big Polluters Out 2025, "Method and FAQs", pp. 2 and 4.
60. Kick Big Polluters Out 2025, "Method and FAQs", pp. 2, 3 and 4.
61. Urgewald, 12 November 2024, "Global Oil & Gas Exit List 2024: Definitions and Methodology", https://gogel.org/sites/default/files/2025-02/Methodology%20public%20GOGEL%202024_final_website.pdf, pp. 1 to 4, 6, 7, 9 and 11. [urgewald-2024-gogel-methodology]
62. Kühne, K., Bartsch, N., Tate, R. D., Higson, J. and Habet, A., 2022, "'Carbon Bombs': Mapping key fossil fuel projects", *Energy Policy* 166, 112950, https://doi.org/10.1016/j.enpol.2022.112950, pp. 1 and 3. [doi-10-1016-j-enpol-2022-112950]
63. Roberts and others (eds) 2025, p. 314 and note 140 on p. 324 (pages of the file read).
64. Nasiritousi and others 2024, pp. 2, 3 and 5.
65. Roberts and others (eds) 2025, pp. 25 and 316 (pages of the file read).
66. Honkonen, T., 2025, "Civil society participation in EU preparation for UN climate negotiations: questions of openness and transparency", *Review of European, Comparative and International Environmental Law* 34(2), 379–393, https://doi.org/10.1111/reel.12620, pp. 2, 3, 7, 8 and 11. [doi-10-1111-reel-12620]
67. Lin, H. and Zhang, Y., 2025, "Navigating the risks of using large language models for text annotation in social science research", *Social Science Computer Review*, read as the preprint arXiv 2503.22040v2, https://doi.org/10.1177/08944393251366243, pp. 5, 6, 12, 13 and 21. [doi-10-1177-08944393251366243]
68. Ziems, C., Held, W., Shaikh, O., Chen, J., Zhang, Z. and Yang, D., 2024, "Can large language models transform computational social science?", *Computational Linguistics*, https://doi.org/10.1162/coli_a_00502, pp. 4, 32 and 35. [doi-10-1162-coli-a-00502]
69. Egami, Hinck, Stewart and Wei, 2023, "Using Imperfect Surrogates for Downstream Inference: Design-based Supervised Learning for Social Science Applications of Large Language Models", NeurIPS 2023, http://papers.nips.cc/paper_files/paper/2023/file/d862f7f5445255090de13b825b880d59-Paper-Conference.pdf, pp. 1, 2, 4 and 10. [nips-d862f7f5445255090de13b825b880d59-paper-conference]
70. Halterman and Keith, 2025, "Codebook LLMs: Evaluating LLMs as Measurement Tools for Political Science Concepts", Political Analysis 34(2), April 2026, 188–204, https://doi.org/10.1017/pan.2025.10017, §§4.3, 6.1, 7.1, 8.2, 8.6 and 10. [doi-10-1017-pan-2025-10017]
71. Pangakis, Wolken and Fasching, 2023, "Automated Annotation with Generative AI Requires Validation", arXiv 2306.00176v1, http://arxiv.org/pdf/2306.00176, pp. 4, 8, 10 and 15. [arxiv-2306-00176-2]
72. Global Witness, n.d., "Our methodology for the COP27 fossil fuel lobbyists analysis", https://globalwitness.org/en/campaigns/fossil-fuels/our-methodology-for-the-cop27-fossil-fuel-lobbyists-analysis/, body para 7; Definitions para 11. [globalwitness-our-methodology-for-the-cop27-fossil-fuel-lobbyists-anal]
73. Kick Big Polluters Out coalition, published by Global Witness, n.d., "Record number of fossil fuel lobbyists granted access to COP28 climate talks", press release, https://www.globalwitness.org/en/press-releases/record-number-fossil-fuel-lobbyists-granted-access-cop28-climate-talks/, Definitions; Topics. [globalwitness-record-number-fossil-fuel-lobbyists-granted-access-cop28]
74. Global Witness with Corporate Accountability and CEO, n.d., "636 fossil fuel lobbyists granted access to COP27", https://www.globalwitness.org/en/campaigns/fossil-gas/636-fossil-fuel-lobbyists-granted-access-cop27/, Topics. [globalwitness-636-fossil-fuel-lobbyists-granted-access-cop27]
75. Kick Big Polluters Out coalition, 2025, "RELEASE: Fossil fuel lobbyists flood COP30 climate talks in Brazil, with largest ever attendance share", https://kickbigpollutersout.org/Release-Kick-Out-The-Suits-COP30, Intro para 4; Methodology para 51. [kickbigpollutersout-release-kick-out-the-suits-cop30]
76. Corporate Europe Observatory (analysis by Kick Big Polluters Out), 2023, "Investigation: Fossil fuel lobbyists attend UN climate talks more than 7000 times as part of decades-long campaign to influence climate action", https://corporateeurope.org/en/2023/11/investigation-fossil-fuel-lobbyists-attend-un-climate-talks-more-7000-times-part-decades, Methodology para 35; Findings para 20. [corporateeurope-investigation-fossil-fuel-lobbyists-attend-un-climate]
77. Fossil Free Politics, 18 November 2024, "Europe brings gas lobbyists to COP29 to strike deals", press release, https://fossilfreepolitics.org/news/europe-brings-gas-lobbyists-to-cop29-to-strike-deals/, paras 1–2 and 16–18. [fossilfreepolitics-europe-brings-gas-lobbyists-to-cop29-to-strike-deal]
78. Climate Investigations Center, n.d., "Thousands of Fossil Fuel "Observers" Attended Climate Negotiations – UNFCCC Data 2005-2018 COP1-COP24", https://climateinvestigations.org/thousands-of-fossil-fuel-observers-attended-climate-negotiations-unfccc-data-2005-2018-cop1-cop24/, the whole page (no section recorded). [climateinvestigations-thousands-of-fossil-fuel-observers-attended-clim]
79. Sherrington, Carlile and Healy, 2023, "Big Meat and Dairy Delegates Triple at COP28", DeSmog, https://www.desmog.com/2023/12/08/big-meat-dairy-delegates-triple-cop28/, sections "Privileged Access to Negotiations" and "The Bigger Picture". [desmog-big-meat-dairy-delegates-triple-cop28]
80. Banking on Climate Chaos coalition, 2026, "Methodology FAQ, Banking on Climate Chaos: Fossil Fuel Finance Report 2026", https://www.bankingonclimatechaos.org/methodology-2026, pp. 4 and 8. [bankingonclimatechaos-methodology-2026]
81. Banking on Climate Chaos coalition, 2026, "BOCC Fossil Fuel Expansion Companies", https://www.bankingonclimatechaos.org/companies-2026, p. 1. [bankingonclimatechaos-companies-2026]
82. Climate Action Network, 2020, "Climate Action Network Position on Conflicts-of-interest and polluting industry obstruction of climate policy in the UNFCCC Process", https://climatenetwork.org/wp-content/uploads/2020/11/can_position_on_conflicts_of_interest-2.pdf, pp. 2–4. [climatenetwork-can-position-on-conflicts-of-interest-2]
83. Transparency International, 2019, "Conflict of interests", Corruptionary, https://www.transparency.org/en/corruptionary/conflict-of-interests, Definition. [transparency-conflict-of-interests]
84. Klöck, C., Baatz, C. and Wendler, F., 2025, "Procedural justice and (in)equitable participation in climate negotiations", *UCL Open Environment* 7(1), https://doi.org/10.14324/111.444/ucloe.3116, sections "Introduction" and "Delegation size at COPs since 2015". [doi-10-14324-111-444-ucloe-3116]
85. Nasiritousi and Linnér, 2016, "Open or closed meetings? Explaining nonstate actor involvement in the international climate change negotiations", International Environmental Agreements 16, 127–144, https://doi.org/10.1007/s10784-014-9237-6, Notes. [google-scholar-lookup-b4b729]
86. InfluenceMap, 2025, "The LobbyMap Methodology", https://lobbymap.org/briefing/LobbyMap-Methodology-24422, sections "Industry Association Selection", "Company Selection", "Table 3" and "About InfluenceMap". [lobbymap-lobbymap-methodology-24422]
87. Nasiritousi, N., 2017, "Fossil fuel emitters and climate change: unpacking the governance activities of large oil and gas companies", *Environmental Politics* 26(4), 621–647, https://doi.org/10.1080/09644016.2017.1320832, pp. 4 and 13. [doi-10-1080-09644016-2017-1320832]
88. Hanegraaff, M., 2023, "When does the structural power of business fade? Assessing business privileged access at global climate negotiations", *Environmental Politics* 32(3), 427–451, https://doi.org/10.1080/09644016.2022.2087353, pp. 10, 11, 14, 21 and 26. [doi-10-1080-09644016-2022-2087353]
89. Hanegraaff, M., 2015, "Transnational Advocacy over Time: Business and NGO Mobilization at UN Climate Summits", *Global Environmental Politics* 15(1), https://doi.org/10.1162/GLEP_a_00273, pp. 8–10. [doi-10-1162-glep-a-00273]
90. Suba, Á., 2025, "Integrity Checklist for National Delegations to COP", Transparency International, https://images.transparencycdn.org/images/Integrity-Checklist-for-National-Delegations-to-COP-Transparency-International.pdf, p. 1. [transparencycdn-integrity-checklist-for-national-delegations-to-cop-tr]
91. Transparency International and co-signatories, 18 March 2025, "Open letter to UNFCCC and Brazilian COP30 leadership to address fossil fuel lobby influence", https://images.transparencycdn.org/images/Transparency-Internationals-Letter-to-UNFCCC-and-COP30-Presidency-on-integrity-reforms-for-undue-influence_signed.pdf, p. 1. [transparencycdn-transparency-internationals-letter-to-unfccc-and-cop30]
92. Kuyper, J.W., Linnér, B.-O. and Schroeder, H., "Non-state actors in hybrid global climate governance: justice, legitimacy, and effectiveness in a post-Paris era", *WIREs Climate Change*, https://doi.org/10.1002/wcc.497, PDF page 6. Authors' manuscript of the journal article; year not given in the copy read. [doi-10-1002-wcc-497]
93. Bergmann, S., 2020, "Non-state actors in the international climate change regulatory framework", *Helsinki Law Review* 14(1), 88–104, https://doi.org/10.33344/vol14iss1pp88-104, PDF pages 2 and 5. [doi-10-33344-vol14iss1pp88-104]
94. van Asselt, H. and Green, F., 2023, "COP26 and the dynamics of anti-fossil fuel norms", *WIREs Climate Change* 14(3), e816, https://doi.org/10.1002/wcc.816, PDF pages 3–4. [doi-10-1002-wcc-816]
95. Desai, D., Si, Y., Bozhilova, D., Puffer, S.M. and Stephens, J.C., 2026, "Renewable energy discourses of fossil fuel companies: obstruction and delay of climate action", *Energy, Sustainability and Society* 16, 13, https://doi.org/10.1186/s13705-026-00565-z, PDF page 7. [doi-10-1186-s13705-026-00565-z]
96. Edwards, G., Gellert, P.K., Faruque, O., Hochstetler, K., McElwee, P.D., Kashwan, P., McKie, R.E., Milani, C., Roberts, J.T. and Walz, J., 2023, "Climate obstruction in the Global South: future research trajectories", *PLOS Climate* 2(7), e0000241, https://doi.org/10.1371/journal.pclm.0000241, PDF page 1. [doi-10-1371-journal-pclm-0000241]
97. Franta, B., 2022, "Weaponizing economics: Big Oil, economic consultants, and climate policy delay", *Environmental Politics* 31(4), 555–575, https://doi.org/10.1080/09644016.2021.1947636, PDF pages 8 and 17. [doi-10-1080-09644016-2021-1947636]
98. Jouty, F. and Bonneuil, C., 2025, "Undermining climate action: the fight by European oil companies against the European carbon tax", *The International History Review*, https://doi.org/10.1080/07075332.2025.2583948, PDF page 4. Authors' manuscript, HAL halshs-05547651, https://shs.hal.science/halshs-05547651v1. [doi-10-1080-07075332-2025-2583948]
99. Green, J., 2023, "The climate establishment and the structural constraints of the Paris partnerships", preprint, Research Square, https://doi.org/10.21203/rs.3.rs-3373795/v1, PDF pages 9 and 11. Not peer reviewed; a later journal version was not read. [springer-s10584-024-03730-5]
100. Törnberg, P., 2023, "How to use large language models for text analysis", preprint, arXiv:2307.13106v1, PDF page 5. Not peer reviewed. [doi-10-4135-9781529683707]
101. Bunt, H.L., Goddard, A., Reader, T.W. and Gillespie, A., 2025, "Validating the use of large language models for psychological text classification", *Frontiers in Social Psychology* 3, 1460277, https://doi.org/10.3389/frsps.2025.1460277, PDF page 9. [doi-10-3389-frsps-2025-1460277]
102. Chae, Y. and Davidson, T., 2025, "Large language models for text classification: from zero-shot learning to instruction-tuning", preprint, SocArXiv, https://doi.org/10.31235/osf.io/sthwk, PDF page 43. Not peer reviewed in the version read. [doi-10-31235-osf-io-sthwk]
103. Nakamura, K., Tan, J.L. and Yean, G., 2026, "Observational equivalence of LLM and human annotation", preprint, arXiv:2609.22133v2, PDF pages 1 and 8. Not peer reviewed. [doi-10-2139-ssrn-7389359]
104. González-Bustamante, B., 2024, "Benchmarking LLMs in political content text-annotation: proof-of-concept with toxicity and incivility data", preprint, arXiv, https://doi.org/10.48550/arXiv.2409.09741, PDF page 8. Not peer reviewed. [doi-10-48550-arxiv-2409-09741]
105. Timoneda, J.C. and Vallejo Vera, S., 2025, "Rolling memory: a new approach to annotation with generative LLMs in social and political research", *Chinese Political Science Review*, https://doi.org/10.1007/s41111-025-00327-w, PDF page 13. [doi-10-1007-s41111-025-00327-w]
106. Grimmer, J. and Stewart, B.M., 2013, "Text as data: the promise and pitfalls of automatic content analysis methods for political texts", *Political Analysis* 21, 267–297, https://doi.org/10.1093/pan/mps028, PDF page 5. [doi-10-1093-pan-mps028]
107. Bonikowski, B., Luo, Y. and Stuhler, O., "Politics as usual? Measuring populism, nationalism, and authoritarianism in U.S. presidential campaigns (1952–2020) with deep neural language models", authors' manuscript, PDF page 31. Year and venue not given in the copy read. [sagepub-00491241221122317]
108. Do, S., Ollion, É. and Shen, R., "The augmented social scientist: using sequential transfer learning to annotate millions of texts with human-level accuracy", *Sociological Methods & Research*, authors' manuscript (stated as forthcoming), PDF page 33. Year not given in the copy read. [sagepub-00491241221134526]
109. Atreja, S., Ashkinaze, J., Li, L., Mendelsohn, J. and Hemphill, L., 2025, "What's in a prompt? A large-scale experiment to assess the impact of prompt design on the compliance and accuracy of LLM-generated text annotations", *Proceedings of the International AAAI Conference on Web and Social Media* 19, 122–145, https://doi.org/10.1609/icwsm.v19i1.35807, PDF page 8. [doi-10-1609-icwsm-v19i1-35807]
110. Burnham, M., 2025, "Stance detection: a practical guide to classifying political beliefs in text", *Political Science Research and Methods* 13, 611–628, https://doi.org/10.1017/psrm.2024.35, PDF pages 6 and 13. [doi-10-1017-psrm-2024-35]
111. Heseltine, M. and Clemm von Hohenberg, B., 2024, "Large language models as a substitute for human experts in annotating political text", *Research & Politics* 11, 1–10, https://doi.org/10.1177/20531680241236239, PDF page 4. [doi-10-1177-20531680241236239]
112. Thalken, R., Stiglitz, E.H., Mimno, D. and Wilkens, M., 2023, "Modeling legal reasoning: LM annotation at the edge of human agreement", *Proceedings of the 2023 Conference on Empirical Methods in Natural Language Processing*, 9252–9265, Association for Computational Linguistics, PDF page 4. [doi-10-18653-v1-2023-emnlp-main-575]
113. UNFCCC secretariat, undated, "How to obtain observer status", UNFCCC website, https://unfccc.int/process-and-meetings/parties-non-party-stakeholders/non-party-stakeholders/overview/how-to-obtain-observer-status, section "FAQ". [unfccc-how-to-obtain-observer-status]
114. Gupta, J. and Allan, J., 2023, *"On Behalf of My Delegation…": A survival guide for new and lonely climate change negotiators*, second edition, International Institute for Sustainable Development, pp. 121, 132 and 70. [gupta-allan-2023-on-behalf-of-my-delegation]
115. UNFCCC secretariat, 2024, "Partnerships with UNFCCC: At a Glance", https://unfccc.int/sites/default/files/resource/UNFCCC_Partnerships_2024.pdf, p. 3. [unfccc-unfccc-partnerships-2024]
116. Martini, M., 2012, "Influence of interest groups on policy-making", U4 Expert Answer 335, U4 Anti-Corruption Resource Centre and Transparency International, pp. 1 and 2. [martini-2012-influence-interest-groups-u4]
117. Năstase, A. and Muurmans, C., 2020, "Regulating lobbying activities in the European Union: a voluntary club perspective", *Regulation & Governance* 14, 238–255, https://doi.org/10.1111/rego.12200, p. 2. [doi-10-1111-rego-12200]
118. Seitz, K. and Martens, J., 2017, "Philanthrolateralism: private funding and corporate influence in the United Nations", *Global Policy* 8, supplement 5, https://doi.org/10.1111/1758-5899.12448, p. 4. [doi-10-1111-1758-5899-12448]
119. Hernández-Aguado, I. and Chilet-Rosell, E., 2018, "Pathways of undue influence in health policy-making: a main actor's perspective", *Journal of Epidemiology and Community Health* 72, 154–159, https://doi.org/10.1136/jech-2017-209677, p. 2. [doi-10-1136-jech-2017-209677]
120. Rasmussen, A. and Reher, S., 2022, "(Inequality in) interest group involvement and the legitimacy of policy making", *British Journal of Political Science*, published online 8 July 2022, https://doi.org/10.1017/S0007123422000242, sections "Introduction" and "Conclusion". [doi-10-1017-s0007123422000242]
121. Li, W. Y., 2023, "Regulatory capture's third face of power", *Socio-Economic Review*, advance article, https://doi.org/10.1093/ser/mwad002, p. 2, note 1 (preprint, submitted version). [doi-10-1093-ser-mwad002]
