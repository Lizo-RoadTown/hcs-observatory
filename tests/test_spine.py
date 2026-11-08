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
    db.execute(SQL)
    a = db.execute("INSERT INTO verified (canonical_key, kind, payload) VALUES ('a','x','{}') RETURNING id").fetchone()[0]
    b = db.execute("INSERT INTO verified (canonical_key, kind, payload) VALUES ('b','x','{}') RETURNING id").fetchone()[0]
    db.execute("INSERT INTO relationships (from_id, to_id, kind, confidence) VALUES (%s,%s,'same_as',0.9)", (a, b))
    with pytest.raises(Exception):
        db.execute("INSERT INTO relationships (from_id, to_id, kind, confidence) VALUES (%s,%s,'same_as',0.5)", (a, b))
    db.execute("INSERT INTO enrichments (verified_id, kind, alias, actor) VALUES (%s,'alias','A',  'r')", (a,))
    with pytest.raises(Exception):
        db.execute("INSERT INTO enrichments (verified_id, kind, actor) VALUES (%s,'alias','r')", (a,))


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
