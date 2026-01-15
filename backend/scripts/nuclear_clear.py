"""
Nuclear database clear - uses raw SQL to delete everything
"""

import sys
import os
from app.db.session import SessionLocal
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def nuclear_clear():
    """Nuclear option - clear everything with raw SQL"""
    print("NUCLEAR DATABASE CLEAR - Deleting EVERYTHING!")
    print("=" * 50)

    db = SessionLocal()
    try:
        # Show current state
        result = db.execute(text("SELECT COUNT(*) FROM products")).scalar()
        print(f"Current products: {result}")

        result = db.execute(text("SELECT COUNT(*) FROM ingredients")).scalar()
        print(f"Current ingredients: {result}")

        result = db.execute(text("SELECT COUNT(*) FROM skin_types")).scalar()
        print(f"Current skin types: {result}")

        print("\nExecuting nuclear clear...")

        # Nuclear clear sequence
        commands = [
            "SET FOREIGN_KEY_CHECKS = 0",
            "TRUNCATE TABLE product_ingredients",
            "TRUNCATE TABLE product_skin_types",
            "TRUNCATE TABLE products",
            "TRUNCATE TABLE ingredients",
            "TRUNCATE TABLE skin_types",
            "SET FOREIGN_KEY_CHECKS = 1",
        ]

        try:
            for cmd in commands:
                print(f"   Executing: {cmd}")
                db.execute(text(cmd))

            db.commit()
            print("All commands executed")
        except SQLAlchemyError:
            db.rollback()
            raise

        # Verify nuclear clear worked
        print("\nVerifying complete destruction...")

        result = db.execute(text("SELECT COUNT(*) FROM products")).scalar()
        print(f"Products remaining: {result}")

        result = db.execute(text("SELECT COUNT(*) FROM ingredients")).scalar()
        print(f"Ingredients remaining: {result}")

        result = db.execute(text("SELECT COUNT(*) FROM skin_types")).scalar()
        print(f"Skin types remaining: {result}")

        # Check junction tables too
        result = db.execute(text("SELECT COUNT(*) FROM product_ingredients")).scalar()
        print(f"Product-ingredient links: {result}")

        result = db.execute(text("SELECT COUNT(*) FROM product_skin_types")).scalar()
        print(f"Product-skintype links: {result}")

        total = (
            db.execute(text("SELECT COUNT(*) FROM products")).scalar()
            + db.execute(text("SELECT COUNT(*) FROM ingredients")).scalar()
            + db.execute(text("SELECT COUNT(*) FROM skin_types")).scalar()
            + db.execute(text("SELECT COUNT(*) FROM product_ingredients")).scalar()
            + db.execute(text("SELECT COUNT(*) FROM product_skin_types")).scalar()
        )
        if total == 0:
            print("\nNUCLEAR CLEAR SUCCESSFUL - Database is completely empty!")
            print("All tables have been wiped clean")
            return True

        print(f"\nNuclear clear incomplete - {total} records remain")
        return False

    except SQLAlchemyError as e:
        print(f"\n Nuclear clear failed: {e}")
        db.rollback()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    nuclear_clear()
