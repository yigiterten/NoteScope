"""Create the README charts from the DuckDB database.

Usage:
    python scripts/make_figures.py
Writes PNG files into reports/figures/.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

import duckdb  # noqa: E402
import matplotlib  # noqa: E402

matplotlib.use("Agg")  # draw to files, no window needed
import matplotlib.pyplot as plt  # noqa: E402

from notescope.config import DB_PATH, REPO_ROOT  # noqa: E402

OUT = REPO_ROOT / "reports" / "figures"
OUT.mkdir(parents=True, exist_ok=True)

COLORS = {"AI": "#2F5BD3", "Other": "#8A93A3"}

con = duckdb.connect(str(DB_PATH), read_only=True)

# Same logic as sql/02_helpful_rate_by_month.sql
monthly = con.sql("""
    SELECT date_trunc('month', created_at) AS month, author_group,
           COUNT(*) AS notes,
           100.0 * AVG(is_helpful_now::INTEGER) AS pct_helpful_now
    FROM note_facts
    WHERE created_ms >= (SELECT MIN(created_ms) FROM note_facts WHERE author_group = 'AI')
    GROUP BY month, author_group
    ORDER BY month, author_group
""").df()

# Figure 1: share of notes currently rated Helpful, by creation month
fig, ax = plt.subplots(figsize=(9, 4.5))
for group, df in monthly.groupby("author_group"):
    ax.plot(df["month"], df["pct_helpful_now"], marker="o", label=group, color=COLORS[group])
ax.set_title("Share of notes currently rated Helpful, by month the note was written")
ax.set_ylabel("% of notes rated Helpful")
ax.set_ylim(bottom=0)
ax.grid(alpha=0.3)
ax.legend(title="Author group")
fig.text(0.01, 0.01, "AI = accounts with enrollment state apiEarnedIn (current state). Latest months are still maturing.",
         fontsize=7, color="gray")
fig.tight_layout(rect=(0, 0.03, 1, 1))
fig.savefig(OUT / "helpful_rate_by_month.png", dpi=150)

# Figure 2: how many notes per month, by group
pivot = monthly.pivot(index="month", columns="author_group", values="notes").fillna(0)
fig, ax = plt.subplots(figsize=(9, 4.5))
ax.bar(pivot.index, pivot["Other"], width=20, label="Other", color=COLORS["Other"])
ax.bar(pivot.index, pivot["AI"], width=20, bottom=pivot["Other"], label="AI", color=COLORS["AI"])
ax.set_title("Notes written per month")
ax.set_ylabel("Number of notes")
ax.grid(axis="y", alpha=0.3)
ax.legend(title="Author group")
fig.tight_layout()
fig.savefig(OUT / "notes_per_month.png", dpi=150)

print("Saved:")
for p in sorted(OUT.glob("*.png")):
    print(" ", p.relative_to(REPO_ROOT))
