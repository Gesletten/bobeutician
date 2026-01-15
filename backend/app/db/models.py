"""Database models for alembic"""

# pylint: disable=import-error
from sqlalchemy import Column, Integer, String, ForeignKey, Table, Float
from sqlalchemy.orm import relationship, declarative_base

Base = declarative_base()

# Junction Tables

product_ingredients_table = Table(
    "product_ingredients",
    Base.metadata,
    Column("product_id", Integer, ForeignKey("products.product_id"), primary_key=True),
    Column(
        "ingredient_id",
        Integer,
        ForeignKey("ingredients.ingredient_id"),
        primary_key=True,
    ),
)

product_skin_types_table = Table(
    "product_skin_types",
    Base.metadata,
    Column("product_id", Integer, ForeignKey("products.product_id"), primary_key=True),
    Column(
        "skin_type_id", Integer, ForeignKey("skin_types.skin_type_id"), primary_key=True
    ),
)


# Main entities
# pylint: disable=too-few-public-methods
class Product(Base):
    """Represents a shincare product"""

    __tablename__ = "products"
    product_id = Column(Integer, primary_key=True)
    product_name = Column(String(255), nullable=False)
    brand_name = Column(String(255))
    category = Column(String(100))
    rank = Column(Float)
    ingredients = relationship(
        "Ingredient", secondary=product_ingredients_table, back_populates="products"
    )

    skin_types = relationship(
        "SkinType", secondary=product_skin_types_table, back_populates="products"
    )

    def __repr__(self):
        return f"<Product(id={self.product_id}, name='{self.brand_name} {self.product_name}')>"


# pylint: disable=too-few-public-methods
class Ingredient(Base):
    """ "Represents an ingredient in a product"""

    __tablename__ = "ingredients"
    ingredient_id = Column(Integer, primary_key=True)
    inci_name = Column(String(255), nullable=False, unique=True, index=True)
    products = relationship(
        "Product", secondary=product_ingredients_table, back_populates="ingredients"
    )

    def __repr__(self):
        return f"<Ingredient(id={self.ingredient_id}, name='{self.inci_name}')>"


# pylint: disable=too-few-public-methods
class SkinType(Base):
    """Represents a skin type"""

    __tablename__ = "skin_types"
    skin_type_id = Column(Integer, primary_key=True)
    type_name = Column(String(50), nullable=False, unique=True, index=True)
    products = relationship(
        "Product", secondary=product_skin_types_table, back_populates="skin_types"
    )

    def __repr__(self):
        return f"<SkinType(id={self.skin_type_id}, name='{self.type_name}')>"
