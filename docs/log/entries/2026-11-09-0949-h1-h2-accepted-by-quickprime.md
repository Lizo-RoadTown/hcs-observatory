---
type: decision
module: lens-core
surfaces: [bus, module]
date: 2026-11-09T09:49
source_commits: {}
---

# H1/H2 accepted by QuickPrime (pending PR #1 merge); lens-core keeps its copy

## What was done
QuickPrime accepted hand-offs H1 (the spine and its tests) and H2 (the launcher) in QuickPrime PR #1. Its CI passed: 34 tests against Postgres 16, none skipped, and the wheel check passed. QuickPrime logged its acceptance as `docs/log/entries/2026-11-09-0939-accept-spine-and-launcher.md`. The merge waits on the operator's review.

## What was found / decided
- **What changed in transit:**
  - copied as files citing lens-core 5af31b3, with a PROVENANCE.md (not git filter-repo);
  - the spine became QuickPrime standard 0.3.0, the 0.2.0 shape without the `oversight_*` tables, which are left for H5 and the engine;
  - the launcher was renamed (`quickprime new`, `QUICKPRIME_DB_URL`);
  - the module list was dropped.
- **One scope per project:** each project's scope_id is its registry UUID, with no graph-wide scope.
- **lens-core keeps its copy** of `spine.sql`, `launch.py` and their tests until PR #1 is merged on QuickPrime main, per the hand-off condition. Removing them is a later decision entry.

## Lessons
A receiver may rightly change a handed-off artifact's version and names. Record the transformations on both sides so lineage stays traceable.
