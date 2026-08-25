from sqlalchemy import text

def test_postgres_is_reachable(postgres_available):
    with postgres_available.connect() as conn:
        assert conn.execute(text("SELECT 1")).scalar_one() == 1
