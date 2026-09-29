---
name: archive-collaboration-planner
description: Convert explicit epistemic defects in the provenance graph into bounded archival research and collaborator tasks. Use to prioritize archive requests, newspaper searches, government-record retrieval, local collaborator work, and source-root tracing without allowing task completion itself to change historical claims.
---

# Archive collaboration planner

Read `../epistemic-core/SKILL.md` and `../epistemic-source-audit/SKILL.md` first.

## Principle
Collaboration is evidence acquisition, not distributed truth assignment. Generate tasks from defects in the current epistemic graph, not from a generic list of archives or interesting topics.

## Defect taxonomy
Classify the target defect using one or more:
- SINGLE_LATER_SOURCE;
- UNKNOWN_SOURCE_ROOT;
- SHARED_LINEAGE_SUSPECTED;
- CONTESTED_ATTRIBUTION;
- CONTESTED_DATE_OR_PLACE;
- EXACT_OBJECT_UNCERTAIN;
- MISSING_CONTEMPORANEOUS_ROOT;
- ARCHIVAL_ASYMMETRY;
- UNKNOWN_AGENT_OR_ROLE;
- TRANSCRIPTION_NEEDS_ORIGINAL;
- IMAGE_LINEAGE_UNRESOLVED;
- SCHEMA_BLOCKED_EVIDENCE.

Every task must name the assertion(s) or evidence edge(s) whose epistemic state motivates it.

## Epistemic-leverage priority tuple
Do not fabricate a pseudo-precise scalar score. Rank/triage transparently using this ordered tuple:
1. defect severity;
2. number/importance of assertions potentially affected;
3. discriminatory power between competing propositions;
4. ability to move evidence toward an earlier/direct root;
5. potential for genuinely independent evidence;
6. retrieval feasibility.

Record the dimensions individually so collaborators can see why a task matters.

## Task construction
A collaboration/archive task must contain:
- task ID and concise title;
- target defect(s);
- affected assertion/evidence IDs;
- exact research question;
- target institution/collection/record series when known;
- bounded date/name/place search parameters;
- desired artifact: scan, catalog record, finding-aid locator, transcription, photograph, negative ID, page image, archival citation, or documented null search;
- minimum provenance metadata to return;
- disconfirming/alternative evidence to capture rather than discard;
- completion criteria;
- epistemic outcomes that each possible result could support;
- explicit statement that completion alone changes no canonical assertion.

## Archive request design
Prefer requests that retrieve the underlying record, not merely a repository interpretation. Ask for identifiers sufficient for another researcher to reproduce the retrieval. For NARA include record group/series/container/item where available. For LOC include item/control/call/collection identifiers as applicable. For newspapers include title/date/page/edition and image/article relationship.

## Collaborator return package
Require collaborators to return the artifact or stable locator plus repository, identifier, date, creator/office when available, exact pages/frames, retrieval date, search terms/range for null results, and notes separating repository metadata from their own interpretation.

Collaborators should report unexpected contradictions and near-matches rather than filtering them out.

## Completion workflow
TASK_COMPLETED -> SOURCE_AUDIT_PENDING -> SCHEMA_FIT -> EVIDENCE_REVIEW -> TRANSACTION_PENDING -> CANONICAL_CHANGE.

No shortcut exists from TASK_COMPLETED to CANONICAL_CHANGE.

## Null results
A bounded null search is valuable for research planning and can lower the expected value of repeating the same search. It is not historical counter-evidence unless the archive's structure/coverage itself makes absence probative.

## Hard stops
Do not create vague tasks such as 'research this sculpture.' Do not prioritize merely because an archive is prestigious or nearby. Do not assign a collaborator to adjudicate a contested claim without requesting the underlying evidence. Do not treat an inaccessible foreign archive as evidence favoring the better-digitized domestic source lane.
