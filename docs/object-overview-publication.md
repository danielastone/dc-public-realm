# Object overview publication standard

Each public object record begins with a conventional cultural-catalog orientation layer: a documentary photograph, current location, relevant presentation/dedication history, and a short subject biography or object context. This layer reduces the learning curve before readers enter the claim-level provenance record.

## Epistemic boundary

The overview improves legibility, not certainty. It does not assign an overall confidence status and does not change assertion statuses. Disputed details stay in the assertion/evidence layer rather than being simplified into the overview. Location, event history, biography/context, and image rights may use different sources because they answer different questions.

## Images and rights

Use a documentary image only when object identity and reuse rights are sufficiently established. Prefer sources such as Wikimedia Commons when the individual file record makes creator and license terms explicit. Record and display creator/credit, exact license or public-domain basis, license URL when applicable, and the source-record URL. Access to an image is not permission to republish it.

The primary photograph is for object identification, not historical proof. If a photograph later supports a claim such as an inscription, material feature, condition, or location, add a separate evidence relationship for that assertion.

Do not use generic stock imagery or generated reconstructions as substitutes for documentary photographs of real cataloged objects. Keep alt text descriptive of the depicted object; keep rights information in the visible caption.

## Record types

`person_memorial` records include a subject name, dates, and concise sourced biography. `historical_object` records use object context instead of manufacturing a person-style Subject field. Event labels preserve the semantics of the source: dedication, rededication, presentation, relocation, and installation are not interchangeable.

## Publication integrity

`data/object-overviews.json` is canonical; generated HTML is disposable. Correct structured data and regenerate rather than patching generated pages. CI validates overview completeness, image rights metadata, image provenance URLs, rendered record heads, and the existing assertion-status publication consistency checks.

## Current alpha scope

The alpha covers Artigas, San Martín, and the Cuban-American Friendship Urn. Artigas uses an NPS public-domain photograph via its Commons file record. San Martín uses a CC BY-SA 3.0 Commons photograph credited to AgnosticPreachersKid. The Cuban-American Friendship Urn uses a CC BY-SA 4.0 Commons photograph credited to AgnosticPreachersKid.

Further schema or presentation expansion should be driven by a demonstrated research, accessibility, collaboration, or performance need rather than by available metadata alone.
