from pydantic import BaseModel, Field
from typing import Optional


class ProductCreate(BaseModel):
    name: str
    price: float = Field(gt=0, description="Price must be greater than 0")
    description: str
    category: str
    stock: int = Field(ge=0, description="Stock must be greater than or equal to 0")
    image: str


class ProductUpdate(BaseModel):
    name: Optional[str] = None
    price: Optional[float] = Field(None, gt=0, description="Price must be greater than 0")
    description: Optional[str] = None
    category: Optional[str] = None
    stock: Optional[int] = Field(None, ge=0, description="Stock must be greater than or equal to 0")
    image: Optional[str] = None


class Product(BaseModel):
    id: int
    name: str
    price: float
    description: str
    category: str
    stock: int
    image: str

    class Config:
        from_attributes = True