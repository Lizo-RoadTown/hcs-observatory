"""Shared test setup: a guarded, throwaway Postgres for database tests.

Database tests use the `db` fixture. It connects to LENS_TEST_DB_URL and wipes the public
schema, so it refuses any database whose name does not contain "test". Without the URL the
tests skip, unless LENS_REQUIRE_DB_TESTS=1 (set in CI), which turns a skip into a failure.
"""
import os

import pytest

DB_URL = os.environ.get("LENS_TEST_DB_URL")
REQUIRE_DB = os.environ.get("LENS_REQUIRE_DB_TESTS") == "1"


def database_name(url: str) -> str:
    from psycopg.conninfo import conninfo_to_dict
    return conninfo_to_dict(url).get("dbname") or ""


def assert_throwaway(url: str) -> None:
    name = database_name(url)
    if "test" not in name.lower():
        raise RuntimeError(
            f"refusing to wipe database {name!r}: LENS_TEST_DB_URL must name a throwaway "
            "database whose name contains 'test'")


def _unavailable(reason: str):
    if REQUIRE_DB:
        pytest.fail(f"database tests are required here but cannot run: {reason}")
    pytest.skip(reason)


@pytest.fixture
def db_url():
    if not DB_URL:
        _unavailable("LENS_TEST_DB_URL not set (CI provides a Postgres)")
    try:
        import psycopg  # noqa: F401
    except ImportError:
        _unavailable("psycopg is not installed")
    assert_throwaway(DB_URL)
    return DB_URL


@pytest.fixture
def db(db_url):
    import psycopg
    with psycopg.connect(db_url, autocommit=True) as conn:
        conn.execute("DROP SCHEMA public CASCADE; CREATE SCHEMA public;")
        yield conn
