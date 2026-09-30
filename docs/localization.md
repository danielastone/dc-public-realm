# Localization architecture

Localization is a presentation layer over the canonical research record, not a second historical database.

## Canonical inheritance

Object IDs, dates, locations, source URLs, image provenance and rights, assertion IDs and statuses, evidence relationships, and research-task IDs remain canonical and language-independent. Localized records may supply only approved human-readable fields keyed to an existing object ID.

## Translation states

`DRAFT` means translation work is incomplete or unreviewed. `REVIEWED` means a human review has occurred. `PUBLISHED` requires review metadata. These states describe the translation, not the historical claim; they must never substitute for assertion statuses such as SUPPORTED or CONTESTED.

## Review rule

A localized page must resolve its factual graph from the same canonical record as the English page. Natural prose need not be textually identical, but language versions may not diverge on dates, sources, image rights, assertion statuses, or evidence relationships.

## Institutional collaboration

Embassy, museum, archive, or subject-matter review may be recorded as translation/context review without implying endorsement or giving the institution automatic evidentiary authority. Any substantive historical correction still enters through the normal assertion/evidence review process.

## Current scope

This infrastructure PR creates the schema and validation boundary only. It deliberately contains no Spanish Artigas prose and creates no Spanish public route. Those belong in subsequent reviewable PRs.
