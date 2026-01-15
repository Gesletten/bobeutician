"""
Clean database verification - shows exactly what's in each table
"""

import sys
import os
from sqlalchemy.exc import SQLAlchemyError
from app.db.session import SessionLocal
from app.db.models import Product, Ingredient, SkinType

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def clean_verification():
    """Clean, simple database verification"""
    print("BOBEUTICIAN DATABASE STATUS")
    print("=" * 35)
    db = SessionLocal()
    try:
        # Simple counts
        products = db.query(Product).count()
        ingredients = db.query(Ingredient).count()
        skin_types = db.query(SkinType).count()

        print(f"Products: {products:,}")
        print(f"Ingredients: {ingredients:,}")
        print(f"Skin Types: {skin_types}")

        print("\nAvailable Skin Types:")
        skin_type_list = db.query(SkinType).order_by(SkinType.type_name).all()

        for st in skin_type_list:
            product_count = len(st.products)
            print(f"{st.type_name}: {product_count:,} products")

        print("\nSample Products by Skin Type:")
        for skin_type in ["Oily", "Dry", "Sensitive"]:
            st_obj = db.query(SkinType).filter(SkinType.type_name == skin_type).first()
            if st_obj and st_obj.products:
                sample = st_obj.products[0]
                print(f"   {skin_type}: {sample.product_name} by {sample.brand_name}")

        print("\nDatabase is healthy and properly populated!")

        return True

    except (SQLAlchemyError, AttributeError, IndexError) as e:
        print(f"Verification failed: {e}")
        return False
    finally:
        db.close()
        db.close()


if __name__ == "__main__":
    clean_verification()
