"""
API endpoints for ingredients
"""
from typing import List, Optional
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app import schemas
from app.db import models
from app.db.session import get_db

router = APIRouter()

@router.get("/ingredients", response_model=List[schemas.Ingredient])
def list_ingredients(
    search: Optional[str] = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    Get list of ingredients.
    """
    query = db.query(models.Ingredient)

    if search:
        query = query.filter(models.Ingredient.inci_name.ilike(f"%{search}%"))

    return query.offset(skip).limit(limit).all()
