from fastapi import HTTPException
from sqlalchemy.orm import Session


from app.repositories.models.product_model import ProductModel

class ProductRepository:

    def get_products(self, db: Session):
        return db.query(ProductModel).all()

    def get_product(self, db: Session, product_id: int):
        product = db.query(ProductModel).filter_by(id=product_id).first()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
        return product

    def create_product(self, db: Session, product: ProductModel):
        new_product = ProductModel(
        name=product.name,
        description=product.description,
        price=product.price,
        category=product.category,
        stock=product.stock,
        image=product.image
        )
        db.add(new_product)
        db.commit()
        db.refresh(new_product)
        return new_product

    def update_product(self, db: Session, product_id: int, product: ProductModel):
        db_product = db.query(ProductModel).filter_by(id=product_id).first()
        if not db_product:
            raise HTTPException(status_code=404, detail="Product not found")
        if db_product:
            db_product.name = product.name
            db_product.description = product.description
            db_product.price = product.price
            db_product.category = product.category
            db_product.stock = product.stock
            db_product.image = product.image
        db.commit()
        db.refresh(db_product)
        return db_product

    def delete_product(self, db: Session, product_id: int):
        db_product = db.query(ProductModel).filter(ProductModel.id == product_id).first()
        if db_product:
            db.delete(db_product)
            db.commit()
        return db_product