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
- merge method;
- expected head SHA.

Do not send optional custom merge commit title/message unless required. In this repository, optional merge metadata previously triggered connector safety blocking while the same merge succeeded with the minimal payload.

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
Action: preserve safety-critical fields, remove unnecessary optional fields, retry minimal mutation. Do not represent the operation as completed until GitHub confirms it.

### Temporary mergeability state
A newly created PR can briefly report indeterminate/not mergeable while GitHub computes state.
Action: re-read rather than treating it as a substantive conflict.

## 6. Transaction-specific controls
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
7. canonical JSON rewrite when a transaction is sufficient.

## Merge completion standard
Do not say "merged" until the merge action returns success and a merge commit SHA. If the connector blocks the mutation, report the PR as validated/open, not merged.
