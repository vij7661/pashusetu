import os
import pytest
from sqlalchemy import create_engine, text

TEST_DATABASE_URL = os.getenv("DATABASE_URL")


@pytest.fixture(scope="session")
def postgres_available():
    if not TEST_DATABASE_URL:
        pytest.skip("DATABASE_URL not configured for PostgreSQL integration tests.")
    engine = create_engine(TEST_DATABASE_URL, pool_pre_ping=True)
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
    except Exception:
        pytest.skip("PostgreSQL integration database unavailable.")
    return engine
