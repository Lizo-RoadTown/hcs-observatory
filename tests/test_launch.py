"""lens-core new: applies the standard to an injected database (roadmap item launcher-applies-spine)."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from lens_core import launch  # noqa: E402


def test_standard_text_and_version_are_found():
    sql = launch.standard_sql()
    assert "CREATE TABLE IF NOT EXISTS verified" in sql
    assert launch.standard_version(sql)


def test_expected_columns_are_read_from_the_standard():
    cols = launch.expected_columns(launch.standard_sql())
    assert {"candidate_id", "decision_id", "decision_action"} <= cols["verified"]
    assert "id" in cols["sources"] and "UNIQUE" not in cols["decisions"]


def test_no_database_is_an_error(monkeypatch, capsys):
    monkeypatch.delenv("LENS_DB_URL", raising=False)
    assert launch.main(["new"]) == 1
    assert "LENS_DB_URL" in capsys.readouterr().err


def _tables(db):
    return {r[0] for r in db.execute(
        "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")}


def test_new_applies_once_then_is_a_no_op(db, db_url, capsys):
    assert launch.main(["new", "--db-url", db_url]) == 0
    assert set(launch.expected_columns(launch.standard_sql())) <= _tables(db)
    assert launch.main(["new", "--db-url", db_url]) == 0
    assert "already at standard version" in capsys.readouterr().out
    assert db.execute("SELECT count(*) FROM standard_version").fetchone()[0] == 1


def test_second_run_keeps_access_grants(db, db_url):
    assert launch.main(["new", "--db-url", db_url]) == 0
    db.execute("DO $$ BEGIN IF NOT EXISTS (SELECT 1 FROM pg_roles WHERE rolname = 'lens_reader') "
               "THEN CREATE ROLE lens_reader; END IF; END $$;")
    db.execute("GRANT SELECT ON verified TO lens_reader")
    assert launch.main(["new", "--db-url", db_url]) == 0
    assert db.execute("SELECT has_table_privilege('lens_reader', 'public.verified', 'SELECT')").fetchone()[0]


def test_refuses_a_database_that_is_not_empty(db, db_url, capsys):
    db.execute("CREATE TABLE something_else (id int)")
    assert launch.main(["new", "--db-url", db_url]) == 2
    assert "not empty" in capsys.readouterr().err
    assert "verified" not in _tables(db)


def test_refuses_a_different_recorded_version(db, db_url, capsys):
    assert launch.main(["new", "--db-url", db_url]) == 0
    db.execute("UPDATE standard_version SET version = '0.0.0-old'")
    assert launch.main(["new", "--db-url", db_url]) == 2
    assert "upgrade" in capsys.readouterr().err


def test_shape_check_reports_missing_columns(db, db_url):
    assert launch.main(["new", "--db-url", db_url]) == 0
    db.execute("ALTER TABLE verified DROP COLUMN provenance")
    import psycopg
    with psycopg.connect(db_url) as conn:
        problems = launch.shape_problems(conn, launch.standard_sql())
    assert problems == ["verified: missing column provenance"]
