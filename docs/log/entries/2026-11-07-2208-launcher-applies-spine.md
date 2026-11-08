---
type: decision
module: lens-core
surfaces: [module, bus, roadmap]
date: 2026-11-07T22:08
source_commits: {}
---

# Launcher applies the standard once, records its version, refuses unsafe targets

## What was done
Roadmap item `launcher-applies-spine`, with the reviewer's changes (R2, P2; approved by the
operator):
- `src/lens_core/launch.py`, `lens-core new`:
  - applies the standard to an empty database and records its version in the new
    `standard_version` table;
  - does nothing on a lab already at that version, so the security defaults are never re-run
    and grants added by access + tenancy (pr-007) survive;
  - refuses a non-empty database or a different recorded version (no upgrades yet);
  - checks afterwards that every declared table and column exists;
  - exit codes: 0 done, 1 configuration, 2 refused or shape problems.
- The standard states `lens-standard-version: 0.1.0` in its header.
- **Packaging:** the wheel bundles `docs/schema/spine.sql` as `lens_core/schema/spine.sql`
  (hatch force-include; still one source). A new `db` extra installs psycopg; the base install
  stays standard-library only. Verified locally by building a wheel; CI now builds the wheel,
  installs it in a clean virtual environment and runs `lens-core version`.
- **Spine notes (P2):**
  - owners, superusers and BYPASSRLS roles skip row security by design;
  - REVOKE FROM PUBLIC on tables records intent;
  - modules must revoke EXECUTE on any function they add, and close tables they add;
  - a test keeps the revoke block's table list equal to the actual tables.
- `tests/test_launch.py`: 3 unit tests and 5 database tests (apply then no-op, grants kept,
  non-empty refused, other version refused, shape check).
- The roadmap item no longer depends on the review contract (it didn't need to).

## What was found / decided
The old stub looked for the standard two folders above the package. That path does not exist
in an installed wheel, and the package had no database driver. Running the launcher twice on a
live lab must not re-run the standard, so the version record is what makes "safe to run
again" true.

## Lessons
Idempotent DDL is not the same as safe to re-run: REVOKE statements are idempotent but
destructive to grants made since. Gate re-application on a recorded version.
