# Alpha publication remediation register

**Audit baseline:** 2026-09-30  
**Scope:** Home, Methodology, Collaborate, Data, Artigas, San Martín, Cuban Urn  
**Status:** ACTIVE

## Purpose

This register is the authoritative tracking record for defects and publication-control gaps identified during the outsider audit of the *Diplomatic Gifts in Washington* alpha.

Finding IDs are permanent. They must not be renumbered or reused after closure. GitHub issues, pull requests, commits, tests, and later audits should cite these IDs.

The original audit should be preserved separately as point-in-time evidence. This register records remediation and disposition; it does not replace or rewrite the audit that produced the findings.

## Closure rule

A finding is **CLOSED** only when all applicable conditions are satisfied:

1. corrective implementation is merged;
2. an automated acceptance test passes, unless the finding is explicitly documented as not automatable;
3. the public build demonstrates the corrected behavior;
4. closure evidence is linked in this register; and
5. where the control applies to object publication, Artigas, San Martín, and Cuban Urn have been checked for regression.

A code change by itself does not close a finding.

## Status values

- **OPEN** — defect/control gap confirmed; corrective action incomplete.
- **IN PROGRESS** — implementation underway.
- **VERIFY** — implementation merged; acceptance/publication verification outstanding.
- **CLOSED** — closure rule satisfied.
- **DEFERRED** — intentionally postponed with documented rationale; not equivalent to closure.

## Remediation register

| ID | Priority | Finding | Acceptance test | Issue | Test | Closure evidence | Status |
|---|---|---|---|---|---|---|---|
| PUB-001 | P0 | `/data/` canonical-data destination returns 404 or otherwise fails to provide the promised data surface. | Every published canonical-data link resolves to a usable data index or the object's canonical data file. | #45 | `scripts/validate_pub001_routes.py` | PRs #48/#49; merge `d447222`; Actions run #118 build + deploy succeeded | CLOSED |
| PUB-002 | P0 | Primary navigation and alpha-state presentation are inconsistent across audited pages. | Home, Methodology, Collaborate, Data, and all audited object pages use the same defined primary navigation and alpha-state treatment. | #46 | TBD | TBD | OPEN |
| PUB-003 | P0 | Open research tasks summarized elsewhere are not exposed on the corresponding object pages. | Published task counts reconcile exactly to visible/linkable open tasks on each audited object page. | #47 | TBD | TBD | OPEN |
| EPI-001 | P0 | Public verification/status labels do not expose the rule responsible for the classification. | Every published epistemic status maps to an identifiable published rule or rule identifier sufficient to explain why the status was assigned. | TBD | TBD | TBD | OPEN |
| EPI-002 | P0 | Multiple sources can appear as corroboration without exposing whether their effective claim roots are independent. | Publication distinguishes independent, dependent/inherited, and unresolved corroboration; independence is asserted only when established under the source-inheritance rules. | TBD | TBD | TBD | OPEN |
| EPI-003 | P0 | Unknown or unresolved source ancestry can disappear from the public presentation. | Unknown ancestry remains explicit in publication and is never silently treated as independent evidence. | TBD | TBD | TBD | OPEN |
| EPI-004 | P1 | Public claim lineage is insufficient for an outsider to trace an important assertion through its evidence and source ancestry. | A published assertion can be traced from stable assertion identity to evidence and effective claim root, with unresolved lineage disclosed. | TBD | TBD | TBD | OPEN |
| EPI-005 | P1 | Conflicting evidence present in canonical data may be lost or understated in rendering. | A material canonical conflict necessarily produces a visible conflict or qualification on the corresponding public assertion. | TBD | TBD | TBD | OPEN |
| DATA-001 | P1 | HTML-to-canonical-data reconciliation is not mechanically demonstrated. | Every rendered factual assertion has a stable assertion identifier that maps unambiguously to canonical data. | TBD | TBD | TBD | OPEN |
| DATA-002 | P1 | Homepage/object summaries can drift from underlying canonical state if maintained separately. | Status badges, research-task counts, and other derived summaries reconcile to or are generated from canonical state. | TBD | TBD | TBD | OPEN |
| UX-001 | P1 | Object cards repeat generic copy rather than communicating object-specific significance or research gaps. | Each audited object card communicates a specific historically or epistemically relevant feature without overstating the evidence. | TBD | TBD | TBD | OPEN |
| META-001 | P2 | Public pages have weak or generic discovery metadata. | Each audited public page has an appropriate unique title and description; canonical/social metadata are present where the site architecture calls for them. | TBD | TBD | TBD | OPEN |

## Publication reconciliation matrix

The alpha remediation is not complete until the three reference objects pass the publication-to-data reconciliation below.

| Control | Artigas | San Martín | Cuban Urn |
|---|---|---|---|
| Rendered assertion maps to stable assertion ID | NOT TESTED | NOT TESTED | NOT TESTED |
| Displayed status equals computed canonical status | NOT TESTED | NOT TESTED | NOT TESTED |
| Status rule is identifiable | NOT TESTED | NOT TESTED | NOT TESTED |
| Displayed evidence maps to evidence records | NOT TESTED | NOT TESTED | NOT TESTED |
| Source independence/dependence is represented accurately | NOT TESTED | NOT TESTED | NOT TESTED |
| Unknown ancestry remains visible | NOT TESTED | NOT TESTED | NOT TESTED |
| Material conflicts remain visible | NOT TESTED | NOT TESTED | NOT TESTED |
| Open research tasks reconcile | NOT TESTED | NOT TESTED | NOT TESTED |
| Canonical-data links resolve | PASS | PASS | PASS |

### San Martín regression control

The Daumas/Dumont naming issue is a specific lineage/normalization stress test. Original source wording, later wording or normalization, uncertainty, and the basis for the current assertion must remain recoverable through the publication chain. A clean normalized display that silently removes the disagreement is a failed publication control even if the underlying data retain the distinction.

## Remediation gates

### Gate 1 — Publication shell

Required findings: `PUB-001`, `PUB-002`, `PUB-003`.

**Exit criterion:** canonical-data navigation works, the site uses the defined shared navigation, and research tasks reconcile to object pages.

**Status:** BLOCKED (`PUB-001` closed; `PUB-002` and `PUB-003` open)

### Gate 2 — Public epistemic contract

Required findings: `EPI-001`, `EPI-002`, `EPI-003`.

**Exit criterion:** a reader can determine why a status was assigned and cannot mistake dependent or unknown source ancestry for independent corroboration.

**Status:** BLOCKED

### Gate 3 — Provenance publication

Required findings: `EPI-004`, `EPI-005`, `DATA-001`.

**Exit criterion:** important published assertions are traceable to canonical evidence/lineage and material conflicts survive rendering.

**Status:** BLOCKED

### Gate 4 — Three-object reconciliation

Required evidence: completed publication reconciliation matrix and San Martín regression control.

**Exit criterion:** Artigas, San Martín, and Cuban Urn pass the defined reconciliation controls.

**Status:** BLOCKED

### Gate 5 — Expansion readiness

Required findings: all P0 and P1 findings closed; publication controls enforced automatically where feasible.

**Exit criterion:** adding another object does not require manually reproducing status, task, provenance, or summary state across separate publication surfaces.

**Status:** BLOCKED

## Closure evidence

### PUB-001

Issue: #45  
Implementation: PR #48 and PR #49  
Merged production fix: `d44722235d3214ff17729b32c4d719a6976f9348`  
Automated acceptance test: `scripts/validate_pub001_routes.py`  
Production verification: GitHub Actions run #118 (`36723721000`), build and deploy jobs both succeeded  
Three-object regression: canonical-data route checks passed for Artigas, San Martín, and Cuban Urn  
Closed: 2026-09-30  
Disposition: `/data/` is now a published canonical-data index, the final homepage routes Data to that index, and downstream page transformations are guarded so all three reference object pages retain the canonical-data link.

## Closure evidence format

When closing a finding, replace the `TBD` fields with durable references and add a short disposition entry below. Example:

```text
EPI-002
Issue: #123
PR: #130
Test: tests/publication/test_epi_002_source_independence.py
Production verification: <stable page/reference>
Closed: YYYY-MM-DD
Disposition: Publication now distinguishes independent, inherited, and unresolved corroboration.
```

Do not mark a finding closed solely because an issue or pull request was closed.

## Audit principle

The relevant end state is not merely that canonical data are internally rigorous. For any important public assertion, an outsider should be able to determine:

1. what exactly is being claimed;
2. what evidence supports it;
3. where that evidence obtained the claim when inheritance matters;
4. what rule produced the displayed status;
5. whether apparent corroboration is actually independent;
6. what material conflicts or uncertainty remain; and
7. what open research could resolve the uncertainty.

If epistemically material qualification exists in canonical state but disappears during publication, the publication control fails even when the rendered statement is technically consistent with one field in the underlying data.
