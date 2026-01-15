"""
Seed script for importing kaggle csv into database
usage: docker compose exec backend python scripts/seed_db.py
docker command: python backend/scripts/seed_db.py
"""

import csv
import sys
import os
from app.db.session import SessionLocal
from app.db.models import Product, Ingredient, SkinType
from sqlalchemy.exc import SQLAlchemyError

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def seed_data(csv_file_path: str):
    """Seed the database from the given CSV file path.

    Reads the CSV located at ``csv_file_path`` and inserts products,
    ingredients and skin types into the database. Commits on success
    and rolls back on errors.
    """
    db = SessionLocal()
    ingredient_cache: dict = {}
    skin_type_cache: dict = {}

    try:
        print(f"Reading from {csv_file_path}...")

        with open(csv_file_path, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            count = 0

            for row in reader:
                product = _build_product_from_row(row)
                db.add(product)

                _attach_ingredients(db, product, row, ingredient_cache)
                _attach_skin_types(db, product, row, skin_type_cache)

                count += 1
                if count % 100 == 0:
                    print(f"Processed {count} products...")

            db.commit()
            print(f"Success! Seeded {count} products.")

    except (csv.Error, OSError, ValueError, SQLAlchemyError) as e:
        print(f"Error: {e}")
        db.rollback()
    finally:
        db.close()


def _build_product_from_row(row: dict) -> Product:
    return Product(
        product_name=row.get("name", "Unknown"),
        brand_name=row.get("brand", "Unknown"),
        category=row.get("Label", None),
        rank=float(row["rank"]) if row.get("rank") else None,
    )


def _get_or_create_skin_type(db, cache: dict, name: str) -> SkinType:
    if name not in cache:
        st = db.query(SkinType).filter_by(type_name=name).first()
        if not st:
            st = SkinType(type_name=name)
            db.add(st)
            db.flush()
        cache[name] = st
    return cache[name]


def _get_or_create_ingredient(db, cache: dict, name: str) -> Ingredient:
    if name not in cache:
        existing = db.query(Ingredient).filter_by(inci_name=name).first()
        if existing:
            cache[name] = existing
        else:
            new_ing = Ingredient(inci_name=name)
            db.add(new_ing)
            db.flush()
            cache[name] = new_ing
    return cache[name]


def _attach_ingredients(
    db, product: Product, row: dict, ingredient_cache: dict
) -> None:
    raw_ingredients = row.get("ingredients", "")
    if not raw_ingredients:
        return

    ing_names = [i.strip() for i in raw_ingredients.split(",")]
    seen_ingredients = set()

    for name in ing_names:
        if not name:
            continue

        if len(name) > 250:
            print(f"Skipping malformed data: {name[:50]}...")
            continue

        ing_obj = _get_or_create_ingredient(db, ingredient_cache, name)
        if ing_obj.ingredient_id in seen_ingredients:
            continue

        product.ingredients.append(ing_obj)
        seen_ingredients.add(ing_obj.ingredient_id)


def _attach_skin_types(db, product: Product, row: dict, skin_type_cache: dict) -> None:
    target_columns = ["Combination", "Dry", "Normal", "Oily", "Sensitive"]
    for col_name in target_columns:
        val = str(row.get(col_name, "")).strip()
        if val == "1":
            st_obj = _get_or_create_skin_type(db, skin_type_cache, col_name)
            product.skin_types.append(st_obj)


if __name__ == "__main__":
    CSV_PATH = os.path.join(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        "data",
        "cosmetic_p.csv",
    )
    if not os.path.exists(CSV_PATH):
        print(f"File not found: {CSV_PATH}")
    else:
        seed_data(CSV_PATH)
