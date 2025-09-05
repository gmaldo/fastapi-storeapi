from sqlalchemy.orm import Session

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
        return self.repository.delete_product(db,hero_id)