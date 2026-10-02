# Working Definition and Classification Criteria

**Criteria version:** 0.9  
**Status:** candidate criteria; not stable until boundary cases pass  
**Scope:** global; Washington, D.C. is the first research node, not part of the definition.

## Purpose

This repository studies objects associated with diplomatic gift-giving and foreign-sponsored public commemoration. It does not assume that an object is a diplomatic gift because it is foreign-themed, was authorized by government, stands on public land, or is described informally as a gift.

Classification is a **derived research conclusion**. The underlying facts are represented as independently sourced role, financing, transfer, placement, occasion, and lifecycle claims. A classification must identify the version of these criteria used to derive it.

## Working definition

For this project, a **diplomatic gift** is an object transferred as a gift rather than by sale or contractual exchange, in a transaction or presentation connected to relations between political communities, where sufficiently supported evidence establishes (1) a foreign polity or its authorized representative as presenter or transferor and (2) acceptance of the object from that foreign counterparty by the recipient side. Reciprocity expected in diplomatic practice does not disqualify a gift; documented contractual consideration or purchase by the recipient does.

The definition deliberately separates three questions that are often collapsed in public descriptions:

1. **Who financed or supplied the object?**
2. **Who presented or transferred it, and to whom?**
3. **Who accepted it, and who separately authorized its placement, custody, or display?**

Evidence for one role does not establish another. In particular, domestic legislation or agency approval authorizing placement does not by itself establish acceptance of a diplomatic gift.

## Terms

### Foreign

`foreign` is evaluated relative to the recipient political community in the transaction being classified. It does not mean merely foreign-born, foreign-themed, or located abroad.

### Polity

A `polity` is a sovereign state or another public political entity capable of acting in an official intergovernmental relationship under the evidence for the case. A municipality may therefore be a polity for a documented sister-city or other official municipal exchange. Private associations, diaspora groups, corporations, foundations, artists, and informal committees are not polities merely because they represent a national or local identity.

International organizations are not silently treated as foreign polities. Gifts to or from an international organization require the relevant organization to be modeled explicitly; until criteria for that relationship are adopted, such a case is `undetermined` unless another rule clearly resolves it.

### Authorized representative

An `authorized representative` is a person or body evidenced as acting officially for the polity in the relevant transaction. Office, nationality, inscription, or affiliation alone does not prove authorization for the transaction.

## Role families

### 1. Financing / attribution

Evidence may establish that an actor:

- funded the object (`FUNDED_BY`); or
- was attributed as donor (`DONOR_ATTRIBUTION`).

These claims describe important participation but **do not by themselves satisfy the official giver/presenter element of `core`**. Financing alone is not presentation; donor attribution alone is not proof of transfer.

### 2. Presentation / transfer

Evidence may establish that an actor:

- formally presented the object (`PRESENTED_BY`); or
- transferred title or otherwise supplied the object as a gift.

For `core`, the presenter/transferor must be a foreign polity or its authorized representative. A domestic intermediary may participate in delivery, installation, or ceremony without replacing the evidenced foreign presenter/transferor.

### 3. Recipient / acceptance

`ACCEPTED_FROM` records evidence that the recipient side accepted the object **from a named source counterparty**. For `core`, that source counterparty must be the same foreign polity or authorized representative established on the presentation/transfer side, or be explicitly linked to that side by supported evidence.

A generic recipient claim, possession, custody, domestic authorization, site approval, maintenance responsibility, dedication attendance, or placement on public land does **not** satisfy this element.

Where evidence establishes legal ownership, the repository preserves that fact separately from physical custody. CIDOC CRM likewise distinguishes acquisition/legal ownership from transfer of custody.

### 4. Placement / authorization

`AUTHORIZED_PLACEMENT` records authority for installation or display at a place. It can be important to an object's public history without proving that the authorizing actor received, accepted, funded, or presented the object.

## Gift framing

Gift framing records evidence that a source characterizes a transfer or presentation as a gift, donation, offering, presentation, or equivalent concept. Gift framing is evidence, not the final diplomatic classification.

Getty AAT `300417701`, **gifts (object genre)**, describes objects transferred from one party to another without expectation or receipt of an equivalent. Getty AAT `300233979`, **presentation pieces**, describes objects intended to be given as gifts or on special occasions, often inscribed with information about the giver, recipient, or occasion. Either may be useful as an object-level vocabulary anchor where appropriate; neither establishes diplomatic context or proves that a historical transfer occurred.

## Financing

Financing is modeled independently because a government, private committee, diaspora organization, artist, foundation, or mixed group may pay for an object without being the diplomatic presenter or legal donor. Unknown or disputed financing must remain unknown or disputed rather than being inferred from nationality or inscription.

Recipient financing is especially material: where sufficiently supported evidence establishes that the purported recipient purchased or commissioned the object for contractual consideration, the object is not a gift under these criteria.

## Occasion and reciprocity

An object may be associated with a state visit, anniversary, independence commemoration, bilateral celebration, exposition, memorial campaign, or another occasion. Occasion is descriptive context and does not itself establish gift status.

`reciprocal_of` may link documented paired or reciprocal gifts. Diplomatic reciprocity—an expectation that a gift, courtesy, or relationship may later be reciprocated—does not itself turn the transaction into a sale or contractual exchange. A reciprocal link must be evidenced; chronological proximity or thematic similarity is insufficient.

## Lifecycle

Subsequent installation, dedication, relocation, removal, storage, restoration, transfer of custody, transfer of title, or loss is represented as lifecycle events. A later relocation or authorization does not rewrite the evidence for the original transaction.

## Assertion threshold used by classification

A role or fact counts toward classification only when its materialized assertion status is `verified` or `supported`.

- `verified` and `supported` claims may count.
- unresolved, contradicted, disputed, pending, or otherwise non-qualifying claims do not count.
- if a role required for a positive class has a material unresolved contradiction, that role does not count and the classification must be `undetermined` unless independent qualifying evidence resolves the contradiction.

The validator must use the repository's canonical machine-readable status vocabulary; this document does not authorize aliases that differ from that vocabulary.

## Classification statuses

Every object receives exactly one computed status under a stated criteria version.

### `core`

Use only when **all** of the following are satisfied by qualifying assertions:

1. gift framing or evidence establishes transfer/presentation as a gift rather than sale or contractual exchange;
2. a foreign polity or its authorized representative is established as presenter or transferor;
3. the recipient side has a qualifying `ACCEPTED_FROM` relationship naming that foreign presenter/transferor (or an explicitly evidenced linked representative) as source counterparty; and
4. no unresolved material contradiction defeats elements 1–3.

This is deliberately stricter than an “any one official role” rule. Funding, placement authorization, diplomatic attendance, or official sponsorship alone cannot produce `core`.

### `periphery`

Use only when all of the following are satisfied:

1. the object is sufficiently evidenced as part of an official cross-polity commemorative or cultural-diplomatic project;
2. at least one polity or authorized representative has a qualifying official role in the object's commissioning, financing, presentation, acceptance, or authorized placement;
3. the evidence affirmatively establishes that the relationship is **not a completed diplomatic gift satisfying `core`**; and
4. the case is not merely missing evidence needed to decide whether `core` applies.

Examples that can satisfy these conditions include a recipient-government-paid commission undertaken as an official bilateral commemorative project, or an official cross-polity monument project explicitly structured as sponsorship/commission rather than a gift.

If transfer mechanics or acceptance are merely unknown, use `undetermined`, not `periphery`.

### `excluded`

Use when qualifying evidence affirmatively establishes that the object is outside both `core` and `periphery`. Excluded cases include:

- purely domestic monuments with no evidenced official cross-polity relationship;
- private or diaspora gifts with no qualifying official polity role;
- ordinary recipient-paid commissions with no qualifying cross-polity diplomatic/commemorative project;
- objects never transferred or presented as gifts and lacking the official relationship required for `periphery`;
- war booty or spoils;
- compulsory tribute or coerced transfers; and
- purported gift histories affirmatively contradicted by stronger qualifying evidence where no periphery rule applies.

### `undetermined`

Use when available evidence is insufficient to derive `core`, `periphery`, or `excluded`, or when a decisive role, counterparty, financing fact, transfer fact, or contradiction remains unresolved.

`undetermined` is the required status for unresolved cases. Absence of evidence must not be converted into a positive classification.

## Boundary cases for validator tests

These are normative examples for criteria 0.9. They should become executable fixtures before promotion to 1.0.

| Case | Expected class | Reason |
|---|---|---|
| Foreign government presents an object as a gift; recipient acceptance from that government is supported | `core` | Gift framing + official foreign presentation + evidenced acceptance |
| Foreign government funds an object, but presenter/transferor and acceptance are unknown | `undetermined` | Funding does not satisfy presentation; missing facts cannot become periphery |
| Foreign government presents an object through a domestic logistics intermediary; recipient acceptance from the foreign government is supported | `core` | Intermediary does not break the evidenced transaction |
| Recipient government pays a foreign government or state workshop to produce a monument under an official bilateral commemorative project | `periphery` | Official cross-polity project, but recipient purchase defeats gift status |
| Recipient pays an ordinary commercial artist abroad; no official foreign polity role | `excluded` | Foreign origin is not diplomacy |
| Private diaspora association gives a monument; no polity or authorized representative has a qualifying official role | `excluded` | Private national identity does not establish state action |
| Sister city officially presents a gift and the recipient municipality accepts it | `core` | Municipal polities can participate in documented official exchange |
| International organization presents an object and no adopted rule resolves its polity status | `undetermined` | International-organization boundary is explicitly unresolved |
| Legislature authorizes placement of a foreign-themed monument; no evidence of foreign presentation or acceptance | `undetermined` | Placement authorization cannot establish gift transaction; absence does not prove exclusion |
| Object is seized as war booty and later displayed publicly | `excluded` | Coercive acquisition is not gift exchange |
| Tribute is compulsory rather than voluntarily gifted | `excluded` | Coercive/obligatory transfer is outside gift framing |
| Source calls object a gift, but credible evidence materially contests whether the foreign polity presented it | `undetermined` | Contested required role does not count |

## Derivation principles

1. **Facts first, classification second.** No assertion type should encode `DIPLOMATIC_GIFT_FROM` or otherwise assert the final class directly.
2. **No role inheritance.** Funding, presenting, accepting, authorizing placement, owning, and holding custody are not interchangeable.
3. **No nationality inference.** An artist's, donor's, committee's, or subject's nationality does not establish state action.
4. **No placement inference.** Presence on federal, municipal, embassy, or other public land does not establish gift acceptance.
5. **No inscription-only leap.** An inscription is evidence of what the inscription says; its historical claims require corroboration where material to classification.
6. **Contradiction blocks the affected role.** A materially contested required role does not count until qualifying evidence resolves the contradiction; where that role is decisive, classify `undetermined`.
7. **Criteria are versioned.** A change to these rules creates a new criteria version; historical classifications remain reproducible.

## External standards and limits

### UNESCO

UNESCO's 1970 Convention, Article 1, defines cultural property for purposes of that Convention. Article 4(d) separately refers to cultural property subject to freely agreed exchange, and Article 4(e) to cultural property received as a gift or legally purchased with the consent of competent authorities of the country of origin. These provisions are useful contextual anchors for cultural-property exchange and gifts; they do **not** define this project's diplomatic-gift classification.

Source: UNESCO, *Convention on the Means of Prohibiting and Preventing the Illicit Import, Export and Transfer of Ownership of Cultural Property* (Paris, 14 November 1970), arts. 1, 4(d)–(e).

### CIDOC CRM

CIDOC CRM is an event-centric cultural-heritage model. Its `E8 Acquisition` models changes in legal ownership, with properties for title transferred to, from, and of an object. CIDOC CRM separately models physical custody. The repository should align transfer events with those concepts where the evidence supports legal ownership or custody, while retaining project-specific diplomatic roles where CIDOC CRM does not express the research question directly.

Source to verify before criteria 1.0: CIDOC CRM current specification and E8 Acquisition documentation.

### Getty vocabularies

- Getty AAT `300417701`: **gifts (object genre)** — generic object-genre anchor for objects transferred without expectation or receipt of an equivalent.
- Getty AAT `300233979`: **presentation pieces** — potentially useful for objects intended as gifts or for special occasions, especially inscribed presentation objects.

Neither term proves diplomatic context. A dedicated Getty AAT concept for **diplomatic gifts** has not been established by this project; do not invent an identifier.

Sources: Getty Research Institute, Art & Architecture Thesaurus, full records for AAT 300417701 and 300233979.

## Scholarly basis

The operational model treats diplomatic gift-giving as an event and relationship involving actors, political context, selection, presentation, reception, and subsequent object history, rather than as an intrinsic nationality-based object type.

**Citation gate:** criteria 0.9 intentionally does not claim a settled scholarly definition. Before promotion to 1.0, add named scholarly works supporting the operational distinctions used here and test the criteria against counterexamples from the expanded corpus.

## Public governance note

Classification changes are versioned and should remain reproducible from the underlying evidence and criteria version. Reviewer identity, review records, and provenance are represented in the repository's public research lifecycle where appropriate. Internal administrative or ethics-review processes are not part of this public definition.

## Version history

### 0.9

Candidate criteria after alpha review. Makes `core` explicitly require both official foreign presentation/transfer and evidenced recipient acceptance; converts `periphery` to checkable conditions; distinguishes diplomatic reciprocity from contractual consideration; defines `foreign`, `polity`, and qualifying evidence; adds explicit exclusions and boundary cases; corrects the UNESCO anchor; adds Getty AAT presentation pieces; and removes internal ethics-process language from the public definition.
