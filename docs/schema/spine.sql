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
-- Not yet here (roadmap):
--   * the scope column on every table (spine-scope-column, loose);
--   * the review and promotion contract (review-promotion-contract);
--   * grants and row security defaults (spine-security-defaults).
-- Groups of people (organizations, members, roles) belong to the access + tenancy module
-- (pr-007), not the spine.
--
-- Requires PostgreSQL 13 or later (gen_random_uuid is built in). Safe to apply more than
-- once.

-- ---------------------------------------------------------------------------
-- Lineage: where a candidate came from, kept separate from the claim itself.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS sources (
    id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    uri           text,                 -- where the material was read from
    snapshot      jsonb,                -- raw captured payload, for audit
    fetched_at    timestamptz NOT NULL DEFAULT now()
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
    source_id     uuid REFERENCES sources(id),
    kind          text NOT NULL,        -- neutral type set, defined per lab (injected)
    payload       jsonb NOT NULL,       -- the finding
    evidence      jsonb,                -- quote or reference supporting it
    confidence    real CHECK (confidence IS NULL OR confidence BETWEEN 0 AND 1),
    status        text NOT NULL DEFAULT 'pending'
                    CHECK (status IN ('pending','accepted','rejected','needs_context','merged')),
    created_at    timestamptz NOT NULL DEFAULT now()
);

-- ---------------------------------------------------------------------------
-- Decisions (append-only review log): every accept, reject, edit, merge or flag.
-- Written by review (human or agent); the audit trail.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS decisions (
    id            uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    candidate_id  uuid NOT NULL REFERENCES candidates(id),
    action        text NOT NULL
                    CHECK (action IN ('accept','reject','edit','merge','flag')),
    actor         text NOT NULL,        -- who decided
    actor_kind    text NOT NULL DEFAULT 'human'
                    CHECK (actor_kind IN ('human','agent')),
    reason        text,
    before        jsonb,
    after         jsonb,
    created_at    timestamptz NOT NULL DEFAULT now()
);

-- ---------------------------------------------------------------------------
-- Verified (the library): human-established truth, versioned.
-- Written by promotion (from an accepted candidate); read by serve.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS verified (
    id             uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    canonical_key  text NOT NULL,
    kind           text NOT NULL,
    payload        jsonb NOT NULL,
    provenance     jsonb,               -- source and decision trail
    is_current     boolean NOT NULL DEFAULT true,
    superseded_by  uuid REFERENCES verified(id),
    verified_by    text,
    verified_at    timestamptz NOT NULL DEFAULT now()
);

-- ---------------------------------------------------------------------------
-- Relationships: verified links between two verified entries (the graph's edges).
-- The one home for relationships. The kind (e.g. same concept, wraps, depends on) is
-- defined per lab. One row per ordered pair and kind.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS relationships (
    id             uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    from_id        uuid NOT NULL REFERENCES verified(id) ON DELETE CASCADE,
    to_id          uuid NOT NULL REFERENCES verified(id) ON DELETE CASCADE,
    kind           text NOT NULL,
    confidence     real NOT NULL CHECK (confidence BETWEEN 0 AND 1),
    evidence       jsonb,               -- why the link holds
    source_id      uuid REFERENCES sources(id),
    candidate_id   uuid REFERENCES candidates(id),  -- the candidate it was promoted from
    validated_by   text,
    validated_at   timestamptz,
    created_at     timestamptz NOT NULL DEFAULT now(),
    CHECK (from_id <> to_id),
    UNIQUE (from_id, to_id, kind)
);

-- ---------------------------------------------------------------------------
-- Enrichments: what was learned about a verified entry after it was verified.
-- The one home for aliases, and for merges, cross-source corroboration, updates over
-- time and refinements.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS enrichments (
    id                   uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    verified_id          uuid NOT NULL REFERENCES verified(id) ON DELETE CASCADE,
    kind                 text NOT NULL
                           CHECK (kind IN ('alias','merge','cross_source','update','refinement')),
    from_verified_id     uuid REFERENCES verified(id) ON DELETE SET NULL,  -- merged from
    candidate_id         uuid REFERENCES candidates(id),
    alias                text,          -- required when kind = 'alias'
    merged               jsonb,         -- attributes taken from the merged entry
    conflict_resolution  jsonb,         -- how conflicts were resolved
    confidence_delta     real,          -- change in confidence from corroboration
    actor                text NOT NULL, -- who or what enriched it
    notes                text,
    created_at           timestamptz NOT NULL DEFAULT now(),
    CHECK (kind <> 'alias' OR alias IS NOT NULL)
);

-- ---------------------------------------------------------------------------
-- Oversight (optional, for agent-assisted labs): capabilities, proposals, trust.
-- oversight_proposals is the one home for proposed improvements.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS oversight_capabilities (
    id                    uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_name            text NOT NULL,
    capability_type       text NOT NULL,
    trust_score           real NOT NULL DEFAULT 0,
    auto_approve_threshold real,
    requires_review       boolean NOT NULL DEFAULT true,
    UNIQUE (agent_name, capability_type)
);

CREATE TABLE IF NOT EXISTS oversight_proposals (
    id             uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    capability_id  uuid REFERENCES oversight_capabilities(id),
    proposed       jsonb NOT NULL,
    rationale      text,
    status         text NOT NULL DEFAULT 'pending'
                     CHECK (status IN ('pending','approved','rejected','auto_approved','implemented','reverted')),
    created_at     timestamptz NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS oversight_trust_history (
    id             uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    capability_id  uuid REFERENCES oversight_capabilities(id),
    delta          real NOT NULL,
    reason         text,
    created_at     timestamptz NOT NULL DEFAULT now()
);
