"""
Pydantic models for API
"""
from typing import List, Optional, Any
from pydantic import BaseModel, ConfigDict, field_validator

class IngredientBase(BaseModel):
    """
    Base model for ingredients
    """
    inci_name: str

class SkinTypeBase(BaseModel):
    """
    Base model for skin types
    """
    type_name: str

class ProductBase(BaseModel):
    """
    Base model for products
    """
    product_name: str
    brand_name: Optional[str] = None
    category: Optional[str] = None
    rank: Optional[float] = None


class Ingredient(IngredientBase):
    """
    Read schema for ingredients for API
    """
    ingredient_id: int
    model_config = ConfigDict(from_attributes=True)

class SkinType(SkinTypeBase):
    """
    Read schema for skin types for API
    """
    skin_type_id: int
    model_config = ConfigDict(from_attributes=True)

class Product(ProductBase):
    """
    Read schema for products for API
    """
    product_id: int
    ingredients: List[str] = []
    skin_types: List[str] = []

    model_config = ConfigDict(from_attributes=True)

    @field_validator('skin_types', mode='before')
    @classmethod
    def flatten_skin_types(cls, v: Any):
        """
        Nicely format skin types for API
        """
        if v and isinstance(v, list):
            return [item.type_name for item in v if hasattr(item, 'type_name')]
        return v

    @field_validator('ingredients', mode='before')
    @classmethod
    def flatten_ingredients(cls, v: Any):
        """
        Nicely format ingredients for API
        """
        if v and isinstance(v, list):
            return [item.inci_name for item in v if hasattr(item, 'inci_name')]
        return v

class QARequest(BaseModel):
    """
    Input schema for QA endpoint
    """
    question: str
    concern: Optional[str] = None
    intake_data: Optional[dict] = None  # Add intake data field

class QAResponse(BaseModel):
    """
    Output schema for QA endpoint
    """
    answer: str
    context_summary: str
    citations: List[str] = []


class ChatRequest(BaseModel):
    """
    Input schema for chat endpoint with intake form integration
    """
    question: str
    intake_data: Optional[dict] = None
    concern: Optional[str] = None
    conversation_id: Optional[str] = None


class ChatResponse(BaseModel):
    """
    Enhanced output schema for chat endpoint
    """
    answer: str
    context_summary: str
    user_profile: str = ""
    citations: List[dict] = []
    recommendation_confidence: float = 0.0
    routine_suggestion: str = ""
    conversation_id: Optional[str] = None
