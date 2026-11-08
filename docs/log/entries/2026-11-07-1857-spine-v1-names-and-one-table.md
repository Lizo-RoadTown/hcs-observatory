---
type: decision
module: lens-core
surfaces: [bus, source, roadmap]
date: 2026-11-07T18:57
source_commits:
  PROVES_LIBRARY: 02ab37e
---

# Spine v1: neutral names and the five one-table choices

## What was done
- The operator said go on Phase B (2026-11-07). The five firm spine items moved to `now` on
  the roadmap; `spine-scope-column` stays loose.
- Read the PROVES source (02ab37e, read-only):
  - **Aliases:** `knowledge_enrichment` (`supabase/migrations/009_add_verified_knowledge_layer.sql:186-216`)
    is a general enrichment table: alias, duplicate merge, cross-source, temporal update,
    epistemic refinement.
  - **Relationships:** `core_equivalences` exists only in the live-schema export
    (`exports/zenodo_supabase_2026-04-25/schema.sql:4141-4154`); no migration creates it.
  - **Broken writer:** `store_equivalence` (`production/Version 3/storage_v3.py:827-838`)
    inserts `equivalence_type`, `confidence_score`, `evidence_snapshot_id` and `reasoning`,
    none of which exist in the live table. It uses `ON CONFLICT (entity_a_id, entity_b_id)`
    with no matching unique constraint, and omits the required `created_by_run_id`, so it
    cannot succeed. The working shape is the live table that the graph API reads.
- Rewrote `docs/schema/spine.sql`:
  - The header no longer names reference tables; it points to Surveyor's case records.
  - Every table has `id uuid PRIMARY KEY DEFAULT gen_random_uuid()`.
  - Confidence is bounded 0 to 1.
  - New `relationships`: verified to verified; kind per lab; confidence; evidence; source;
    candidate; validation; no self-links; unique per ordered pair and kind.
  - New `enrichments`: the one home for aliases (required when kind is alias), merges,
    cross-source, updates and refinements.
  - Review state is documented as `candidates.status` plus the latest decision.
  - Groups of people are declared out of the spine (access + tenancy, pr-007).
- `tests/test_spine.py`:
  - static: no reference-system names in `docs/schema`; one table per kind; generated keys;
  - with a database: applies twice to an empty Postgres; relationship uniqueness; alias rule.
  - The database tests run in CI against a Postgres 16 service (`LENS_TEST_DB_URL`) and skip
    locally without one. psycopg is added to the dev extras.

## What was found / decided
The draft already used neutral table names; only its header carried PROVES names. Candidate
edges are ordinary candidates (kind plus payload) rather than a second staging table, which
keeps one intake path; promotion writes them to `relationships`. The enrichment kinds were
renamed neutrally (duplicate_merge to merge, temporal_update to update, epistemic_refinement to
refinement). Every name stays provisional until reconciliation (step 8).

## Lessons
The live schema and the code that writes it can disagree: the reference writer for
relationships could never have run. Derive the standard from the shape the working readers use,
and check writers against it.
