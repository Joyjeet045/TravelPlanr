import os
import shutil
import sqlite3
import pandas as pd
import requests

db_url = "https://storage.googleapis.com/benchmarks-artifacts/travel-db/travel2.sqlite"
local_file = "travel2.sqlite"
backup_file = "travel2.backup.sqlite"
overwrite = False
if overwrite or not os.path.exists(local_file):
    response = requests.get(db_url)
    response.raise_for_status()
    with open(local_file, "wb") as f:
        f.write(response.content)
    shutil.copy(local_file, backup_file)

def update_dates(file):
    """Update all datetime-like columns in every table to be current and realistic for testing."""
    shutil.copy(backup_file, file)
    conn = sqlite3.connect(file)
    cursor = conn.cursor()
    tables = pd.read_sql(
        "SELECT name FROM sqlite_master WHERE type='table';", conn
    ).name.tolist()
    tdf = {}
    for t in tables:
        tdf[t] = pd.read_sql(f"SELECT * from {t}", conn)
    example_times = []
    for df in tdf.values():
        for col in df.columns:
            try:
                dt = pd.to_datetime(df[col].replace("\\N", pd.NaT), errors='coerce')
                if dt.notna().any():
                    example_times.append(dt.max())
            except Exception:
                continue
    example_times = [t for t in example_times if pd.notna(t)]
    if not example_times:
        raise ValueError("No datetime columns found in any table!")
    example_time = max(example_times)
    current_time = pd.to_datetime("now").tz_localize(example_time.tz) if hasattr(example_time, 'tz') and example_time.tz else pd.to_datetime("now")
    time_diff = current_time - example_time
    for table_name, df in tdf.items():
        for col in df.columns:
            try:
                dt = pd.to_datetime(df[col].replace("\\N", pd.NaT), errors='coerce')
                if dt.notna().any():
                    new_col = dt + time_diff
                    mask = dt.notna()
                    df.loc[mask, col] = new_col[mask].astype(str)
            except Exception:
                continue
        df.to_sql(table_name, conn, if_exists="replace", index=False)
    conn.commit()
    conn.close()
    return file

db = update_dates(local_file) 