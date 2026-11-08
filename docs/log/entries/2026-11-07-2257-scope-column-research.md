---
type: process
module: lens-core
surfaces: [roadmap]
date: 2026-11-07T22:57
source_commits: {}
---

# Scope column researched; recommendation and a proposed split

## What was done
A read-only agent researched roadmap item `spine-scope-column` across PROVES, Tapestry,
Loom_MCP and the Postgres and Supabase docs. lens-core re-checked the key citations
(`spine.sql:140`, `Loom_MCP storage.py:142`, `tapestry 001_init_memory.sql:151,160`) and wrote
`docs/plans/2026-11-07-scope-column-research.md`.

## What was found / decided
- **Recommended:**
  - one opaque `scope_id uuid NOT NULL`, written explicitly by the module;
  - composite keys so no reference crosses scopes (foreign key checks bypass row security);
  - per-scope uniqueness;
  - crossings as new candidates in the target scope;
  - standard 0.2.0, with no upgrade path needed because no live lab exists.
- **lens-core decided its own design question:** require PostgreSQL 15, for
  `ON DELETE SET NULL (from_verified_id)`. Postgres 13 is past end of life; CI runs 16.
- **Two questions go to Tapestry as research:** whether personal and project data ever share
  a database, and whether scope ids come from one registry shared with `tenant_id` and
  QuickPrime.
- **Proposed split:** the column shape as a firm lens-core item; boundary enforcement as a loose
  item for access + tenancy and Tapestry. Making it firm is the operator's call; the roadmap is
  unchanged until then.

## Lessons
Row security does not cover foreign key checks, so isolation needs the scope inside the keys
themselves, not only in policies.
