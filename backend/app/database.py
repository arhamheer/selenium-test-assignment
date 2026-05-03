from sqlalchemy import create_engine, text
from sqlalchemy.engine import make_url
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import os
import re

# Database URL - read from environment variable
DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    "postgresql://postgres:pajay6205@localhost:5432/taskflow_db",
)


def ensure_postgres_database_exists(database_url: str):
    try:
        parsed_url = make_url(database_url)
    except Exception:
        return

    if parsed_url.get_backend_name() != "postgresql" or not parsed_url.database:
        return

    database_name = parsed_url.database
    admin_url = parsed_url.set(database="postgres")
    admin_engine = create_engine(admin_url, isolation_level="AUTOCOMMIT")

    try:
        with admin_engine.connect() as connection:
            exists = connection.execute(
                text("SELECT 1 FROM pg_database WHERE datname = :database_name"),
                {"database_name": database_name},
            ).scalar()

            if not exists:
                if not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", database_name):
                    raise ValueError(
                        f"Unsupported database name for auto-creation: {database_name}"
                    )

                connection.execute(text(f'CREATE DATABASE "{database_name}"'))
                print(f"Created missing PostgreSQL database: {database_name}")
    except Exception as error:
        print(f"Warning: Could not ensure PostgreSQL database exists: {error}")
    finally:
        admin_engine.dispose()


ensure_postgres_database_exists(DATABASE_URL)

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Dependency to get DB session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()