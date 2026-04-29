import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import pandas as pd
import TableDataTypes

load_dotenv()
table_names = ["historical_figures", "biographies", "historical_events", "qa_pairs"]
create_tables_sql = [
    """
    CREATE TABLE IF NOT EXISTS historical_figures (
        curid BIGINT PRIMARY KEY,
        name TEXT NOT NULL,
        birth_year INT,
        birth_city TEXT,
        country TEXT,
        continent TEXT,
        occupation TEXT,
        industry TEXT,
        domain TEXT,
        gender TEXT
    );
    """,

    """
    CREATE TABLE IF NOT EXISTS biographies (
        curid BIGINT PRIMARY KEY REFERENCES historical_figures(curid),
        name TEXT NOT NULL,
        biography TEXT NOT NULL
    );
    """,

    """
    CREATE TABLE IF NOT EXISTS historical_events (
        id BIGINT PRIMARY KEY,
        event_name TEXT NOT NULL,
        day BIGINT,
        month BIGINT,
        year BIGINT,
        country TEXT,
        event_type TEXT,
        place_name TEXT,
        impact TEXT,
        affected_population TEXT,
        responsible_entity TEXT,
        raw_day TEXT
    );
    """,

    """
    CREATE TABLE IF NOT EXISTS qa_pairs (
        id BIGINT PRIMARY KEY,
        question TEXT NOT NULL,
        answer TEXT NOT NULL,
        time_period TEXT NOT NULL
    );
    """
]
drop_tables_sql = [
    "DROP TABLE IF EXISTS biographies;",
    "DROP TABLE IF EXISTS historical_events;",
    "DROP TABLE IF EXISTS historical_figures;",
    "DROP TABLE IF EXISTS qa_pairs;"
]
DATABASE_URL = os.getenv("DATABASE_URL")

def check_connection():
    if not DATABASE_URL:
        raise ValueError("DATABASE_URL is not set in .env file")

    try:
        engine = create_engine(DATABASE_URL)

        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            print("✅ Successfully connected to Neon/Postgres!")

    except SQLAlchemyError as e:
        print("❌ Database connection failed.")
        print(f"Error: {e}")
        engine = None


def run_sql(engine, query):
    try:
        with engine.connect() as conn:
            conn.execute(text(query))
        print(f"✅ SQL statement executed successfully: {query}")
    except SQLAlchemyError as e:
        print(f"❌ Error executing SQL: {e}")
def run_sql_list(engine, query):
    try:
        with engine.begin() as conn:
            for sql in query:
                conn.execute(text(sql))
        print("✅ SQL statements executed successfully")
    except SQLAlchemyError as e:
        print(f"❌ Error executing SQL: {e}")

def view_tables(engine):
    with engine.connect() as conn:
        result = conn.execute(text("""
                                   SELECT table_name
                                   FROM information_schema.tables
                                   WHERE table_schema = 'public'
                                   """))

        tables = [row[0] for row in result]
        print("Tables in DB:", tables)
def validate_column_names(engine, table_name, df):

    with engine.connect() as conn:
        result = conn.execute(text(f"""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name = '{table_name}'
        """))

        db_cols = {row[0] for row in result}
        df_cols = set(df.columns)

        print("DB columns:", db_cols)
        print("DF columns:", df_cols)
        return db_cols == df_cols

def validate_data_types(engine, table_name, df):
    def normalize_pg_type(pg_type):
        pg_type = pg_type.lower()

        if pg_type in {"smallint", "integer", "bigint"}:
            return "int"
        elif pg_type in {"numeric", "real", "double precision", "decimal"}:
            return "float"
        elif pg_type in {"text", "character varying", "character", "varchar"}:
            return "str"
        elif pg_type in {"boolean"}:
            return "bool"
        elif pg_type in {"date", "timestamp without time zone", "timestamp with time zone"}:
            return "datetime"
        else:
            return pg_type
    def normalize_pd_type(pd_dtype):
        if pd.api.types.is_integer_dtype(pd_dtype):
            return "int"
        elif pd.api.types.is_float_dtype(pd_dtype):
            return "float"
        elif pd.api.types.is_bool_dtype(pd_dtype):
            return "bool"
        elif pd.api.types.is_datetime64_any_dtype(pd_dtype):
            return "datetime"
        else:
            return "str"

    with engine.connect() as conn:
        result = conn.execute(text("""
                                   SELECT column_name, data_type
                                   FROM information_schema.columns
                                   WHERE table_name = :table_name
                                     AND table_schema = 'public'
                                   """), {"table_name": table_name})

        db_schema = {row[0]: normalize_pg_type(row[1]) for row in result}
        df_schema = {col: normalize_pd_type(df[col].dtype) for col in df.columns}

        db_cols = set(db_schema.keys())
        df_cols = set(df_schema.keys())

        missing_in_df = db_cols - df_cols
        extra_in_df = df_cols - db_cols

        common_cols = db_cols & df_cols
        type_conflicts = {}

        for col in common_cols:
            if db_schema[col] != df_schema[col]:
                type_conflicts[col] = {
                    "db_type": db_schema[col],
                    "df_type": df_schema[col]
                }

        print("DB schema:", db_schema)
        print("DF schema:", df_schema)

        if missing_in_df:
            print("\n❌ Missing in DF:", missing_in_df)
        if extra_in_df:
            print("\n❌ Extra in DF:", extra_in_df)
        if type_conflicts:
            print("\n Type conflicts:")
            for col, types in type_conflicts.items():
                print(f"  - {col}: DB={types['db_type']} | DF={types['df_type']}")

        is_valid = not missing_in_df and not extra_in_df and not type_conflicts

        if is_valid:
            print("\n✅ Schema matches")
        else:
            print("\n❌ Schema validation failed")

        return {
            "is_valid": is_valid,
            "missing_in_df": missing_in_df,
            "extra_in_df": extra_in_df,
            "type_conflicts": type_conflicts,
            "db_schema": db_schema,
            "df_schema": df_schema
        }
def add_data_to_table(engine, table_name, data_source ,is_df = False):

    if is_df:
        df = data_source
    else:
        df = pd.read_csv(data_source)

    if not validate_column_names(engine, table_name, df):
        print("❌ Column mismatch detected")
        return
    print(validate_data_types(engine, table_name, df))
    print("*"*30)
    df.to_sql(table_name, engine, if_exists="append", index=False)
    print("DATA UPLOADED SUCCESSFULLY")
    print("Table Head:")
    preview_table(engine, table_name)

def preview_table(engine, table_name, limit=10):
    with engine.connect() as conn:
        result = conn.execute(text(f"SELECT * FROM {table_name} LIMIT 10"))
        print(result.fetchall())
def main():
    # only need to create once
    engine = create_engine(DATABASE_URL)
    check_connection()

    df_qa1 = pd.read_json("data/qa1_clean.jsonl", lines=True)
    df_qa2 = pd.read_json("data/qa2_clean.jsonl", lines=True)

    max_id = df_qa1["id"].max()

    df_qa2["id"] = range(max_id + 1, max_id + 1 + len(df_qa2))

    # Combine
    df_qa = pd.concat([df_qa1, df_qa2], ignore_index=True)

    add_data_to_table(engine, "qa_pairs", df_qa, is_df = True)

    # run_sql_list(engine, create_tables_sql)

    # run_sql(engine, drop_tables_sql[3])

    # add_data_to_table(engine, "historical_figures", "data/historical_figures.csv")
    # add_data_to_table(engine, "historical_events", "data/historical_events_core.csv")

main()