---
type: decision
module: lens-core
surfaces: [roadmap]
date: 2026-11-08T12:01
source_commits: {}
---

# Scope column made firm; boundary enforcement split out

## What was done
- Split `spine-scope-column`, as proposed in `docs/plans/2026-11-07-scope-column-research.md`:
  - `spine-scope-column` (lens-core) is now **firm, now, in progress**: an opaque
    `scope_id`, composite keys so no reference crosses scopes, per-scope uniqueness, the
    PostgreSQL 15 floor, standard 0.2.0.
  - New `scope-boundary-enforcement` (access + tenancy, loose, later): policies, crossing
    authorization, and keeping public projects apart from their owner's personal data.
- Recorded Tapestry's answer to question 2 (`decision-scope-ids-two-authorities-2026-11-08`,
  citations checked) in the research doc. Project scope ids come from the project registry;
  person ids are carried as given.

## What was found / decided
The operator said "continue" after being asked whether to make the column firm; lens-core took
that as the go-ahead. The column's shape holds for every answer received:
- separate databases (operator);
- two id authorities (Tapestry);
- the open owner rule and tenancy-home.

Those open questions now sit with the enforcement item.

## Lessons
Split an item when part of it is settled and part is not, so the settled part can be built.
