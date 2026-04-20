import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
load_dotenv()

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
        biography TEXT NOT NULL
    );
    """,

    """
    CREATE TABLE IF NOT EXISTS historical_events (
        id BIGINT PRIMARY KEY,
        event_name TEXT NOT NULL,
        day INT,
        month INT,
        year INT,
        country TEXT,
        event_type TEXT,
        place_name TEXT,
        impact TEXT,
        affected_population TEXT,
        responsible_entity TEXT,
        outcome TEXT
    );
    """,

    """
    CREATE TABLE IF NOT EXISTS qa_pairs (
        id BIGINT PRIMARY KEY,
        question TEXT NOT NULL,
        answer TEXT NOT NULL,
        dataset_name TEXT NOT NULL,
        time_period TEXT NOT NULL
    );
    """
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

def create_table(engine, query):
    try:
        with engine.begin() as conn:
            conn.execute(text(query))
        print("✅ All tables created successfully")

    except SQLAlchemyError as e:
        print("❌ Error creating tables:", e)

def view_tables(engine):
    with engine.connect() as conn:
        result = conn.execute(text("""
                                   SELECT table_name
                                   FROM information_schema.tables
                                   WHERE table_schema = 'public'
                                   """))

        tables = [row[0] for row in result]
        print("Tables in DB:", tables)


def main():
    # only need to create once
    engine = create_engine(DATABASE_URL)
    # for i in create_tables_sql:
    #     create_table(engine, i)

    view_tables(engine)
main()