# Research: the scope column (roadmap item `spine-scope-column`), 2026-11-07

**Status:** research and recommendation. Nothing is built. Making the item firm is the
operator's call; two questions go to Tapestry.
**From:** a read-only research agent (PROVES, Tapestry, Loom_MCP, Postgres and Supabase docs),
with the key citations re-checked by lens-core.

## The problem

Every spine row must belong to exactly one scope: a project, a person, or a shared graph
(QuickPrime). Row security can then keep scopes apart. The standard must stay neutral about
scale (`docs/architecture/observatories.md`). Today no table has a scope column, and
`canonical_key` has no uniqueness rule because scope would change what unique means
(`docs/schema/spine.sql:17-19`).

## What the evidence shows

- **PROVES got it wrong in four ways:**
  - the organization column had a different name on each table, was nullable, and was added
    later (`023_organizations_and_provenance.sql:122,174,191`);
  - it was filled by a trigger reading a column that was never created (`023:450-467`; Surveyor
    `database-bus.md:59-60`);
  - no policy checked it on staging, decisions or the library; isolation lived only inside
    privileged functions (`database-bus.md:68-71`);
  - two tenancy models ran side by side (`database-bus.md:89`).
- **Tapestry and Loom_MCP do it right, and it is implemented:**
  - `tenant_id uuid NOT NULL` on every table;
  - the module writes it explicitly;
  - each transaction sets `app.tenant_id` (`Loom_MCP/services/agent-context/storage.py:142`);
  - policies compare against it and fail closed to an all-zeros id (`tapestry/infra/migrations/001_init_memory.sql:160`);
  - FORCE ROW LEVEL SECURITY covers owners (`:151`).

  Their gap: a child row can reference a parent in another tenant (plain foreign keys,
  `002_init_projects.sql:84-87`).
- **Postgres:** foreign key checks bypass row security
  (postgresql.org/docs/current/ddl-rowsecurity.html). Row security alone cannot stop a row in
  one scope from pointing at a row in another; composite foreign keys that include the scope
  can.

## Recommendation

1. **One column, `scope_id uuid NOT NULL`, on every spine table except `standard_version`.**
   - The scope is opaque: no kind column and no scopes table in the spine. That is what keeps
     it neutral; a project, a person and a shared graph are each just an id.
   - A scopes registry belongs to access + tenancy. The spine tests already forbid group
     tables in the standard.
2. **The writing module sets it explicitly.** No column default from a session setting, no
   trigger, no function. That matches Loom_MCP and avoids PROVES's implicit assignment.
   - Access + tenancy names the session setting, writes the policies (`USING` and `WITH CHECK`
     on `scope_id`), and sets FORCE ROW LEVEL SECURITY.
3. **No reference crosses scopes.**
   - `UNIQUE (id, scope_id)` on every referenced table.
   - Every internal foreign key includes `scope_id`.
   - The verified-to-decision key becomes
     `(decision_id, candidate_id, decision_action, scope_id)`, so the accept-only guarantee
     holds within one scope.
4. **Moving knowledge between scopes means a new candidate in the target scope,** reviewed
   through the normal path, with lineage in that scope's `sources` row. The spine already
   handles imports this way. Rows never change scope: the composite keys block it for any row
   that is referenced, and access + tenancy blocks it for the rest (no UPDATE grant on
   `scope_id`).
5. **Uniqueness per scope:**
   - a partial unique index on `verified (scope_id, canonical_key) WHERE is_current`;
   - `oversight_capabilities UNIQUE (scope_id, agent_name, capability_type)`;
   - a leading `scope_id` index on every table.
6. **Require PostgreSQL 15** (decided by lens-core). The enrichment's "merged from" link keeps
   its meaning with `ON DELETE SET NULL (from_verified_id)`, which only exists from 15. Plain
   SET NULL would also null `scope_id` and fail. Postgres 13 is past end of life; CI runs 16
   and the PROVES Supabase runs 17.
7. **Standard version 0.1.0 becomes 0.2.0.**
   - It is a breaking change, and the launcher already refuses a different recorded version.
   - No live Lens lab exists (`LENS_DB_URL` is empty and no launch is logged), so no upgrade
     path is needed before v1.

Tests in the existing style:
- static: every table has the column; no setting-based default; every internal reference
  includes the scope;
- database: decisions, verified rows, relationships, enrichments and supersedes links cannot
  cross scopes; per-scope `canonical_key` uniqueness; a referenced row's scope cannot change;
  a crossing works only as a new candidate; the delete rule keeps `scope_id`.

## What is not decided here

The questions only Tapestry can answer are sent to Tapestry as research items:
1. Do personal and project data ever share one database? Or is the boundary always between
   databases, with the export step as the boundary?
2. Do scope ids come from one registry shared with Tapestry's `tenant_id` and QuickPrime, so
   a person's id means the same thing everywhere?

Who authorizes a crossing, and how it is recorded, belongs to access + tenancy and Tapestry.

None of these changes the column's shape. The recommendation holds whatever the answers are.

## The operator's answer (2026-11-07)

Question 1 is answered (loom memory
`decision-personal-project-boundary-and-public-projects-2026-11-07`):
- **Separate databases:** personal and project data do not typically share a database. A
  project is like a GitHub repo that people push to, pull from and contribute to. There is a
  boundary between the two layers.
- **Owners:** an owner holds everything personally. Whether to force the owner's personal data
  apart from the project's when the project is made **public** is to be discussed with the
  operator.
- **Public projects:** a public project is what QuickPrime reads. It notes the contributors and
  hooks into the project and their personal MCPs to track communication between contributors.

Effect on this design: none on the column's shape. The boundary is normally between databases,
and within a project database `scope_id` keeps projects apart. Forced separation for public
projects belongs to the boundary-enforcement item. Question 2 (one shared id registry) stays
with Tapestry.

## Tapestry's answer to question 2 (2026-11-08)

Loom memory `decision-scope-ids-two-authorities-2026-11-08`, citations checked:
- **Project ids come from one shared registry.** The project registry mints random UUIDs
  (`tapestry/infra/migrations/002_init_projects.sql:14-15`), and every onboarded repo already
  holds its UUID. A Lens project's `scope_id` should be its registry project id, so it means
  the same thing in the Lens, Tapestry and the shared graph.
- **Person ids are an auth-layer constant,** the same across Tapestry's services
  (`tapestry/packages/auth/python/loom_auth/auth_bridge.py:94-110`), not a registry row. The
  Lens carries a person id as given and never mints its own.
- Whether people also get rows in one unified registry is the open tenancy-home decision. The
  opaque `scope_id` does not depend on it.

## Proposed roadmap change

Split `spine-scope-column`:
- **`spine-scope-column`** (lens-core): the column, the composite keys, uniqueness and the
  Postgres 15 floor. It can be **firm now**, since the shape does not depend on the open
  questions.
- **`scope-boundary-enforcement`** (access + tenancy, with Tapestry; loose): the policies, the
  session setting, and authorizing crossings, decided when Tapestry answers the two questions
  above.
