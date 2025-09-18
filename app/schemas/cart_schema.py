from pydantic import BaseModel
from typing import List, Optional


class CartCreate(BaseModel):
    user_id: int


class Cart(BaseModel):
    id: int
    user_id: int

    class Config:
        from_attributes = True


class CartWithItems(BaseModel):
    id: int
    user_id: int
    items: List['CartItem'] = []

    class Config:
        from_attributes = True


# Importar después para evitar circular imports
from .cart_item_schema import CartItem
CartWithItems.model_rebuild()