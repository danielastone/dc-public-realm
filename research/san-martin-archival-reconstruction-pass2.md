# San Martín archival reconstruction — pass 2

Reviewed: 2026-09-28

## Purpose

Move the San Martín record backward from later heritage summaries toward contemporaneous web-accessible records. This pass does not promote findings into canonical assertions merely because they are plausible. It records what each source can establish and, separately, what remains a source-genealogy problem.

## 1. Congressional chain: the diplomatic offer predates the 1925 ceremony

The Congressional Record for February 13, 1924 prints President Calvin Coolidge's transmittal to Congress. Coolidge states that he is forwarding a Secretary of State letter informing him of a gift by the people of Argentina to the United States of an equestrian statue of General San Martín and requesting legislation authorizing erection in Washington.

Source: https://www.congress.gov/68/crecb/1924/02/13/GPO-CRECB-1924-pt3-v65-5.pdf

Epistemic use:
- strong contemporaneous evidence that the executive branch represented the offer to Congress as a gift from the people of Argentina;
- strong evidence that a Secretary of State letter existed upstream of the presidential transmittal;
- not independent evidence of the underlying Argentine diplomatic communication, because the presidential message expressly derives the information from State.

Research implication: locate the Secretary of State letter and, if possible, the Argentine diplomatic note to which it responded. These are candidate RG 59 roots.

## 2. Commission of Fine Arts record exposes a site disagreement

A federal Commission of Fine Arts publication, *Monuments, Statues, and Portraits*, records that citizens of Argentina offered, and Congress accepted, a copy of the equestrian statue in Buenos Aires. It says CFA was asked to advise on location; CFA recommended Massachusetts Avenue and Eleventh Street, regarded Judiciary Square as inappropriate, and its recommendation was not followed.

Source: https://www.govinfo.gov/content/pkg/GOVPUB-FA-854443ffd59ff55f34dd3772b9153d82/pdf/GOVPUB-FA-854443ffd59ff55f34dd3772b9153d82.pdf

Epistemic use:
- this is materially stronger than a modern location summary for reconstructing the planning decision;
- it establishes that the final Judiciary Square placement should not be modeled as a simple CFA-selected site;
- it creates a new archival target: the underlying CFA minutes/correspondence/site recommendation in RG 66.

Do not infer from this publication alone who overrode the CFA recommendation or why.

## 3. LOC contemporary photograph: ceremony and physical state

The Library of Congress catalog has a National Photo Company photograph titled `President Coolidge at unveiling of San Martin Statue, 10-28-25`, LCCN 2016841087, dated October 28, 1925.

Canonical catalog target: https://www.loc.gov/pictures/item/2016841087/

Epistemic use:
- contemporaneous image evidence for the dedication event and the monument's 1925 physical configuration;
- catalog metadata and depicted content must be represented separately;
- the image is not evidence of sculptor attribution merely because later cataloging associates it with the San Martín monument.

This is a priority candidate for the historical-image provenance dataset.

## 4. LOC presidential speech: presentation and acceptance are directly contemporaneous

LOC preserves the Government Printing Office version of Coolidge's October 28, 1925 dedication address in the Everett Sanders Papers. The speech says the Argentine ambassador had spoken on behalf of his government and people; later Coolidge says the country that gave San Martín to the cause of freedom was presenting the statue to the U.S. government, and he expressly accepts it on behalf of the government and people of the United States.

Source: https://www.loc.gov/item/mss38893_07/

Epistemic use:
- direct contemporaneous evidence of U.S. acceptance at the ceremony;
- direct evidence of Coolidge's characterization of the diplomatic presentation;
- not proof that every donor label used in later inventories (`people`, `citizens`, `government`) is semantically interchangeable.

The donor ontology should therefore preserve wording and speaker rather than normalize all variants into a single actor prematurely.

## 5. Later HALS is explicitly derivative for relocation details

LOC's HALS DC-68 states that the statue was dedicated October 28, 1925 at Judiciary Square; disassembled in 1970 because of Metro construction; and relocated to Reservation 106 in 1976. Crucially, its footnotes for the disassembly/relocation history point to the National Register nomination.

Source: https://tile.loc.gov/storage-services/master/pnp/habshaer/dc/dc1200/dc1246/data/dc1246data.pdf

Epistemic consequence:
- HALS and the NRHP nomination must not count as independent corroboration for those facts;
- encode HALS as derivative of the NRHP record for claims explicitly sourced to it;
- HALS remains independently useful where it contributes its own field documentation or separately sourced material.

This is the concrete example the project's dependency model needed: institutional independence is not evidentiary independence.

## 6. Newspaper evidence: syndication must be modeled

International newspaper results from October 29–30, 1925 report the Washington ceremony using substantially similar event framing. At least one identifies its feed as an Australian/New Zealand cable association. Such stories should not be counted as multiple independent witnesses merely because they appeared in different newspapers.

Example: https://paperspast.natlib.govt.nz/newspapers/STEP19251029.2.24

Research rule:
- newspaper title is not the source family;
- capture byline/wire/cable attribution when available;
- stories with common wire ancestry share a source_family_id;
- a local Washington reporter's independently reported story can be a different root only if the text/byline supports that conclusion;
- unattributed similarity = dependency_status UNKNOWN, not INDEPENDENT.

## 7. Attribution conflict remains open

This pass does not resolve Daumas versus Dumont.

The U.S. documentary tradition repeatedly uses Dumont, including period federal material. Argentine official sources identify Louis-Joseph Daumas as author of the Buenos Aires original. A contemporaneous U.S. statement proves a contemporaneous U.S. attribution; it does not prove the attribution's art-historical correctness.

New research question: what source supplied `Dumont` to State, Congress, CFA, or the monument's physical inscription/dedication materials?

Priority search order:
1. RG 59 State Department diplomatic correspondence / Argentine note and enclosures;
2. RG 66 CFA minutes, correspondence, photographs, drawings, or submitted monument documentation;
3. 1925 dedication pamphlet and inscriptions;
4. Argentine government correspondence or fabrication records;
5. independent contemporary newspaper reporting, with wire genealogy recorded.

## 8. Proposed evidence graph

```text
Argentine diplomatic note ?
        |
        v
State Department letter (RG 59 target)
        |
        +--> Coolidge transmittal --> Congress / authorization
        |
        +--> dedication planning ?

CFA submission / correspondence (RG 66 target)
        |
        +--> site recommendation: Massachusetts Ave & 11th
        +--> Judiciary Square objection

1925 dedication event
        +--> LOC National Photo Company image
        +--> Coolidge GPO speech
        +--> dedication pamphlet
        +--> newspaper reports -- group by wire/reporting lineage

NPS administrative files ?
        |
        +--> NRHP nomination
                 |
                 +--> HALS relocation narrative
```

Question marks denote unresolved source roots, not missing facts.

## Next gate

Do not add another modern summary source. The next useful evidence is an upstream record that answers at least one of these:

- What exactly did Argentina offer, and how was authorship described in the original diplomatic paperwork?
- What documentation did CFA receive with the proposed monument?
- Why was Judiciary Square selected despite CFA's stated objection?
- Does the 1925 dedication pamphlet identify sculptor/caster/origin, and if so, what is the provenance of that wording?
- Can a contemporary newspaper account be demonstrated to be independently reported rather than wire-derived?
