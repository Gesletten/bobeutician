"""
API endpoints for products
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app import schemas
from app.db import models
from app.db.session import get_db

router = APIRouter()


@router.get("/products/{product_id}", response_model=schemas.Product)
def get_product(product_id: int, db: Session = Depends(get_db)):
    """
    Get a specific product by ID.
    """
    product = (
        db.query(models.Product).filter(models.Product.product_id == product_id).first()
    )
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product


@router.get("/products", response_model=List[schemas.Product])
def _filter_params(
    search: Optional[str] = None,
    skin_types: List[str] = Query(None, alias="skin_type"),
    ingredients: List[str] = Query(None, alias="ingredient"),
    skip: int = 0,
    limit: int = 50,
):
    return {
        "search": search,
        "skin_types": skin_types,
        "ingredients": ingredients,
        "skip": skip,
        "limit": limit,
    }


@router.get("/products", response_model=List[schemas.Product])
def filter_products(
    params: dict = Depends(_filter_params), db: Session = Depends(get_db)
):
    """
    Filter Endpoint.
    """
    search = params.get("search")
    skin_types = params.get("skin_types")
    ingredients = params.get("ingredients")
    skip = params.get("skip", 0)
    limit = params.get("limit", 50)
    query = db.query(models.Product)

    if search:
        search_term = f"%{search}%"
        query = query.filter(
            or_(
                models.Product.product_name.ilike(search_term),
                models.Product.brand_name.ilike(search_term),
            )
        )

    if skin_types:
        query = query.join(models.Product.skin_types)
        query = query.filter(models.SkinType.type_name.in_(skin_types))

    if ingredients:
        query = query.join(models.Product.ingredients)
        query = query.filter(models.Ingredient.inci_name.in_(ingredients))

    query = query.distinct()
    products = query.offset(skip).limit(limit).all()

    return products
