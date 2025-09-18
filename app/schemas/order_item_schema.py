from pydantic import BaseModel, Field
from typing import List, Optional


class OrderItemCreate(BaseModel):
    order_id: int
    product_id: int
    quantity: int = Field(gt=0, description="Quantity must be greater than 0")
    price: float = Field(gt=0, description="Price must be greater than 0")


class OrderItemUpdate(BaseModel):
    quantity: Optional[int] = Field(None, gt=0, description="Quantity must be greater than 0")
    price: Optional[float] = Field(None, gt=0, description="Price must be greater than 0")


class OrderItemBulkCreate(BaseModel):
    items: List[OrderItemCreate]


class OrderItem(BaseModel):
    id: int
    order_id: int
    product_id: int
    quantity: int
    price: float

    class Config:
        from_attributes = True


class OrderItemWithProduct(BaseModel):
    id: int
    order_id: int
    product_id: int
    quantity: int
    price: float
    product: Optional['Product'] = None

    class Config:
        from_attributes = True


# Importar después para evitar circular imports
from .product_schema import Product
OrderItemWithProduct.model_rebuild()