---
type: decision
module: lens-core
surfaces: [bus, module]
date: 2026-11-08T12:09
source_commits: {}
---

# Standard 0.2.0: every row has one scope; nothing points across scopes

## What was done
Built roadmap item `spine-scope-column` to `docs/plans/2026-11-07-scope-column-research.md`,
test-first:
- **The column:** `scope_id uuid NOT NULL` on every table except `standard_version`. It is
  opaque and written by the module: no default, no trigger, no setting read.
- **No cross-scope references:** `UNIQUE (id, scope_id)` on every referenced table, and every
  link is now a table-level composite key including `scope_id`:
  - candidates to sources;
  - decisions to candidates;
  - the verified-to-decision contract (now four columns);
  - supersedes;
  - both ends and the source and candidate of relationships;
  - verified, merged-from and candidate of enrichments;
  - both oversight children.
- **Uniqueness and indexes:** a partial unique index for one current `canonical_key` per
  scope; oversight capability uniqueness per scope; a scope index on every scoped table.
- **Floor and version:** PostgreSQL 15 (`ON DELETE SET NULL (from_verified_id)` keeps the
  enrichment's scope when its merged-from entry is deleted). Standard version 0.2.0.
- **Launcher:** its column reader now ignores constraint continuation lines (`ON ...`). A test
  pins that every scoped table expects `scope_id`.
- **Tests:**
  - 3 static: every table but the version record has the scope; no default or setting;
    every reference carries the scope.
  - 7 database: decision, verified, relationship, enrichment and supersedes cannot cross
    scopes; per-scope key uniqueness; a referenced row cannot change scope; crossing works
    only as a new candidate; the delete rule keeps the scope.
  - Existing contract tests now run inside a scope.

## What was found / decided
No live Lens lab exists, so 0.1.0 is replaced without an upgrade path; the launcher refuses a lab
recording another version. The Tapestry rule is followed: project scopes take the registry
project id, and person ids are carried, never minted. Policies, the session setting, crossing
authorization and the public-project owner rule stay with `scope-boundary-enforcement`.

## Lessons
A parser that reads columns from DDL must also skip the continuation lines of table
constraints; the scope keys introduced the first multi-line constraint.
