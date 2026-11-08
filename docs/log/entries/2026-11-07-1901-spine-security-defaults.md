---
type: decision
module: lens-core
surfaces: [bus]
date: 2026-11-07T19:05
source_commits: {}
---

# Spine starts closed: row security on, no PUBLIC or hosted-API grants, no triggers

## What was done
Roadmap item `spine-security-defaults`. At the end of `docs/schema/spine.sql`, every table:
- has row security on with no policies;
- revokes all privileges from PUBLIC.

A guarded block revokes everything from `anon` and `authenticated` when those roles exist
(Supabase's API roles, which hosts grant new tables to by default).

Tests: a static check that every table is closed and the standard has no triggers; a database
test that simulates a host granting new tables to anon and authenticated by default, then
checks that neither they nor an unrelated role can read any table and that row security is on
everywhere.

## What was found / decided
PROVES had grants to anon and no organization row security (Surveyor database-bus.md). The
neutral standard starts closed on any host; access is opened deliberately by the access +
tenancy module (pr-007) with policies and grants. Guarding on role existence keeps the standard
from depending on one host. The PROVES `source_id` trigger bug cannot recur, because the
standard defines no triggers.

## Lessons
Default privileges on hosted Postgres grant new tables to API roles silently. A standard that
must start closed has to revoke after creating, not just avoid granting.
