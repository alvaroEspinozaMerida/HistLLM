#utility functions for getting engine and loading data
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from datasets import Dataset
import pandas as pd
import os

def get_engine(database_url: str | None = None):
    load_dotenv()

    db_url = database_url or os.getenv("DATABASE_URL")

    if not db_url:
        raise ValueError("DATABASE_URL not found in .env")

    db_url = db_url.strip().strip('"').strip("'")

    return create_engine(db_url)


def load_table_as_dataset(engine, table_name: str, columns=None):
    if columns:
        column_sql = ", ".join(columns)
    else:
        column_sql = "*"

    query = text(f"SELECT {column_sql} FROM {table_name}")

    df = pd.read_sql(query, engine)

    return Dataset.from_pandas(df, preserve_index=False)