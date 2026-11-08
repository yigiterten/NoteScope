"""Summarise the (very large) Community Notes ratings files into one row per note.

The raw ratings (about 46 GB) are NOT copied into the database. DuckDB reads the TSV files
once, groups them by note and stores only the summary in the table `note_ratings`.

Usage:
    python scripts/load_ratings.py --files 1    # smoke test: only the first ratings file
    python scripts/load_ratings.py              # all ratings files (may take 10-30 minutes)
    python scripts/load_ratings.py --memory 4GB # lower the memory DuckDB may use (default 4GB)

Table created: note_ratings(note_id, n_ratings, n_raters_approx, n_helpful, n_somewhat_helpful,
                            n_not_helpful, first_rating_ms, last_rating_ms)
"""
import argparse
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import duckdb  # noqa: E402

from notescope.config import DATA_DIR, DB_PATH  # noqa: E402

RATINGS_SQL = """
SELECT TRY_CAST(noteId AS BIGINT)                                   AS note_id,
       COUNT(*)                                                     AS n_ratings,
       approx_count_distinct(raterParticipantId)                    AS n_raters_approx,
       SUM(COALESCE(TRY_CAST(helpful AS INTEGER), 0))               AS n_helpful,
       SUM((helpfulnessLevel = 'SOMEWHAT_HELPFUL')::INTEGER)        AS n_somewhat_helpful,
       SUM(COALESCE(TRY_CAST(notHelpful AS INTEGER), 0))            AS n_not_helpful,
       MIN(TRY_CAST(createdAtMillis AS BIGINT))                     AS first_rating_ms,
       MAX(TRY_CAST(createdAtMillis AS BIGINT))                     AS last_rating_ms
FROM {src}
GROUP BY 1
"""


def read_tsv(files: list[Path]) -> str:
    paths = ", ".join("'" + str(f).replace("'", "''") + "'" for f in files)
    return (
        f"read_csv([{paths}], delim='\\t', quote='', escape='', header=true, "
        "all_varchar=true, union_by_name=true)"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--files", type=int, default=None, help="use only the first N ratings files (smoke test)")
    parser.add_argument("--memory", default="4GB", help="memory limit for DuckDB, e.g. 4GB")
    args = parser.parse_args()

    files = sorted(DATA_DIR.rglob("ratings-*.tsv"))
    if not files:
        sys.exit(f"No ratings-*.tsv files found under {DATA_DIR}. Set NOTESCOPE_DATA_DIR.")
    if args.files:
        files = files[: args.files]
    total_gb = sum(f.stat().st_size for f in files) / 1e9
    print(f"Database : {DB_PATH}")
    print(f"Ratings  : {len(files)} file(s), {total_gb:.1f} GB")

    tmp_dir = DB_PATH.parent / "duckdb_tmp"
    tmp_dir.mkdir(parents=True, exist_ok=True)
    con = duckdb.connect(str(DB_PATH))
    con.execute(f"SET memory_limit = '{args.memory}'")
    con.execute(f"SET temp_directory = '{tmp_dir}'")
    con.execute("SET preserve_insertion_order = false")

    print("Reading and summarising... (the terminal stays quiet until it is done)")
    start = time.time()
    table = "note_ratings"
    con.execute(f"CREATE OR REPLACE TABLE {table} AS {RATINGS_SQL.format(src=read_tsv(files))}")
    rows, ratings = con.execute("SELECT COUNT(*), SUM(n_ratings) FROM note_ratings").fetchone()
    print(f"Done in {(time.time() - start) / 60:.1f} min: {rows:,} notes with ratings, {int(ratings):,} ratings in total")
    if args.files:
        print("Note: this was a partial load (smoke test). Run without --files for the full data.")
    con.close()


if __name__ == "__main__":
    main()
