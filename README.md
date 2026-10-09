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
```
