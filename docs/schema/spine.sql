-- The Lens: the shared database standard ("the spine"). v1 in progress (Phase B).
--
-- The fixed shape every Lens lab meets on. Domain-neutral by design: no subject-specific
-- columns and no proprietary vocabulary. A lab maps its domain into these neutral slots
-- (kinds and payloads, set by injected config) instead of changing the shape.
--
-- The spine: candidates -> decisions -> verified, with sources for lineage.
-- Around the verified layer: relationships and enrichments.
-- Plus an optional oversight set for agent-assisted labs (its home is still open: roadmap
-- item oversight-tables-home).
--
-- Where each table came from, and the one-table choices the operator approved, are
-- recorded in Surveyor: docs/decomposition/proves/database-bus.md and module-map.md
-- section 5. Names here are provisional; final names come after the full decomposition
-- is reconciled.
--
-- Scope (lens-core docs/plans/2026-11-07-scope-column-research.md):
--   * Every row except standard_version carries scope_id: the one scope it belongs to. It
--     is opaque. A project's scope is its registry project id; a person's is the id their
--     auth layer carries. The standard never says what kind of scope it is.
--   * The writing module sets scope_id explicitly. There is no default and no trigger.
--   * No reference crosses scopes: every link between spine tables is a composite key
--     that includes scope_id (foreign key checks bypass row security, so policies alone
--     could not stop it).
--   * Rows never change scope. Moving knowledge to another scope means a new candidate in
--     the target scope, reviewed the normal way, with its origin recorded in that scope's
--     sources row.
--   * Policies that use scope_id, the session setting they read, and who may cross
--     scopes belong to the access + tenancy module (pr-007), roadmap item
--     scope-boundary-enforcement.
-- Groups of people (organizations, members, roles) belong to that module too, not the spine.
--
-- Requires PostgreSQL 15 or later (ON DELETE SET NULL with a column list). Safe to apply
-- to an empty database more than once. Apply it with `lens-core new`, which records the
-- version below and does not re-apply it to a lab already at this version: re-running the
-- security defaults on a live lab would remove grants that the access + tenancy module
-- added.
--
-- lens-standard-version: 0.2.0

-- ---------------------------------------------------------------------------
-- Lineage: where a candidate came from, kept separate from the claim itself.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS sources (
    id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    scope_id      uuid NOT NULL,
    uri           text,                 -- where the material was read from
    snapshot      jsonb,                -- raw captured payload, for audit
    fetched_at    timestamptz NOT NULL DEFAULT now(),
    UNIQUE (id, scope_id)
);

-- ---------------------------------------------------------------------------
-- Candidates (the inbox): findings captured but NOT yet true.
-- Written by intake; read by review. A candidate edge between two things is a candidate
-- like any other (its kind and payload say so); promotion writes it to relationships.
-- Review state is this status plus the latest row in decisions. There is no second
-- review-state column anywhere.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS candidates (
    id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    scope_id      uuid NOT NULL,
    source_id     uuid,
    kind          text NOT NULL,        -- neutral type set, defined per lab (injected)
    payload       jsonb NOT NULL,       -- the finding
    evidence      jsonb,                -- quote or reference supporting it
    confidence    real CHECK (confidence IS NULL OR confidence BETWEEN 0 AND 1),
    status        text NOT NULL DEFAULT 'pending'
                    CHECK (status IN ('pending','accepted','rejected','needs_context','merged')),
    created_at    timestamptz NOT NULL DEFAULT now(),
    UNIQUE (id, scope_id),
    FOREIGN KEY (source_id, scope_id) REFERENCES sources (id, scope_id)
);

-- ---------------------------------------------------------------------------
-- Decisions (append-only review log): every accept, reject, edit, merge or flag.
-- Written by review (human or agent); the audit trail.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS decisions (
    id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    scope_id      uuid NOT NULL,
    candidate_id  uuid NOT NULL,
    action        text NOT NULL
                    CHECK (action IN ('accept','reject','edit','merge','flag')),
    actor         text NOT NULL,        -- who decided
    actor_kind    text NOT NULL DEFAULT 'human'
                    CHECK (actor_kind IN ('human','agent')),
    reason        text,
    before        jsonb,
    after         jsonb,
    created_at    timestamptz NOT NULL DEFAULT now(),
    UNIQUE (id, candidate_id, action, scope_id),  -- lets verified point at one accept decision
    FOREIGN KEY (candidate_id, scope_id) REFERENCES candidates (id, scope_id)
);

-- ---------------------------------------------------------------------------
-- Verified (the library): human-established truth, versioned.
-- Written by promotion (lens-review owns that code); read by serve.
--
-- The review and promotion contract, enforced by the database: every verified entry
-- names the candidate it came from and the decision that accepted it, and that decision
-- must be an 'accept' on that same candidate, in the same scope. Imports follow the same
-- path (record a candidate and an accept decision by the importer). The composite foreign
-- key does this without triggers.
--
-- Not enforced here (no triggers; the writer's job, checked by lens-review's tests):
--   * the candidate's status being 'accepted';
--   * the accept being the latest decision on that candidate.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS verified (
    id               uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    scope_id         uuid NOT NULL,
    canonical_key    text NOT NULL,
    kind             text NOT NULL,
    payload          jsonb NOT NULL,
    candidate_id     uuid NOT NULL,
    decision_id      uuid NOT NULL,
    decision_action  text NOT NULL DEFAULT 'accept' CHECK (decision_action = 'accept'),
    provenance       jsonb,             -- further trail (sources, merged decisions)
    is_current       boolean NOT NULL DEFAULT true,
    superseded_by    uuid,
    verified_by      text,
    verified_at      timestamptz NOT NULL DEFAULT now(),
    UNIQUE (id, scope_id),
    FOREIGN KEY (decision_id, candidate_id, decision_action, scope_id)
        REFERENCES decisions (id, candidate_id, action, scope_id),
    FOREIGN KEY (superseded_by, scope_id) REFERENCES verified (id, scope_id)
);

-- One current entry per canonical key within a scope.
CREATE UNIQUE INDEX IF NOT EXISTS verified_current_key_per_scope
    ON verified (scope_id, canonical_key) WHERE is_current;

-- ---------------------------------------------------------------------------
-- Relationships: verified links between two verified entries (the graph's edges).
-- The one home for relationships. The kind (e.g. same concept, wraps, depends on) is
-- defined per lab. One row per ordered pair and kind; both ends are in the row's scope.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS relationships (
    id             uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    scope_id       uuid NOT NULL,
    from_id        uuid NOT NULL,
    to_id          uuid NOT NULL,
    kind           text NOT NULL,
    confidence     real NOT NULL CHECK (confidence BETWEEN 0 AND 1),
    evidence       jsonb,               -- why the link holds
    source_id      uuid,
    candidate_id   uuid,                -- the candidate it was promoted from
    validated_by   text,
    validated_at   timestamptz,
    created_at     timestamptz NOT NULL DEFAULT now(),
    CHECK (from_id <> to_id),
    UNIQUE (from_id, to_id, kind),
    FOREIGN KEY (from_id, scope_id) REFERENCES verified (id, scope_id) ON DELETE CASCADE,
    FOREIGN KEY (to_id, scope_id) REFERENCES verified (id, scope_id) ON DELETE CASCADE,
    FOREIGN KEY (source_id, scope_id) REFERENCES sources (id, scope_id),
    FOREIGN KEY (candidate_id, scope_id) REFERENCES candidates (id, scope_id)
);

-- ---------------------------------------------------------------------------
-- Enrichments: what was learned about a verified entry after it was verified.
-- The one home for aliases, and for merges, cross-source corroboration, updates over
-- time and refinements.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS enrichments (
    id                   uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    scope_id             uuid NOT NULL,
    verified_id          uuid NOT NULL,
    kind                 text NOT NULL
                           CHECK (kind IN ('alias','merge','cross_source','update','refinement')),
    from_verified_id     uuid,          -- merged from; cleared if that entry is deleted
    candidate_id         uuid,
    alias                text,          -- required when kind = 'alias'
    merged               jsonb,         -- attributes taken from the merged entry
    conflict_resolution  jsonb,         -- how conflicts were resolved
    confidence_delta     real,          -- change in confidence from corroboration
    actor                text NOT NULL, -- who or what enriched it
    notes                text,
    created_at           timestamptz NOT NULL DEFAULT now(),
    CHECK (kind <> 'alias' OR alias IS NOT NULL),
    FOREIGN KEY (verified_id, scope_id) REFERENCES verified (id, scope_id) ON DELETE CASCADE,
    FOREIGN KEY (from_verified_id, scope_id) REFERENCES verified (id, scope_id)
        ON DELETE SET NULL (from_verified_id),
    FOREIGN KEY (candidate_id, scope_id) REFERENCES candidates (id, scope_id)
);

-- ---------------------------------------------------------------------------
-- Oversight (optional, for agent-assisted labs): capabilities, proposals, trust.
-- oversight_proposals is the one home for proposed improvements.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS oversight_capabilities (
    id                    uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    scope_id              uuid NOT NULL,
    agent_name            text NOT NULL,
    capability_type       text NOT NULL,
    trust_score           real NOT NULL DEFAULT 0,
    auto_approve_threshold real,
    requires_review       boolean NOT NULL DEFAULT true,
    UNIQUE (id, scope_id),
    UNIQUE (scope_id, agent_name, capability_type)
);

CREATE TABLE IF NOT EXISTS oversight_proposals (
    id             uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    scope_id       uuid NOT NULL,
    capability_id  uuid,
    proposed       jsonb NOT NULL,
    rationale      text,
    status         text NOT NULL DEFAULT 'pending'
                     CHECK (status IN ('pending','approved','rejected','auto_approved','implemented','reverted')),
    created_at     timestamptz NOT NULL DEFAULT now(),
    FOREIGN KEY (capability_id, scope_id) REFERENCES oversight_capabilities (id, scope_id)
);

CREATE TABLE IF NOT EXISTS oversight_trust_history (
    id             uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    scope_id       uuid NOT NULL,
    capability_id  uuid,
    delta          real NOT NULL,
    reason         text,
    created_at     timestamptz NOT NULL DEFAULT now(),
    FOREIGN KEY (capability_id, scope_id) REFERENCES oversight_capabilities (id, scope_id)
);

-- Scope filters: every scoped table is indexed by scope first.
CREATE INDEX IF NOT EXISTS sources_scope_idx ON sources (scope_id);
CREATE INDEX IF NOT EXISTS candidates_scope_idx ON candidates (scope_id);
CREATE INDEX IF NOT EXISTS decisions_scope_idx ON decisions (scope_id);
CREATE INDEX IF NOT EXISTS verified_scope_idx ON verified (scope_id);
CREATE INDEX IF NOT EXISTS relationships_scope_idx ON relationships (scope_id);
CREATE INDEX IF NOT EXISTS enrichments_scope_idx ON enrichments (scope_id);
CREATE INDEX IF NOT EXISTS oversight_capabilities_scope_idx ON oversight_capabilities (scope_id);
CREATE INDEX IF NOT EXISTS oversight_proposals_scope_idx ON oversight_proposals (scope_id);
CREATE INDEX IF NOT EXISTS oversight_trust_history_scope_idx ON oversight_trust_history (scope_id);

-- ---------------------------------------------------------------------------
-- Which version of this standard a lab is on. Written by `lens-core new`. Not scoped: it
-- describes the lab, not any one scope.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS standard_version (
    id          uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    version     text NOT NULL UNIQUE,
    applied_at  timestamptz NOT NULL DEFAULT now()
);

-- ---------------------------------------------------------------------------
-- Security defaults: every table starts closed.
-- Row security is on with no policies, so an ordinary role sees no rows even if it is
-- granted access by mistake. Hosts that grant new tables to API roles by default
-- (Supabase's anon and authenticated) have those grants removed after creation.
-- Policies and grants for real users come from the access + tenancy module (pr-007).
--
-- Notes:
--   * Table owners, superusers and roles with BYPASSRLS (for example a host's service
--     role) skip row security by design; keep their credentials server-side.
--   * Tables get no PUBLIC privileges by default; the REVOKE FROM PUBLIC lines record the
--     intent. The schema's own PUBLIC usage is left to the host.
--   * The standard defines no functions or triggers. A module that adds a function must
--     revoke EXECUTE from PUBLIC (and from anon and authenticated) itself.
--   * Tables a module adds later are that module's to close the same way.
-- ---------------------------------------------------------------------------
ALTER TABLE sources ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON sources FROM PUBLIC;
ALTER TABLE candidates ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON candidates FROM PUBLIC;
ALTER TABLE decisions ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON decisions FROM PUBLIC;
ALTER TABLE verified ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON verified FROM PUBLIC;
ALTER TABLE relationships ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON relationships FROM PUBLIC;
ALTER TABLE enrichments ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON enrichments FROM PUBLIC;
ALTER TABLE oversight_capabilities ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON oversight_capabilities FROM PUBLIC;
ALTER TABLE oversight_proposals ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON oversight_proposals FROM PUBLIC;
ALTER TABLE oversight_trust_history ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON oversight_trust_history FROM PUBLIC;
ALTER TABLE standard_version ENABLE ROW LEVEL SECURITY;
REVOKE ALL ON standard_version FROM PUBLIC;

DO $$
DECLARE
    r text;
    t text;
BEGIN
    FOREACH r IN ARRAY ARRAY['anon', 'authenticated'] LOOP
        IF EXISTS (SELECT 1 FROM pg_roles WHERE rolname = r) THEN
            FOREACH t IN ARRAY ARRAY['sources', 'candidates', 'decisions', 'verified', 'relationships', 'enrichments', 'oversight_capabilities', 'oversight_proposals', 'oversight_trust_history', 'standard_version'] LOOP
                EXECUTE format('REVOKE ALL ON %I FROM %I', t, r);
            END LOOP;
        END IF;
    END LOOP;
END $$;
