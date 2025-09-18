from pydantic import BaseModel, Field
from typing import Optional


class CartItemCreate(BaseModel):
    cart_id: int
    product_id: int
    quantity: int = Field(gt=0, description="Quantity must be greater than 0")


class CartItemUpdate(BaseModel):
    quantity: int = Field(gt=0, description="Quantity must be greater than 0")


class AddToCart(BaseModel):
    product_id: int
    quantity: int = Field(default=1, gt=0, description="Quantity must be greater than 0")


class CartItem(BaseModel):
    id: int
    cart_id: int
    product_id: int
    quantity: int

    class Config:
        from_attributes = True


class CartItemWithProduct(BaseModel):
    id: int
    cart_id: int
    product_id: int
    quantity: int
    product: Optional['Product'] = None

    class Config:
        from_attributes = True


# Importar después para evitar circular imports
from .product_schema import Product
CartItemWithProduct.model_rebuild()