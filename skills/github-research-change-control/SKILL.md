---
name: github-research-change-control
description: Safe GitHub workflow for provenance research repositories. Use for branches, repository writes, CI diagnosis, pull requests, transactions, schema migrations, and merges.
---

# GitHub research change control

## Principle
A failed write or merge is a diagnostic event, not permission to weaken controls.

## 1. Inspect before mutation
Read the current default/base state and the exact target files. Capture current blob SHAs. If a PR exists, read its current head SHA and state.

Classify the proposed change as one or more of:
- evidence/data transaction;
- schema migration;
- validator/test change;
- rendering/site change;
- workflow/CI change;
- documentation only.

Prefer one conceptual change per branch. Do not mix new historical evidence with ontology redesign unless the evidence itself requires that migration.

## 2. Choose the narrowest mutation
Prefer transaction files over direct canonical-data rewrites. Never invent an ID without checking the current namespace. Never add an enum simply to accommodate one record; route semantic mismatches to adaptive-schema review.

For file updates, use the current blob SHA as an optimistic lock. On stale SHA, re-read; never force an overwrite from stale state.

## 3. Validate the actual head
Required sequence before merge:
1. Read PR and capture current head SHA.
2. Retrieve CI/workflow results for that exact SHA.
3. Require all repository gates to succeed.
4. Re-read PR state if mergeability was initially unknown/false immediately after creation.
5. Confirm the head has not changed since validation.
6. Merge only with expected_head_sha equal to the validated head.

A successful workflow on an older head is not a merge gate for a newer head.

## 4. Minimal merge payload
Default merge mutation contains only:
- repository;
- PR number;
- expected head SHA.

Let GitHub use the repository's default merge method unless a specific method is itself a requirement. Do not send optional merge method, custom commit title, or custom commit message merely for presentation. In this repository, optional merge metadata and, later, an explicit merge method have both coincided with connector safety blocks while narrower payloads succeeded.

Preserve expected_head_sha on retries.

## 5. Failure classification
Diagnose before retrying:

### CI/model failure
Examples: invalid enum, broken reference, epistemic invariant failure.
Action: inspect logs; fix model/data. Do not merge around it.

### Concurrency failure
Examples: stale blob SHA, PR head changed.
Action: re-read state, reconcile, revalidate.

### GitHub state failure
Examples: merge conflict, permissions, branch rule.
Action: resolve repository state; do not weaken validation.

### Connector/safety failure
Mutation is blocked before GitHub accepts it.
Action: preserve safety-critical fields and remove unnecessary optional fields. One minimal retry is reasonable after re-reading PR state. If the minimal mutation containing only repository, PR number and expected_head_sha is also blocked, stop automated merge attempts for that validated head. Do not repeatedly hammer the same mutation and do not remove expected_head_sha merely to seek execution.

Connector permission to execute a mutation is distinct from repository readiness. Record both states separately.

### Temporary mergeability state
A newly created PR can briefly report indeterminate/not mergeable while GitHub computes state.
Action: re-read rather than treating it as a substantive conflict.

## 6. Validated human-merge handoff
When the connector blocks the minimal protected merge but all repository controls pass, produce a bounded handoff containing:
- PR number and link;
- validated head SHA;
- workflows checked and their successful conclusions;
- latest mergeable state;
- statement that the connector blocked execution before GitHub accepted the mutation;
- instruction to merge that PR in GitHub only if the displayed head still matches the validated SHA and required checks remain green.

After a human merge, re-read the PR before claiming completion. If the head changed before human merge, the prior validation is stale and the new head must be validated.

Do not substitute auto-merge unless the repository supports it and the user actually wants that behavior.

## 7. Transaction-specific controls
- Check transaction ID uniqueness before write.
- Use precondition hashes for updates to existing evidence records.
- Validate baseline and materialized state.
- Record epistemic deltas even when headline status is unchanged.
- Canonical state should be reproducible from baseline + ordered transactions/migrations.

## Regression cases
The workflow must correctly handle:
1. stale content SHA;
2. duplicate evidence/transaction ID;
3. invalid schema enum;
4. CI success on an obsolete PR head;
5. temporary PR mergeability lag;
6. connector merge block caused by optional metadata;
7. connector merge block even after a minimal protected payload;
8. unsupported auto-merge;
9. canonical JSON rewrite when a transaction is sufficient.

## Merge completion standard
Do not say "merged" until GitHub state confirms the PR was merged. A successful merge mutation normally supplies a merge commit SHA; after a human handoff, verify by re-reading the PR. If the connector blocks the mutation, report the PR as validated/open, not merged.
