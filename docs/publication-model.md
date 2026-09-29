# Public publication model

## Purpose

The public site should let a visitor understand an object before asking the visitor to understand the research system behind it.

The publication contract is progressive disclosure:

**Narrative → citation → evidence → claim provenance → research task**

The internal knowledge graph remains the authoritative structured representation. The publication layer translates that graph for readers; it must not create a second editorial truth system.

## Public-first rule

An ordinary object page should read like a well-sourced museum or encyclopedia entry. Internal assertion IDs, predicate names, transaction IDs, record hashes, effective-root identifiers, and dependency vocabulary are advanced provenance information and should not appear in the default reading path.

A reader should be able to answer who, what, where, and when from the overview. A reader who asks *why do we believe this?* should be able to move one level deeper without leaving the object page.

## Five public epistemic states

Public states are derived presentations of the underlying graph, not manually maintained confidence judgments.

### Documented

Direct documentary or observational evidence supports the proposition within the scope and date of that evidence.

`Documented` does not mean universally or permanently true. A document can itself be erroneous, and later evidence can create a conflict.

### Attributed

A named source or scholar makes the proposition, but the publication should preserve that attribution rather than present the proposition as an unqualified fact.

### Disputed

Material credible sources conflict about the proposition. The public page should state the disagreement and attribute the competing accounts rather than silently choose one.

### Unresolved

Available evidence does not establish an answer, or source relationships prevent a stronger conclusion.

`Not identified by this source` must not be silently converted into `historically unknown`.

### Research needed

A bounded unresolved question has a defined next research action. This state is a collaboration opportunity, not a synonym for missing data.

## No numerical confidence scores

The publication must not display pseudo-precise confidence percentages or scores. The current architecture does not provide an empirically calibrated probability model, and source count is not a proxy for epistemic independence.

Prefer statements such as:

- `2 publications · source independence unresolved`
- `3 publications · 1 known evidence lineage`
- `Sources disagree`
- `Documentary root not yet established`

## Public vocabulary

| Internal concept | Default public language |
| --- | --- |
| assertion | claim |
| assertion_evidence | evidence |
| PRIMARY_SUPPORT | main source |
| CORROBORATION | additional source |
| QUALIFIES | qualification |
| dependency_status unknown | source relationship not yet known |
| effective claim root | underlying evidence |
| inherits_claim_from | draws this claim from |
| interpretation_note | research note |
| source lineage / claim lineage | provenance |
| research_task | open question / research task |

The exact internal vocabulary may remain available in a technical provenance view.

## Information architecture

The default object page has five primary sections.

### Overview

Human-readable object history with ordinary inline citation markers. This is the default reading experience.

### Evidence

Claim-level evidence. Selecting a citation should reveal the source, locator, role of that source, qualifications, disagreements, and a compact source-independence statement.

Suggested disclosure pattern:

> **Evidence for this claim**
>
> **[Source title]**  
> Main source · [page/section/record locator]
>
> **[Second source]**  
> Additional source
>
> **2 publications · source independence unresolved**
>
> `View provenance`

### Sources

Human-readable bibliography/document inventory. Repository custody, institutional authorship, and documentary origin should remain distinguishable.

### Open questions

Bounded unresolved research questions written so that a visitor can understand what is needed without knowing the ontology or GitHub workflow.

### Provenance

Advanced view of claim ancestry, source inheritance, evidence roles, effective roots, transactions, and technical identifiers.

## Source count is not corroboration

The public interface must not imply that three citations equal three independent confirmations.

Where independence is unresolved, say so. Where multiple publications are known to descend from one documentary or claim root, expose that fact.

The signature public interaction should make it possible to discover:

> This statement appears in several authoritative publications, but some may derive from the same underlying evidence.

This distinction is more important than displaying a raw source count.

## Institutional authority is claim-specific

A source is not globally `strong` or `weak`. Its evidentiary value depends on the proposition.

For example, a dated photograph may be strong evidence of an object's physical appearance at that date while providing no evidence for a claimed event decades earlier. An institutional catalog can be useful evidence while still containing inherited or erroneous historical assertions.

The public UI should therefore describe what a source supports rather than assign a global authority score.

## External records are not automatically evidence

External identifiers and records support interoperability and discovery. They do not automatically support every proposition about an object.

Keep a visible distinction between:

**External records** — Smithsonian, NPS, Library of Congress, Wikidata, Wikipedia/Wikimedia, national authority records, and other identity/discovery links.

**Evidence used here** — sources actually connected to specific claims in this project's evidence graph.

Adding an external identifier must not change an assertion's evidentiary status.

## Collaboration model

Public collaboration uses progressive disclosure too.

### Quick contribution

A visitor sees a concrete request in ordinary language, for example:

> **Can you access this book?**
>
> We need pp. 443–444 of James M. Goode's *The Outdoor Sculpture of Washington, D.C.* (1974) to determine where several later accounts of the Artigas memorial originated.

The visitor should not need to understand claim IDs or source-inheritance terminology.

### Research contribution

A researcher can open a fuller task explaining the historical question, known source chain, expected locators, and epistemic constraints.

### Technical contribution

GitHub exposes claim matrices, IDs, JSON structures, transactions, validators, and source-inheritance mechanics.

GitHub is research infrastructure, not the required first interface for public participation.

## Art-historical modes

A later publication phase may distinguish three internal epistemic modes:

- `DOCUMENTARY_FACT`
- `ATTRIBUTION_RECONSTRUCTION`
- `INTERPRETATION`

Public language should normally be **Historical record**, **Attribution**, and **Interpretation**.

These modes must not function as confidence scores.

Documentary claims may be presented as documented when evidence warrants it. Attribution/reconstruction claims should preserve competing hypotheses and named attributions. Interpretive claims should ordinarily remain attributed arguments and must not acquire a mechanical `verified` presentation merely because several publications repeat them.

## Artigas vertical-slice requirement

OBJ-0001 is the publication UX test object. Do not generalize the new interface to the other alpha objects until Artigas demonstrates the complete path:

1. readable narrative;
2. familiar citations;
3. evidence disclosure;
4. source-independence disclosure;
5. open research questions;
6. advanced provenance.

No fourth object is needed to test this model.

## Usability gate

Before replication, test the Artigas page with at least three reader perspectives:

1. ordinary visitor — `What is this monument?`
2. researcher/art historian — `Why is this attribution made?`
3. potential contributor — `What can I help establish?`

After using the page, each should be able to explain:

- what is known;
- what remains uncertain;
- why a principal claim is supported; and
- what contribution would materially advance the research.

Passing this test should not require the reader to understand `effective claim root`, transaction hashes, or internal predicate IDs.

## Publication invariants

1. Publication never overwrites or bypasses the transaction-ledger knowledge architecture.
2. Public status is derived from evidence and provenance, not maintained as a competing truth field.
3. Source quantity never substitutes for source independence.
4. Institutional custody never substitutes for claim origin.
5. Uncertainty is surfaced rather than silently normalized.
6. Interpretive scholarship is attributed rather than mechanically verified.
7. Collaboration requests expose bounded questions before exposing technical machinery.
8. The object remains the primary subject of the page; the epistemic architecture becomes visible when the reader asks for evidence.