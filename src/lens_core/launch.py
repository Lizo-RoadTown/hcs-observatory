"""`lens-core` launcher.

Stands up a Lens lab: applies the shared standard (docs/schema/spine.sql) to an injected
database and records which version it applied. The database is INJECTED via LENS_DB_URL
or --db-url, never hardcoded. The base install is standard-library only, so `lens-core
--help` works at once; applying the standard needs the driver extra:
`pip install "lens-core[db]"`.

`lens-core new`:
  * applies the standard to an empty database and records its version;
  * does nothing on a lab already at this version, so it never re-runs the security
    defaults and strips grants a module added later;
  * refuses a database that has other tables, or a different recorded version (upgrades
    are not supported yet);
  * checks afterwards that every table and column the standard declares exists.
Exit codes: 0 done, 1 configuration error, 2 refused or shape problems.
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from importlib import resources
from pathlib import Path

MODULES = ["lens-ingest", "lens-review", "lens-serve", "lens-observe"]
_REPO_STANDARD = Path(__file__).resolve().parents[2] / "docs" / "schema" / "spine.sql"
_CONSTRAINT_WORDS = {"UNIQUE", "FOREIGN", "CHECK", "PRIMARY", "CONSTRAINT", "REFERENCES", "ON"}


def standard_sql() -> str:
    """The standard: bundled in the wheel as lens_core/schema/spine.sql, or read from the
    repo when running from a checkout."""
    bundled = resources.files("lens_core").joinpath("schema", "spine.sql")
    if bundled.is_file():
        return bundled.read_text(encoding="utf-8")
    return _REPO_STANDARD.read_text(encoding="utf-8")


def standard_version(sql: str) -> str:
    m = re.search(r"lens-standard-version:\s*(\S+)", sql)
    if not m:
        raise ValueError("the standard does not state its lens-standard-version")
    return m.group(1)


def expected_columns(sql: str) -> dict[str, set[str]]:
    out: dict[str, set[str]] = {}
    for name, body in re.findall(r"CREATE TABLE IF NOT EXISTS\s+(\w+)\s*\((.*?)\n\);", sql, re.S):
        cols = set()
        for line in body.splitlines():
            m = re.match(r"\s+(\w+)\s+\w", line)
            if m and m.group(1).upper() not in _CONSTRAINT_WORDS:
                cols.add(m.group(1))
        out[name] = cols
    return out


def shape_problems(conn, sql: str) -> list[str]:
    rows = conn.execute("SELECT table_name, column_name FROM information_schema.columns "
                        "WHERE table_schema = 'public'").fetchall()
    have: dict[str, set[str]] = {}
    for table, column in rows:
        have.setdefault(table, set()).add(column)
    problems = []
    for table, cols in expected_columns(sql).items():
        if table not in have:
            problems.append(f"{table}: missing table")
            continue
        problems.extend(f"{table}: missing column {c}" for c in sorted(cols - have[table]))
    return problems


def _public_tables(conn) -> set[str]:
    return {r[0] for r in conn.execute(
        "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public'")}


def _cmd_new(args: argparse.Namespace) -> int:
    url = args.db_url or os.environ.get("LENS_DB_URL")
    if not url:
        print("error: no database. Set LENS_DB_URL or pass --db-url "
              "(the connection is injected, never hardcoded).", file=sys.stderr)
        return 1
    try:
        import psycopg
    except ImportError:
        print('error: applying the standard needs the driver: pip install "lens-core[db]"',
              file=sys.stderr)
        return 1
    sql = standard_sql()
    version = standard_version(sql)
    where = url.split("@")[-1] if "@" in url else "(set)"
    print(f"==> lens-core new: standard {version} -> {where}")
    print(f"    modules: {', '.join(args.modules or MODULES)}")
    with psycopg.connect(url) as conn:
        tables = _public_tables(conn)
        if "standard_version" in tables:
            recorded = {r[0] for r in conn.execute("SELECT version FROM standard_version")}
            if version not in recorded:
                print(f"error: this lab records standard version(s) {sorted(recorded)}, not "
                      f"{version}. Upgrades are not supported yet.", file=sys.stderr)
                return 2
            problems = shape_problems(conn, sql)
            print(f"    already at standard version {version}; nothing applied.")
        elif tables:
            print(f"error: the database is not empty ({len(tables)} table(s) in public, for "
                  f"example {sorted(tables)[0]}). lens-core new only applies the standard to an "
                  "empty database.", file=sys.stderr)
            return 2
        else:
            conn.execute(sql)
            conn.execute("INSERT INTO standard_version (version) VALUES (%s)", (version,))
            problems = shape_problems(conn, sql)
            if problems:
                conn.rollback()
            else:
                print(f"    applied standard {version}.")
    for p in problems:
        print(f"shape problem: {p}", file=sys.stderr)
    return 2 if problems else 0


def _cmd_version(_args: argparse.Namespace) -> int:
    from lens_core import __version__
    print(f"lens-core {__version__} (standard {standard_version(standard_sql())})")
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="lens-core", description="The Lens: launch a lab (the project observatory).")
    subs = p.add_subparsers(dest="command", metavar="<command>")

    new = subs.add_parser("new", help="Apply the shared standard to an empty, injected database.")
    new.add_argument("--db-url", default=None, help="Database URL (default: LENS_DB_URL env).")
    new.add_argument("--modules", nargs="*", default=None,
                     help=f"Modules to compose (default: {', '.join(MODULES)}).")
    new.set_defaults(func=_cmd_new)

    subs.add_parser("version", help="Print version.").set_defaults(func=_cmd_version)

    args = p.parse_args(argv)
    if not getattr(args, "func", None):
        p.print_help()
        return 0
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
