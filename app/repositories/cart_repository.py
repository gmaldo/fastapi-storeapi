from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.repositories.models.cart_models import CartModel


class CartRepository:

    def get_all_carts(self, db: Session):
        return db.query(CartModel).all()

    def get_cart_by_user_id(self, db: Session, user_id: int):
        cart = db.query(CartModel).filter_by(user_id=user_id).first()
        if not cart:
            # Si no existe carrito, crear uno automáticamente
            cart = self.create_cart(db, user_id)
        return cart

    def get_cart(self, db: Session, cart_id: int):
        cart = db.query(CartModel).filter_by(id=cart_id).first()
        if not cart:
            raise HTTPException(status_code=404, detail="Cart not found")
        return cart

    def create_cart(self, db: Session, user_id: int):
        # Verificar si el usuario ya tiene un carrito
        existing_cart = db.query(CartModel).filter_by(user_id=user_id).first()
        if existing_cart:
            raise HTTPException(status_code=400, detail="User already has a cart")
        
        new_cart = CartModel(user_id=user_id)
        db.add(new_cart)
        db.commit()
        db.refresh(new_cart)
        return new_cart

    def delete_cart(self, db: Session, cart_id: int):
        db_cart = db.query(CartModel).filter_by(id=cart_id).first()
        if not db_cart:
            raise HTTPException(status_code=404, detail="Cart not found")
        
        db.delete(db_cart)
        db.commit()
        return db_cart