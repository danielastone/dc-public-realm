# Fourth-object validation harness

Diagnostic harness for the I1 → I4 migration boundary. **Not part of any
workflow; nothing here changes production builders, validators, golden
expectations or deployment.**

```
pip install pyyaml
python3 tests/fourth-object/harness.py <output-dir>
```

Runtime ≈ 80 s. The harness works only in temporary copies and asserts that the
real checkout is unchanged before and after.

## What it does

1. **Clean reference**: runs every `run:` step of `build-site.yml` on an
   unmodified copy (must be 60/60).
2. **Fixture**: `make_fixture.py` writes a test-only ledger transaction for
   **OBJ-9104**, a *synthetic structural clone* of OBJ-0003 (see below).
3. **Unpatched control**: the existing production builder with OBJ-9104 in the
   ledger. Publication fails; this is the current production limitation.
4. **S0**: the same, plus one temp-only change: the legacy builder's fixed
   object list gains OBJ-9104. The real Python publication chain then produces
   the fourth page, homepage card, task pages and exports.
5. **Matrix D1–D12**: each row mutates a fresh copy of S0 (site rows) or the
   fixture before materialization (data rows), re-runs the validators, and
   classifies the row by its **difference from the unmutated S0**:
   `INTENDED_REJECT`, `UNEXPECTED_ACCEPT`, `WRONG_REASON`, `BLOCKED`, `PASS`.
   S0's own failures are recorded separately and never count as detection.
6. **Positive controls**: every row is repeated on the corresponding OBJ-0003
   record in the clean reference build. A row caught there but missed on
   OBJ-9104 is a scope gap, not a weak mutation.

Every row records proof that the mutation reached the artifact (marker counts
before/after, or the mutated field in materialized JSON), the intended
validator's baseline and mutated exit codes and diagnostic, and every other
step that newly failed.

## OBJ-9104 is synthetic

OBJ-9104 is a **structural clone of OBJ-0003, not an independently sourced
historical record**. Its 15 assertions, 21 evidence rows, 5 sources (with
ancestry), 3 research tasks and overview are copied into an isolated namespace
(`A-T9104-*`, `AE-T9104-*`, `SRC-T9104-*`, `TST-9104-*`) so it exercises the
same rendering paths: multi-source dependency, UNKNOWN ancestry, material
conflicts and research tasks. Overview prose is copied verbatim so displayed
facts reconcile to assertion literals. Links to real related entities (`AG-*`,
`OBJ-PRE-0001`, related assertion `A-0205C`) are inherited fixture
dependencies, not historical claims; mutations never touch them.

## S0 is a simulated publisher

A passing S0 does **not** show that production can publish a fourth object; the
unpatched control shows it cannot. Rendered-page mutations are applied after
rendering, so the Python determinism and final JS↔Python parity checks catch
every one of them. That is an artifact of the method (a renderer defect present
in both renderers would not be caught that way); those checks are reported but
never counted as the intended control.

`results/` holds the committed output of one run; two consecutive runs produced
byte-identical `results.json`.
