from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session

from app.repositories.database import get_db
from app.services import ProductService
from app.schemas import Product

router  = APIRouter(prefix="/products", tags=["Products"])
service = ProductService()

@router.get("/")
def get_products(db: Session = Depends(get_db)):
    return service.get_products(db)

@router.get("/{product_id}")
def get_product(product_id: int,db: Session = Depends(get_db),):
    return service.get_product(db,product_id)

@router.post("/")
def create_product(product: Product,db: Session = Depends(get_db)):
    return service.create_product(db,product)

@router.put("/{product_id}")
def update_product(product_id: int, product: Product, db: Session = Depends(get_db)):
    return service.update_product(db, product_id, product)

@router.delete("/{product_id}")
def delete_product(product_id: int,db: Session = Depends(get_db)):
    return service.delete_product(db,product_id)
