from functools import lru_cache
import sqlite3

import pandas as pd


@lru_cache(maxsize=8)
def query_database(sql: str) -> pd.DataFrame:
    conn = sqlite3.connect("data/nba.sqlite")
    df = pd.read_sql_query(sql, conn)
    return df
