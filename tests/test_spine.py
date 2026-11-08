"""The shared standard (docs/schema/spine.sql).

Static tests read the SQL and run everywhere. Database tests apply it to a real, empty
Postgres given by LENS_TEST_DB_URL (CI provides one); they are skipped without it.
"""
import re
from pathlib import Path

import pytest

SPINE = Path(__file__).resolve().parents[1] / "docs" / "schema" / "spine.sql"
SQL = SPINE.read_text(encoding="utf-8")
SCHEMA_DIR = SPINE.parent

# Tables of the reference system the standard was derived from. The standard must not carry
# them (roadmap item spine-neutral-names); the mapping lives in Surveyor's case records.
REFERENCE_TABLES = [
    "staging_extractions", "validation_decisions", "core_entities", "raw_snapshots",
    "core_equivalences", "knowledge_enrichment", "entity_alias", "staging_relationships",
    "kg_relationships", "knowledge_component_relationships", "agent_proposals",
    "improvement_suggestions", "agent_capabilities", "agent_trust_history", "pipeline_runs",
    "knowledge_epistemics",
]


def tables(sql: str) -> list[str]:
    return re.findall(r"CREATE TABLE IF NOT EXISTS\s+(\w+)", sql, re.I)


def test_no_reference_system_names_in_the_standard():
    for path in SCHEMA_DIR.rglob("*"):
        if path.is_file():
            text = path.read_text(encoding="utf-8").lower()
            found = [t for t in REFERENCE_TABLES if re.search(rf"\b{t}\b", text)]
            assert not found, f"{path.name} names reference tables: {found}"


def test_one_table_per_kind_of_data():
    # The five approved one-table choices (Surveyor module-map section 5).
    names = tables(SQL)
    assert len(names) == len(set(names)), "a table is declared twice"
    assert [n for n in names if "relationship" in n] == ["relationships"]
    assert [n for n in names if "alias" in n or "enrich" in n] == ["enrichments"]
    assert [n for n in names if "proposal" in n or "suggestion" in n] == ["oversight_proposals"]
    # Review state is candidates.status plus the latest decision: no second review column.
    assert "review_decision" not in SQL
    # Groups of people belong to access + tenancy, not the spine.
    assert not [n for n in names if n in ("organizations", "teams", "groups")]


def test_every_table_has_a_generated_primary_key():
    for name in tables(SQL):
        body = re.search(rf"CREATE TABLE IF NOT EXISTS\s+{name}\s*\((.*?)\n\);", SQL, re.S | re.I)
        assert body, name
        assert re.search(r"id\s+uuid PRIMARY KEY DEFAULT gen_random_uuid\(\)", body.group(1)), name


def test_guard_refuses_a_database_that_is_not_a_throwaway():
    pytest.importorskip("psycopg")
    from conftest import assert_throwaway
    with pytest.raises(RuntimeError, match="refusing"):
        assert_throwaway("postgresql://u:p@db.example.supabase.co:5432/postgres")
    assert_throwaway("postgresql://u:p@localhost:5432/lens_test")


def test_spine_applies_to_an_empty_database_twice(db):
    db.execute(SQL)
    db.execute(SQL)  # idempotent
    got = {r[0] for r in db.execute(
        "SELECT table_name FROM information_schema.tables WHERE table_schema='public'")}
    assert set(tables(SQL)) <= got


def test_relationships_and_enrichments_hang_off_verified(db):
    _, ca = _seed(db)
    a = _verify(db, ca, _decide(db, ca, "accept"), key="a")
    cb = _candidate(db)
    b = _verify(db, cb, _decide(db, cb, "accept"), key="b")
    db.execute("INSERT INTO relationships (scope_id, from_id, to_id, kind, confidence) "
               "VALUES (%s,%s,%s,'same_as',0.9)", (S1, a, b))
    with pytest.raises(Exception):
        db.execute("INSERT INTO relationships (scope_id, from_id, to_id, kind, confidence) "
                   "VALUES (%s,%s,%s,'same_as',0.5)", (S1, a, b))
    db.execute("INSERT INTO enrichments (scope_id, verified_id, kind, alias, actor) "
               "VALUES (%s,%s,'alias','A','r')", (S1, a))
    with pytest.raises(Exception):
        db.execute("INSERT INTO enrichments (scope_id, verified_id, kind, actor) "
                   "VALUES (%s,%s,'alias','r')", (S1, a))


def test_every_table_starts_closed_in_the_sql():
    # spine-security-defaults: row security on, nothing granted to PUBLIC, no triggers.
    for name in tables(SQL):
        assert re.search(rf"ALTER TABLE {name} ENABLE ROW LEVEL SECURITY;", SQL), name
        assert re.search(rf"REVOKE ALL ON {name} FROM PUBLIC;", SQL), name
    assert "CREATE TRIGGER" not in SQL.upper()


def test_hosted_roles_and_strangers_get_nothing(db):
    for role in ("anon", "authenticated", "lens_probe"):
        db.execute(f"DO $$ BEGIN IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = '{role}') "
                   f"THEN CREATE ROLE {role}; END IF; END $$;")
    # Simulate a host that grants new tables to its API roles by default.
    db.execute("ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT ALL ON TABLES TO anon, authenticated")
    try:
        db.execute(SQL)
        for name in tables(SQL):
            for role in ("anon", "authenticated", "lens_probe"):
                for priv in ("SELECT", "INSERT", "UPDATE", "DELETE"):
                    granted = db.execute("SELECT has_table_privilege(%s, %s, %s)",
                                         (role, f"public.{name}", priv)).fetchone()[0]
                    assert not granted, f"{role} has {priv} on {name}"
            rls = db.execute("SELECT relrowsecurity FROM pg_class WHERE oid = %s::regclass",
                             (f"public.{name}",)).fetchone()[0]
            assert rls, f"row security is off on {name}"
    finally:
        db.execute("ALTER DEFAULT PRIVILEGES IN SCHEMA public REVOKE ALL ON TABLES FROM anon, authenticated")


# ---- review-promotion-contract: every verified entry traces to an accept decision ----

S1 = "11111111-1111-1111-1111-111111111111"
S2 = "22222222-2222-2222-2222-222222222222"


def _candidate(db, scope=S1, source=None):
    return db.execute("INSERT INTO candidates (scope_id, source_id, kind, payload) "
                      "VALUES (%s,%s,'thing','{}') RETURNING id", (scope, source)).fetchone()[0]


def _seed(db, scope=S1):
    db.execute(SQL)
    src = db.execute("INSERT INTO sources (scope_id, uri) VALUES (%s,'doc://a') RETURNING id",
                     (scope,)).fetchone()[0]
    return src, _candidate(db, scope, src)


def _decide(db, cand, action, scope=S1):
    return db.execute("INSERT INTO decisions (scope_id, candidate_id, action, actor) "
                      "VALUES (%s,%s,%s,'reviewer-1') RETURNING id", (scope, cand, action)).fetchone()[0]


def _verify(db, cand, dec, scope=S1, key="k"):
    return db.execute("INSERT INTO verified (scope_id, canonical_key, kind, payload, candidate_id, "
                      "decision_id, verified_by) VALUES (%s,%s,'thing','{}',%s,%s,'reviewer-1') "
                      "RETURNING id", (scope, key, cand, dec)).fetchone()[0]


def test_contract_is_declared_in_the_sql():
    assert re.search(r"UNIQUE \(id, candidate_id, action, scope_id\)", SQL)
    assert re.search(r"FOREIGN KEY \(decision_id, candidate_id, decision_action, scope_id\)\s+REFERENCES "
                     r"decisions \(id, candidate_id, action, scope_id\)", SQL)
    assert "CHECK (decision_action = 'accept')" in SQL


def test_source_to_verified_through_an_accept(db):
    _, cand = _seed(db)
    dec = _decide(db, cand, "accept")
    db.execute("UPDATE candidates SET status = 'accepted' WHERE id = %s", (cand,))
    vid = _verify(db, cand, dec)
    row = db.execute("SELECT v.id FROM verified v JOIN decisions d ON d.id = v.decision_id "
                     "JOIN candidates c ON c.id = v.candidate_id JOIN sources s ON s.id = c.source_id "
                     "WHERE v.id = %s AND d.action = 'accept'", (vid,)).fetchone()
    assert row is not None


def test_verified_needs_a_decision(db):
    _, cand = _seed(db)
    with pytest.raises(Exception):
        db.execute("INSERT INTO verified (scope_id, canonical_key, kind, payload, candidate_id) "
                   "VALUES (%s,'k','thing','{}',%s)", (S1, cand))


def test_a_reject_cannot_be_promoted(db):
    _, cand = _seed(db)
    dec = _decide(db, cand, "reject")
    with pytest.raises(Exception):
        _verify(db, cand, dec)


def test_a_decision_cannot_be_borrowed_from_another_candidate(db):
    src, cand = _seed(db)
    other = _candidate(db, S1, src)
    dec = _decide(db, other, "accept")
    with pytest.raises(Exception):
        _verify(db, cand, dec)


def test_revoke_block_lists_exactly_the_spine_tables():
    # The guarded revoke for hosted API roles is a hand-written list; keep it in step.
    block = re.search(r"FOREACH t IN ARRAY ARRAY\[(.*?)\]", SQL, re.S).group(1)
    listed = re.findall(r"'(\w+)'", block)
    assert listed == tables(SQL)


# ---- spine-scope-column: every row has one scope; nothing points across scopes ----

SCOPED = ["sources", "candidates", "decisions", "verified", "relationships", "enrichments",
          "oversight_capabilities", "oversight_proposals", "oversight_trust_history"]


def _body(name):
    return re.search(rf"CREATE TABLE IF NOT EXISTS\s+{name}\s*\((.*?)\n\);", SQL, re.S).group(1)


def test_every_table_but_the_version_record_has_a_scope():
    assert sorted(SCOPED + ["standard_version"]) == sorted(tables(SQL))
    for name in SCOPED:
        assert re.search(r"^\s+scope_id\s+uuid NOT NULL,", _body(name), re.M), name
    assert "scope_id" not in _body("standard_version")


def test_scope_is_written_by_the_module_not_defaulted():
    assert not re.search(r"scope_id[^,\n]*DEFAULT", SQL)
    assert "current_setting" not in SQL


def test_every_reference_between_spine_tables_carries_the_scope():
    for name in SCOPED:
        body = _body(name)
        # No inline column references: every link is a table-level composite key.
        assert not re.search(r"^\s+\w+\s+uuid[^\n]*REFERENCES", body, re.M), name
        for cols, target in re.findall(r"FOREIGN KEY \(([^)]*)\)\s+REFERENCES\s+(\w+)", body):
            assert "scope_id" in cols, f"{name}: {cols} -> {target}"


def test_a_decision_cannot_point_into_another_scope(db):
    _, cand = _seed(db, S1)
    with pytest.raises(Exception):
        _decide(db, cand, "accept", scope=S2)


def test_a_verified_entry_cannot_use_another_scopes_accept(db):
    _, cand = _seed(db, S1)
    dec = _decide(db, cand, "accept", scope=S1)
    with pytest.raises(Exception):
        _verify(db, cand, dec, scope=S2)


def test_relationships_enrichments_and_supersedes_stay_in_scope(db):
    _, c1 = _seed(db, S1)
    v1 = _verify(db, c1, _decide(db, c1, "accept"), key="one")
    c2 = _candidate(db, S2)
    v2 = _verify(db, c2, _decide(db, c2, "accept", scope=S2), scope=S2, key="two")
    with pytest.raises(Exception):
        db.execute("INSERT INTO relationships (scope_id, from_id, to_id, kind, confidence) "
                   "VALUES (%s,%s,%s,'same_as',0.9)", (S1, v1, v2))
    with pytest.raises(Exception):
        db.execute("INSERT INTO enrichments (scope_id, verified_id, from_verified_id, kind, actor) "
                   "VALUES (%s,%s,%s,'merge','r')", (S1, v1, v2))
    with pytest.raises(Exception):
        db.execute("UPDATE verified SET superseded_by = %s WHERE id = %s", (v2, v1))


def test_canonical_key_is_unique_per_scope_among_current_entries(db):
    _, c1 = _seed(db, S1)
    _verify(db, c1, _decide(db, c1, "accept"), key="x")
    c2 = _candidate(db, S2)
    _verify(db, c2, _decide(db, c2, "accept", scope=S2), scope=S2, key="x")  # other scope: fine
    c3 = _candidate(db, S1)
    with pytest.raises(Exception):
        _verify(db, c3, _decide(db, c3, "accept"), key="x")


def test_a_referenced_row_cannot_change_scope(db):
    _, cand = _seed(db, S1)
    _decide(db, cand, "flag")
    with pytest.raises(Exception):
        db.execute("UPDATE candidates SET scope_id = %s WHERE id = %s", (S2, cand))


def test_crossing_scopes_is_a_new_candidate_in_the_target_scope(db):
    _, c1 = _seed(db, S1)
    _verify(db, c1, _decide(db, c1, "accept"), key="shared-fact")
    src2 = db.execute("INSERT INTO sources (scope_id, uri) VALUES (%s, %s) RETURNING id",
                      (S2, f"lens://{S1}/verified/shared-fact")).fetchone()[0]
    c2 = _candidate(db, S2, src2)
    assert _verify(db, c2, _decide(db, c2, "accept", scope=S2), scope=S2, key="shared-fact")


def test_deleting_a_merged_from_entry_keeps_the_enrichments_scope(db):
    _, c1 = _seed(db, S1)
    keep = _verify(db, c1, _decide(db, c1, "accept"), key="keep")
    c2 = _candidate(db, S1)
    gone = _verify(db, c2, _decide(db, c2, "accept"), key="gone")
    eid = db.execute("INSERT INTO enrichments (scope_id, verified_id, from_verified_id, kind, actor) "
                     "VALUES (%s,%s,%s,'merge','r') RETURNING id", (S1, keep, gone)).fetchone()[0]
    db.execute("DELETE FROM verified WHERE id = %s", (gone,))
    scope, merged_from = db.execute("SELECT scope_id::text, from_verified_id FROM enrichments "
                                    "WHERE id = %s", (eid,)).fetchone()
    assert scope == S1 and merged_from is None
