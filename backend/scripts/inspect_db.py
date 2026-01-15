"""
Comprehensive database inspection script
"""

import sys
import os
from app.db.session import SessionLocal
from app.db.models import SkinType
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def inspect_database():
    """Comprehensive database inspection"""
    print("COMPREHENSIVE DATABASE INSPECTION")
    print("=" * 50)

    db = SessionLocal()
    try:
        # Check table structure
        print("1. TABLE STRUCTURE:")
        tables = db.execute(text("SHOW TABLES")).fetchall()
        print(f"   Tables found: {len(tables)}")
        for table in tables:
            table_name = table[0]
            count = db.execute(text(f"SELECT COUNT(*) FROM {table_name}")).scalar()
            print(f"      • {table_name}: {count} rows")

        print("\n2. SKIN_TYPES DETAILED INSPECTION:")
        # Raw SQL query
        result = db.execute(
            text("SELECT skin_type_id, type_name FROM skin_types ORDER BY skin_type_id")
        ).fetchall()
        print(f"   Raw SQL results ({len(result)} rows):")
        for row in result:
            print(f"      ID: {row[0]} | Name: '{row[1]}' | Length: {len(str(row[1]))}")

        # ORM query
        skin_types = db.query(SkinType).order_by(SkinType.skin_type_id).all()
        print(f"\nORM results ({len(skin_types)} objects):")
        for st in skin_types:
            print(
                f"ID: {st.skin_type_id} | Name: '{st.type_name}' | Length: {len(st.type_name)}"
            )
            # Check products for this skin type
            product_count = len(st.products)
            print(f"Products: {product_count}")

        print("\n3. SAMPLE PRODUCT-SKINTYPE RELATIONSHIPS:")
        # Check junction table
        result = db.execute(
            text(
                """
            SELECT p.product_name, st.type_name 
            FROM products p 
            JOIN product_skin_types pst ON p.product_id = pst.product_id 
            JOIN skin_types st ON pst.skin_type_id = st.skin_type_id 
            LIMIT 5
        """
            )
        ).fetchall()

        print(f"Sample relationships ({len(result)}):")
        for row in result:
            print(f"Product: {row[0][:30]}... | Skin Type: '{row[1]}'")

        print("\n4. POTENTIAL ISSUES CHECK:")
        # Check for empty or malformed skin type names
        bad_skin_types = db.execute(
            text(
                """
            SELECT skin_type_id, type_name, LENGTH(type_name) as name_length
            FROM skin_types 
            WHERE type_name = '' OR type_name IS NULL OR LENGTH(type_name) > 50
        """
            )
        ).fetchall()

        if bad_skin_types:
            print(f"Found {len(bad_skin_types)} problematic skin types:")
            for row in bad_skin_types:
                print(f"D: {row[0]} | Name: '{row[1]}' | Length: {row[2]}")
        else:
            print("No problematic skin types found")

        # Check for duplicates
        duplicates = db.execute(
            text(
                """
            SELECT type_name, COUNT(*) as count
            FROM skin_types 
            GROUP BY type_name 
            HAVING COUNT(*) > 1
        """
            )
        ).fetchall()

        if duplicates:
            print(f"Found {len(duplicates)} duplicate skin types:")
            for row in duplicates:
                print(f"Name: '{row[0]}' appears {row[1]} times")
        else:
            print("No duplicate skin types found")

        print("\nInspection complete!")
    except SQLAlchemyError as e:
        print(f"Inspection failed (database error): {e}")
    finally:
        db.close()


if __name__ == "__main__":
    inspect_database()
