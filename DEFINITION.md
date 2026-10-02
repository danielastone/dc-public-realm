# Working Definition and Classification Criteria

**Criteria version:** 1.0  
**Status:** working definition for repository classification  
**Scope:** global; Washington, D.C. is the first research node, not part of the definition.

## Purpose

This repository studies objects associated with diplomatic gift-giving and foreign-sponsored public commemoration. It does not assume that an object is a diplomatic gift because it is foreign-themed, was authorized by government, stands on public land, or is described informally as a gift.

Classification is a **derived research conclusion**. The underlying facts are represented as independently sourced role, financing, transfer, placement, occasion, and lifecycle claims. A classification must identify the version of these criteria used to derive it.

## Working definition

For this project, a **diplomatic gift** is an object transferred without an expected equivalent in return, in a transaction or presentation connected to relations between political communities, where credible evidence establishes a foreign polity or its authorized representative in the giver/presenter side of the transaction and establishes a recipient or accepting counterparty on the other side.

The definition deliberately separates three questions that are often collapsed in public descriptions:

1. **Who financed or supplied the object?**
2. **Who presented or transferred it, and to whom?**
3. **Who authorized its placement, custody, or display?**

Evidence for one role does not establish another. In particular, domestic legislation or agency approval authorizing placement does not by itself establish acceptance of a diplomatic gift.

## Three role families

### 1. Giver / presentation role

Evidence may establish that an actor:

- funded the object (`FUNDED_BY`);
- was attributed as donor (`DONOR_ATTRIBUTION`);
- formally presented the object (`PRESENTED_BY`); or
- transferred title or otherwise supplied the object as a gift.

These are distinct claims. Financing alone is not presentation; donor attribution alone is not proof of legal transfer.

### 2. Recipient / acceptance role

`ACCEPTED_FROM` records evidence of acceptance in a gift relationship. For this project's diplomatic classification, the counterparty recorded as the source of that acceptance must be a **foreign polity or its authorized representative**. Domestic authorization, site approval, maintenance responsibility, or custody does not satisfy this role.

Where evidence establishes legal ownership, the repository should preserve that fact separately from physical custody. CIDOC CRM likewise distinguishes acquisition/legal ownership from transfer of custody.

### 3. Placement / authorization role

`AUTHORIZED_PLACEMENT` records authority for installation or display at a place. It can be important to an object's public history without proving that the authorizing actor received, accepted, funded, or presented the object.

## Gift framing

The repository uses **gift framing** to record evidence that a source characterizes a transfer or presentation as a gift, donation, offering, or equivalent concept. Gift framing is evidence, not the final diplomatic classification.

The Getty Art & Architecture Thesaurus defines the object genre “gifts” as objects transferred from one party to another without expectation or receipt of an equivalent. The project adopts that non-reciprocity concept as a useful vocabulary anchor, while treating diplomatic context as a separate evidentiary question.

## Financing

Financing is modeled independently because a government, private committee, diaspora organization, artist, foundation, or mixed group may pay for an object without being the diplomatic presenter or legal donor. Unknown or disputed financing must remain unknown or disputed rather than being inferred from nationality or inscription.

## Occasion and reciprocity

An object may be associated with a state visit, anniversary, independence commemoration, bilateral celebration, exposition, memorial campaign, or another occasion. Occasion is descriptive context and does not itself establish gift status.

`reciprocal_of` may link documented paired or reciprocal gifts. Reciprocity must be evidenced; chronological proximity or thematic similarity is insufficient.

## Lifecycle

Subsequent installation, dedication, relocation, removal, storage, restoration, transfer of custody, transfer of title, or loss is represented as lifecycle events. A later relocation or authorization does not rewrite the evidence for the original transaction.

## Classification statuses

Every object receives exactly one computed status under a stated criteria version.

### `core`

Use when the evidence supports all of the following:

1. credible gift framing or evidence of a non-reciprocal transfer/presentation;
2. a foreign polity or its authorized representative is evidenced on the giver/presenter side;
3. a recipient/accepting counterparty is evidenced on the other side; and
4. the evidence is sufficiently supported under the repository's assertion-status rules to make the classification without relying on unresolved inference.

### `periphery`

Use when the object is demonstrably part of diplomatic or state-to-state cultural exchange but does not satisfy every `core` element. Examples may include foreign-state-funded public monuments presented through domestic intermediaries, commemorative projects with strong diplomatic sponsorship but unclear transfer mechanics, or other documented cultural-diplomatic objects adjacent to gift exchange.

`periphery` is not a lower-confidence substitute for `core`; it describes a different evidentiary relationship.

### `excluded`

Use when sufficient evidence affirmatively shows that the object falls outside the working definition and the project's defined periphery. Examples include a purely domestic monument with no evidenced foreign diplomatic role, or an object whose supposed gift history is contradicted by stronger evidence.

### `undetermined`

Use when available evidence is insufficient to derive `core`, `periphery`, or `excluded`, including when a decisive role, counterparty, financing fact, or transfer fact remains unresolved.

`undetermined` is the required status for unresolved cases; absence of evidence must not be converted into a positive classification.

## Derivation principles

1. **Facts first, classification second.** No assertion type should encode `DIPLOMATIC_GIFT_FROM` or otherwise assert the final class directly.
2. **No role inheritance.** Funding, presenting, accepting, authorizing placement, owning, and holding custody are not interchangeable.
3. **No nationality inference.** An artist's, donor's, committee's, or subject's nationality does not establish state action.
4. **No placement inference.** Presence on federal, municipal, embassy, or other public land does not establish gift acceptance.
5. **No inscription-only leap.** An inscription is evidence of what the inscription says; its historical claims require corroboration where material to classification.
6. **Contradiction is preserved.** Conflicting credible sources remain visible and can force `undetermined` status.
7. **Criteria are versioned.** A change to these rules creates a new criteria version; historical classifications remain reproducible.

## External standards and limits

### UNESCO

UNESCO's 1970 Convention provides a useful international anchor for the broad concept of **cultural property**: property specifically designated by a state as important for archaeology, prehistory, history, literature, art, or science within enumerated categories. This project uses that framework only as contextual grounding for cultural objects. The Convention does **not** define this project's diplomatic-gift classification and should not be treated as doing so.

### CIDOC CRM

CIDOC CRM is an event-centric cultural-heritage model. Its `E8 Acquisition` models changes in legal ownership, with properties for title transferred to, from, and of an object. CIDOC CRM separately models physical custody. The repository should align transfer events with those concepts where the evidence supports legal ownership or custody, while retaining project-specific diplomatic roles where CIDOC CRM does not express the research question directly.

### Getty vocabularies

Getty AAT contains the concept `gifts (object genre)` (AAT 300417701), defined around transfer without expected equivalent. This is a useful external identifier for gift framing. No project classification should assume that Getty's generic gift concept establishes diplomatic context.

A dedicated Getty AAT concept for **diplomatic gifts** has not been established by the project's initial terminology check. Until a specific authoritative identifier is verified, do not invent one; record the generic gift concept plus project-specific diplomatic evidence instead.

## Scholarly basis

The research model follows the historical literature's treatment of diplomatic gifts as objects whose meaning depends on actors, political relationships, selection, presentation, ceremony, and reception—not merely the object's nationality or later location. For example, scholarship discussed by the Getty on Greek antiquities presented as state gifts to U.S. presidents emphasizes government selection, presentation, ceremony, and political messaging. Such scholarship supports modeling diplomatic gift-giving as an event and relationship rather than as an intrinsic object type.

This document is intentionally a working operational definition, not a claim that scholarship has one universally accepted definition of “diplomatic gift.” As the corpus expands globally, counterexamples should be used to revise the criteria explicitly rather than silently stretching classifications.

## Governance

- Daniel is the sole reviewer during the current alpha.
- Self-reviewed changes must be identified as such in the review record once that type is implemented.
- The ethics gate remains in force for steward outreach and downstream agency notices.
- Ordinary archival research may proceed.
- Classification changes must be produced through the repository's transaction/provenance lifecycle rather than baseline edits once migration machinery is in place.

## Version history

### 1.0

Initial criteria version. Establishes the four statuses (`core`, `periphery`, `excluded`, `undetermined`); separates financing, presentation, acceptance, and placement roles; makes classification derived; and records UNESCO, CIDOC CRM, and Getty AAT as external anchors with explicit limits.
