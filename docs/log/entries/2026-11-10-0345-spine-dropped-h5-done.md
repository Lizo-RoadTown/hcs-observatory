---
type: decision
module: lens-core
surfaces: [identity, definition, module]
date: 2026-11-10T03:45
source_commits: {}
---

# Spine, launcher and tests dropped; H5 complete

## What was done
- Deleted `docs/schema/spine.sql` (frozen 0.2.0), `src/lens_core/` (the launcher), `tests/`, `pyproject.toml` and `.github/workflows/tests.yml`. There is no code left to test; CI returns with the web app.
- Removed the `bus` surface from `decomposition.json`.
- Rewrote README.md for the observatory (function names, the six modules, public-repo rule).
- Marked docs/BUILD.md historical.
- Removed `LENS_DB_URL` from .env.example.
- Removed the "in transition" notes from CHARTER.md and CLAUDE.md.

## What was found / decided
The conditions were verified on GitHub:
- H1/H2: the project knowledge graph's PR #1 is on main, as standard 0.3.0.
- H5: hcs-adaptive-engine PR #32 was merged by the operator at 2026-11-10T11:42Z. `migrations/0001_engine_trust.sql` is on main (b79aaf8), and its 13 tests pass on PostgreSQL 15.
- The engine dropped `oversight_proposals`, because proposals have one home: coordination's gate.

lens-core now holds no code from the old Lens. It is the observatory, with no data store.

## Lessons
- A peer's correction ("#32 is NOT merged") was out of date: the merge had already happened. Check GitHub state before acting on either message.
