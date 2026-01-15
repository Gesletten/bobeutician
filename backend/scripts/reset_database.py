"""Reset and repopulate database script.

Completely clears the database and reseeds with fresh CSV data.
"""

import sys
import os
from sqlalchemy.exc import SQLAlchemyError
from app.db.session import engine, SessionLocal
from app.db.models import Base, Product, Ingredient, SkinType
from scripts.seed_db import seed_data
from scripts._db_utils import truncate_tables

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def reset_database():
    """Complete database reset and reseed"""
    print("RESETTING DATABASE - This will delete ALL data!")
    print("=" * 50)

    try:
        # Step 1: Truncate all tables using SQL
        print("1. Truncating all tables...")
        db = SessionLocal()
        try:
            truncate_tables(db)
            print("All tables truncated")
        except SQLAlchemyError as e:
            print(f"Truncate failed, falling back to DROP/CREATE: {e}")
            db.rollback()
            db.close()

            # Fallback: Drop and recreate tables
            Base.metadata.drop_all(bind=engine)
            Base.metadata.create_all(bind=engine)
            print("Tables dropped and recreated")

        # Step 2: Verify clean state
        print("2. Verifying clean database...")
        db = SessionLocal()
        try:
            product_count = db.query(Product).count()
            ingredient_count = db.query(Ingredient).count()
            skin_type_count = db.query(SkinType).count()

            if product_count == 0 and ingredient_count == 0 and skin_type_count == 0:
                print("Database completely empty")
            else:
                print(
                    "Database still has data: "
                    f"{product_count} products, {ingredient_count} ingredients, "
                    f"{skin_type_count} skin types"
                )
        finally:
            db.close()

        # Step 3: Reseed with CSV data
        print("3. Reseeding with CSV data...")
        csv_path = os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "data",
            "cosmetic_p.csv",
        )

        if not os.path.exists(csv_path):
            print(f"CSV file not found: {csv_path}")
            return False

        seed_data(csv_path)
        print("Database reseeded successfully")

        # Step 4: Final verification
        print("4. Final verification...")
        db = SessionLocal()
        try:
            product_count = db.query(Product).count()
            ingredient_count = db.query(Ingredient).count()
            skin_type_count = db.query(SkinType).count()

            print(
                "Final counts: "
                f"{product_count} products, {ingredient_count} ingredients, "
                f"{skin_type_count} skin types"
            )
        finally:
            db.close()

        print("\nDatabase reset complete!")
        print("=" * 50)
        return True

    except SQLAlchemyError as e:
        print(f"\nReset failed: {e}")
        return False


if __name__ == "__main__":
    reset_database()
