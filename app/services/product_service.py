from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.repositories import ProductRepository
from app.repositories.models.product_model import ProductModel   


class ProductService:
    def __init__(self):
        self.repository : ProductRepository = ProductRepository()

    def get_products(self, db: Session):
        return self.repository.get_products(db)

    def get_product(self, db: Session, product_id: int):
        return self.repository.get_product(db,product_id)

    def create_product(self, db: Session, product: ProductModel):
        return self.repository.create_product(db,product)

    def update_product(self, db: Session, product_id: int, product: ProductModel):
        return self.repository.update_product(db,product_id, product)

    def delete_product(self, db: Session, product_id: int):
        return self.repository.delete_product(db,product_id)
    
    def reduce_product_stock(self, db: Session, product_id: int, quantity: int):
        """Reducir stock de un producto"""
        # Obtener producto actual
        product = self.repository.get_product(db, product_id)
        
        # Verificar stock suficiente
        if product.stock < quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient stock for product {product.name}. Available: {product.stock}, Requested: {quantity}"
            )
        
        # Calcular nuevo stock
        new_stock = product.stock - quantity
        
        # Crear modelo actualizado
        updated_product = ProductModel(
            name=product.name,
            price=product.price,
            description=product.description,
            category=product.category,
            stock=new_stock,
            image=product.image
        )
        
        # Actualizar en base de datos
        return self.repository.update_product(db, product_id, updated_product)