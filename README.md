# NoteScope

Do AI-written Community Notes on X reach "Helpful" status more often and faster than human-written ones?

> Status: v0.1 (Nov 2026): v0 analysis plus note-level rating counts and time to first rating. Next: survival analysis.

## Business question
X publishes its Community Notes data openly. Some notes are written by AI note writers, others by humans.
NoteScope compares the two: how often notes become "Helpful", and how long it takes.

## Method
- Data: X Community Notes open data (notes, note status history, user enrollment, ratings)
- Tools: Python, SQL (DuckDB), pandas, matplotlib
- Pipeline: download -> load into DuckDB (the 46 GB of ratings are summarised to one row per note, not copied) -> SQL metrics -> charts

## Findings
Data snapshot: 3.19M notes, 3.40M note-status records, 39 AI writer accounts (enrollment state `apiEarnedIn`), 331k AI notes vs 3.07M other notes. Comparison window: from the first AI note (Sep 2025) onward.

![Share of notes currently rated Helpful, by month](reports/figures/helpful_rate_by_month.png)

1. **AI notes are rated Helpful more often than other notes in every month since Sep 2025** (14 of 14 months). Over all time: 10.7% of AI notes vs 8.2% of other notes are currently Helpful. The AI notes' share of "Not Helpful" is lower too (1.0% vs 4.4%).
2. **The gap has narrowed.** In Oct 2025 to Feb 2026 AI notes reached about 18-22% Helpful against 8-10% for other notes. Since Apr 2026, when AI note volume jumped (7k notes in Feb to 37k in Apr and 44-54k per month after), the rates are about 9-10% vs 5-7%.
3. **Speed to Helpful is about the same.** Median time from writing to first Helpful status is 8.5 hours for AI notes and 8.1 hours for other notes (90th percentile 55 vs 51 hours). AI notes reach "Not Helpful" faster at the median (2.4 vs 3.3 hours) but slower in the tail (33.5 vs 23.3 hours at the 90th percentile).
4. **Most notes in both groups are still undecided** (about 88% "Needs More Ratings").

### v0.1: ratings
Ratings data: 241.6M ratings on 3.36M notes (nearly all notes).

![Median ratings per note, by month](reports/figures/ratings_per_note_by_month.png)

5. **AI notes receive fewer ratings than other notes since spring 2026.** In the comparison window the median AI note has 10 ratings against 21 for other notes (90th percentile 62 vs 182). The monthly view compares notes of the same month (so the same time to collect ratings): until Feb 2026 AI notes got as many or more ratings (for example 29 vs 26 in Dec 2025), from Apr 2026 they get about 8-10 against 14-18. The change coincides with the jump in AI note volume (7k notes in Feb, 37k in Apr), but this data cannot say why.
6. **The first rating arrives equally fast.** Median time from writing to the first rating is about 10 minutes for AI notes (0.17 hours) and 9 minutes for other notes (0.15 hours), 90th percentile 2.6 vs 2.4 hours.
7. **AI notes reach a decision with fewer ratings.** Notes that are currently Helpful have a median of 47 ratings for AI notes and 73 for other notes. This only describes notes that already reached a status.

Queries: `sql/01_overview.sql` to `sql/07_ratings_quality.sql`. Figures: `python scripts/make_figures.py`.

## Recommendations
- Treat the Helpful-rate advantage of AI notes as real but shrinking, and monitor it as AI volume grows: quality per note may fall as volume rises.
- Compare AI and human notes on the same tweets (matched design) before drawing causal conclusions. The groups may choose different posts.
- For speed, report time to first Helpful status together with the share of notes that never leave "Needs More Ratings", since the timing statistic only covers decided notes.

## Limitations
- **Descriptive, not causal.** AI and human writers may pick different tweets, topics and moments. Nothing here controls for that.
- **AI group is defined by current account state.** `apiEarnedIn` is the enrollment state at the time of the data snapshot, not at writing time. Accounts that lost or never earned that status are not counted as AI.
- **Current status only.** The Helpful share uses each note's status now. A note that was Helpful and later lost the status counts as not Helpful.
- **Recent months are immature.** Newer notes have had less time to collect ratings, so the latest months look lower for both groups.
- **Timing covers decided notes only.** Hours to first non-"Needs More Ratings" status exist only for notes that left that state.
- **Incomplete joins.** 13% of status records have no row in the notes files (likely deleted notes), and 5% of status records come from authors missing in the enrollment file. The latter are counted as "Other".
- **Ratings summary.** Rating counts include every rating row. For about 1% of AI notes and 3% of other notes the count is clearly above the number of distinct raters (people changing their rating). The distinct-rater count is approximate (HyperLogLog). Medians are almost identical for both measures. 2.7% of rated notes have no status record and are left out.
- **Data lag.** The public files are daily snapshots published with a delay of about 48 hours.

## Data availability and terms
- **Source:** the public Community Notes data from X's "Download data" page (notes, note status history, user enrollment, ratings). It is used under the X Developer Agreement and Policy.
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
scripts/         load_data.py, load_ratings.py, run_sql.py, make_figures.py, check_setup.py
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
python scripts/load_ratings.py   # summarises the ratings files (a few minutes)
python scripts/make_figures.py   # writes charts to reports/figures/
```
