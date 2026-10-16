"""Run a .sql file against the NoteScope DuckDB database and print each result.

Usage:
    python scripts/run_sql.py sql/01_overview.sql
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import duckdb  # noqa: E402

from notescope.config import DB_PATH  # noqa: E402


def main() -> None:
    if len(sys.argv) != 2:
        sys.exit("usage: python scripts/run_sql.py sql/01_overview.sql")
    if not DB_PATH.exists():
        sys.exit(f"Database not found at {DB_PATH}. Run: python scripts/load_data.py")
    con = duckdb.connect(str(DB_PATH), read_only=True)
    text = Path(sys.argv[1]).read_text(encoding="utf-8")
    for statement in (s.strip() for s in text.split(";")):
        code_lines = [line for line in statement.splitlines() if line.strip() and not line.strip().startswith("--")]
        if not code_lines:
            continue
        print()
        con.sql(statement).show(max_width=200, max_rows=60)


if __name__ == "__main__":
    main()
