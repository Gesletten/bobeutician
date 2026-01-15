"""Database utility helpers for maintenance scripts.

Provides a small abstraction for truncating the known tables so the
truncate sequence is not duplicated across multiple scripts.
"""

from sqlalchemy import text


def truncate_tables(db):
    """Disable foreign key checks, truncate tables, re-enable and commit.

    Expects a SQLAlchemy connection/session-like object with `execute`
    and `commit` methods.
    """
    db.execute(text("SET FOREIGN_KEY_CHECKS = 0"))
    db.execute(text("TRUNCATE TABLE product_ingredients"))
    db.execute(text("TRUNCATE TABLE product_skin_types"))
    db.execute(text("TRUNCATE TABLE products"))
    db.execute(text("TRUNCATE TABLE ingredients"))
    db.execute(text("TRUNCATE TABLE skin_types"))
    db.execute(text("SET FOREIGN_KEY_CHECKS = 1"))
    db.commit()
