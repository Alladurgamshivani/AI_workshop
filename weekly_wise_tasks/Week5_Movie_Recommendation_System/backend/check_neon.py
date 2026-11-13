
from pathlib import Path
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Load the root .env file
env_path = Path(__file__).resolve().parents[1] / ".env"
load_dotenv(env_path, override=True)

database_url = os.getenv("DATABASE_URL")

if not database_url:
    raise ValueError("DATABASE_URL not found")

engine = create_engine(database_url)

with engine.connect() as connection:
    print("DATABASE:", connection.execute(
        text("SELECT current_database()")
    ).scalar())

    print("HOST:", connection.execute(
        text("SELECT inet_server_addr()")
    ).scalar())

    tables = connection.execute(text("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
        ORDER BY table_name
    """)).fetchall()

    print("TABLES:", [row[0] for row in tables])

    for table in ["movies", "users", "ratings"]:
        count = connection.execute(
            text(f"SELECT COUNT(*) FROM {table}")
        ).scalar() if table in [row[0] for row in tables] else "Table missing"

        print(f"{table.upper()}:", count)
from sqlalchemy import text

with engine.connect() as connection:
    result = connection.execute(text("""
        SELECT
            current_database(),
            current_user,
            inet_server_addr(),
            inet_server_port(),
            version()
    """))

    print("CONNECTION DETAILS:", result.fetchone())