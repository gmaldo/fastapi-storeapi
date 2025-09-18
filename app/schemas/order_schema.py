from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional


class OrderCreate(BaseModel):
    user_id: int
    total: float = Field(gt=0, description="Total must be greater than 0")


class OrderUpdate(BaseModel):
    total: Optional[float] = Field(None, gt=0, description="Total must be greater than 0")


class Order(BaseModel):
    id: int
    user_id: int
    total: float
    date: datetime

    class Config:
        from_attributes = True


class OrderWithItems(BaseModel):
    id: int
    user_id: int
    total: float
    date: datetime
    items: List['OrderItem'] = []

    class Config:
        from_attributes = True


class CreateOrderFromCart(BaseModel):
    user_id: int


# Importar después para evitar circular imports
from .order_item_schema import OrderItem
OrderWithItems.model_rebuild()