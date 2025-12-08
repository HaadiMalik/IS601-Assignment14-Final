# database.py = 16-20
from app.database import get_db


def test_get_db_generator_smoke():
    gen = get_db()
    session = next(gen)
    assert session is not None
    # close generator to trigger finally clause
    gen.close()
