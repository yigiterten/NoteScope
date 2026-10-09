"""Quick sanity check: are Python, DuckDB and pandas working?"""
import sys

import duckdb
import pandas as pd

print("Python :", sys.version.split()[0])
print("DuckDB :", duckdb.__version__)
print("pandas :", pd.__version__)

# Run a tiny SQL query on an in-memory database
result = duckdb.sql("SELECT 'NoteScope is ready' AS message, 42 AS answer").df()
print(result)
