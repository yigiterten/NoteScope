# NoteScope

Do AI-written Community Notes on X reach "Helpful" status more often and faster than human-written ones?

> Status: v0 in progress (target: 21 Oct 2026)

## Business question
X publishes its Community Notes data openly. Some notes are written by AI note writers, others by humans.
NoteScope compares the two: how often notes become "Helpful", and how long it takes.

## Method
- Data: X Community Notes open data (notes, note status history, user enrollment)
- Tools: Python, SQL (DuckDB), pandas, matplotlib
- Pipeline: download -> load into DuckDB -> SQL metrics -> charts

## Findings
_To be added after Session 4._

## Recommendations
_To be added after Session 4._

## Limitations
_To be added after Session 4._

## Data availability and terms
- **Source:** the public Community Notes data from X's "Download data" page (notes, note status history, user enrollment). It is used under the X Developer Agreement and Policy.
- **No raw data in this repo.** Note texts and the raw or processed tables are not published here (see `.gitignore`). To reproduce the analysis, download the files yourself from the page above and point the scripts to your local data folder.
- **Aggregate analysis only.** Results are reported in aggregate. Participant IDs are pseudonymous and are not used to profile individuals.
- **Purpose:** non-commercial research linked to an MSc thesis (UCD, Social Data Science). The project studies the socio-technical dynamics of crowd-sourced verification (consensus and bridging patterns in Community Notes). It does not aim to detect or benchmark rule violations on X.
- **Example notes:** if note texts are shown in reports, they are few, unmodified and attributed as X's display requirements ask.

## Project structure
```
data/raw/        downloaded source files (not tracked by git)
data/processed/  DuckDB database and cleaned tables (not tracked)
sql/             SQL queries
src/notescope/   reusable Python code
notebooks/       exploration
reports/figures/ charts used in the README
scripts/         helper scripts (e.g. check_setup.py)
```

## How to run
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python scripts/check_setup.py

# point to the folder with the downloaded Community Notes TSV files (default: ~/Desktop/Thesis/Community Notes)
export NOTESCOPE_DATA_DIR="/path/to/Community Notes"
python scripts/load_data.py
python scripts/run_sql.py sql/01_overview.sql
```
