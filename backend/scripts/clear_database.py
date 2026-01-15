"""Clear database script - just deletes all data without reseeding."""

import sys
import os

from sqlalchemy.exc import SQLAlchemyError
from app.db.models import Product, Ingredient, SkinType
from app.db.session import SessionLocal, engine
from app.db.models import Base
from scripts._db_utils import truncate_tables

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def clear_database():
    """Clear all data from database"""
    print("CLEARING DATABASE - Deleting all data...")
    print("=" * 40)

    try:
        db = SessionLocal()

        # Method 1: Try SQL TRUNCATE (fastest)
        try:
            print("1. Attempting SQL TRUNCATE...")

            truncate_tables(db)
            print("TRUNCATE successful")

        except SQLAlchemyError as e:
            print(f"   TRUNCATE failed: {e}")
            db.rollback()

            # Method 2: Drop and recreate tables
            print("2. Falling back to DROP/CREATE...")
            db.close()
            Base.metadata.drop_all(bind=engine)
            Base.metadata.create_all(bind=engine)
            print("   DROP/CREATE successful")
            db = SessionLocal()

        # Verify it's empty
        print("3. Verifying empty database...")

        product_count = db.query(Product).count()
        ingredient_count = db.query(Ingredient).count()
        skin_type_count = db.query(SkinType).count()

        if product_count == 0 and ingredient_count == 0 and skin_type_count == 0:
            print("Database is completely empty")
            print("\nDatabase cleared successfully!")
            return True

        # If we reach here there is still data in the DB
        print(
            f"Still has data: {product_count} products, {ingredient_count} ingredients"
        )
        return False

    except SQLAlchemyError as e:
        print(f"Clear failed (SQLAlchemyError): {e}")
        return False
    finally:
        if "db" in locals():
            db.close()


if __name__ == "__main__":
    clear_database()
