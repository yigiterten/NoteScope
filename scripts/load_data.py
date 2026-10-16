"""Load the Community Notes TSV files into a local DuckDB database.

Usage:
    python scripts/load_data.py                 # full load (a few minutes)
    python scripts/load_data.py --sample 50000  # quick smoke test: first 50,000 rows per table

Tables created: enrollment, note_status, notes. View created: note_facts.
"""
import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import duckdb  # noqa: E402

from notescope.config import DATA_DIR, DB_PATH  # noqa: E402


def find_files(pattern: str) -> list[Path]:
    return sorted(DATA_DIR.rglob(pattern))


def read_tsv(files: list[Path]) -> str:
    """DuckDB read_csv call for tab-separated files with a header row.
    quote='' means quotes inside note texts are kept as plain characters."""
    paths = ", ".join("'" + str(f).replace("'", "''") + "'" for f in files)
    return (
        f"read_csv([{paths}], delim='\\t', quote='', escape='', header=true, "
        "all_varchar=true, union_by_name=true)"
    )


def build_table(con, name: str, select_sql: str, files: list[Path], limit: int | None) -> None:
    start = time.time()
    tail = f" LIMIT {limit}" if limit else ""
    con.execute(f"CREATE OR REPLACE TABLE {name} AS {select_sql.format(src=read_tsv(files))}{tail}")
    rows = con.execute(f"SELECT COUNT(*) FROM {name}").fetchone()[0]
    print(f"  {name:<12} {rows:>10,} rows  ({time.time() - start:.0f}s, {len(files)} file(s))")


ENROLLMENT_SQL = """
SELECT participantId                                        AS participant_id,
       enrollmentState                                      AS enrollment_state,
       TRY_CAST(timestampOfLastStateChange AS BIGINT)       AS last_state_change_ms,
       modelingPopulation                                   AS modeling_population
FROM {src}
"""

NOTE_STATUS_SQL = """
SELECT TRY_CAST(noteId AS BIGINT)                                        AS note_id,
       noteAuthorParticipantId                                           AS author_id,
       TRY_CAST(createdAtMillis AS BIGINT)                               AS created_ms,
       NULLIF(firstNonNMRStatus, '')                                     AS first_non_nmr_status,
       TRY_CAST(NULLIF(timestampMillisOfFirstNonNMRStatus, '') AS BIGINT) AS first_non_nmr_ms,
       currentStatus                                                     AS current_status,
       TRY_CAST(NULLIF(timestampMillisOfCurrentStatus, '') AS BIGINT)    AS current_status_ms,
       NULLIF(lockedStatus, '')                                          AS locked_status,
       currentDecidedBy                                                  AS current_decided_by
FROM {src}
"""

NOTES_SQL = """
SELECT TRY_CAST(noteId AS BIGINT)                  AS note_id,
       noteAuthorParticipantId                     AS author_id,
       TRY_CAST(createdAtMillis AS BIGINT)         AS created_ms,
       TRY_CAST(tweetId AS BIGINT)                 AS tweet_id,
       classification,
       TRY_CAST(trustworthySources AS INTEGER)     AS trustworthy_sources,
       TRY_CAST(isMediaNote AS INTEGER)            AS is_media_note,
       TRY_CAST(isCollaborativeNote AS INTEGER)    AS is_collaborative_note,
       summary
FROM {src}
"""

# One row per note with the author group. 'AI' = author account is enrolled as apiEarnedIn
# (AI Note Writer API). The enrollment state is the account's CURRENT state, not its state at writing time.
NOTE_FACTS_VIEW = """
CREATE OR REPLACE VIEW note_facts AS
SELECT s.note_id,
       s.author_id,
       s.created_ms,
       epoch_ms(s.created_ms)                                          AS created_at,
       CASE WHEN e.enrollment_state = 'apiEarnedIn' THEN 'AI' ELSE 'Other' END AS author_group,
       s.current_status,
       s.first_non_nmr_status,
       (s.current_status = 'CURRENTLY_RATED_HELPFUL')                  AS is_helpful_now,
       (s.first_non_nmr_status = 'CURRENTLY_RATED_HELPFUL')            AS first_status_helpful,
       (s.first_non_nmr_ms - s.created_ms) / 3600000.0                 AS hours_to_first_status
FROM note_status s
LEFT JOIN enrollment e ON e.participant_id = s.author_id
"""


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--sample", type=int, default=None, help="load only the first N rows of each table (smoke test)")
    args = parser.parse_args()

    print(f"Data folder : {DATA_DIR}")
    print(f"Database    : {DB_PATH}")
    enrollment_files = find_files("userEnrollment-*.tsv")
    status_files = find_files("noteStatusHistory-*.tsv")
    notes_files = find_files("notes-*.tsv")
    for label, files in [("userEnrollment", enrollment_files), ("noteStatusHistory", status_files), ("notes", notes_files)]:
        if not files:
            sys.exit(f"No {label}-*.tsv files found under {DATA_DIR}. Set NOTESCOPE_DATA_DIR to the folder with the downloaded files.")
        print(f"Found {len(files)} {label} file(s)")

    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(DB_PATH))
    print("Loading...")
    build_table(con, "enrollment", ENROLLMENT_SQL, enrollment_files, args.sample)
    build_table(con, "note_status", NOTE_STATUS_SQL, status_files, args.sample)
    build_table(con, "notes", NOTES_SQL, notes_files, args.sample)
    con.execute(NOTE_FACTS_VIEW)
    ai = con.execute("SELECT COUNT(*) FROM enrollment WHERE enrollment_state = 'apiEarnedIn'").fetchone()[0]
    print(f"Done. AI writer accounts (apiEarnedIn): {ai}")
    con.close()


if __name__ == "__main__":
    main()
