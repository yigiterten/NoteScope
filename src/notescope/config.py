"""Project paths.

The raw Community Notes files are NOT part of this repository (see README, "Data availability and terms").
Point NOTESCOPE_DATA_DIR at the folder that holds the downloaded TSV files; subfolders are searched too.
"""
import os
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]

_default_data_dir = Path.home() / "Desktop" / "Thesis" / "Community Notes"
DATA_DIR = Path(os.environ.get("NOTESCOPE_DATA_DIR", _default_data_dir)).expanduser()

DB_PATH = REPO_ROOT / "data" / "processed" / "notescope.duckdb"
