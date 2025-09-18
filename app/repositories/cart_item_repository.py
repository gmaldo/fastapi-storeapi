from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.repositories.models.cart_models import CartItemModel


class CartItemRepository:

    def get_cart_items(self, db: Session, cart_id: int):
        return db.query(CartItemModel).filter_by(cart_id=cart_id).all()

    def get_cart_item(self, db: Session, item_id: int):
        item = db.query(CartItemModel).filter_by(id=item_id).first()
        if not item:
            raise HTTPException(status_code=404, detail="Cart item not found")
        return item

    def add_item_to_cart(self, db: Session, cart_id: int, product_id: int, quantity: int = 1):
        # Verificar si el item ya existe en el carrito
        existing_item = db.query(CartItemModel).filter_by(
            cart_id=cart_id,
            product_id=product_id
        ).first()
        
        if existing_item:
            # Si existe, sumar la cantidad
            existing_item.quantity += quantity
            db.commit()
            db.refresh(existing_item)
            return existing_item
        else:
            # Si no existe, crear nuevo item
            new_item = CartItemModel(
                cart_id=cart_id,
                product_id=product_id,
                quantity=quantity
            )
            db.add(new_item)
            db.commit()
            db.refresh(new_item)
            return new_item

    def update_cart_item_quantity(self, db: Session, item_id: int, quantity: int):
        db_item = db.query(CartItemModel).filter_by(id=item_id).first()
        if not db_item:
            raise HTTPException(status_code=404, detail="Cart item not found")
        
        if quantity <= 0:
            raise HTTPException(status_code=400, detail="Quantity must be greater than 0")
        
        db_item.quantity = quantity
        db.commit()
        db.refresh(db_item)
        return db_item

    def remove_item_from_cart(self, db: Session, item_id: int):
        db_item = db.query(CartItemModel).filter_by(id=item_id).first()
        if not db_item:
            raise HTTPException(status_code=404, detail="Cart item not found")
        
        db.delete(db_item)
        db.commit()
        return db_item

    def clear_cart(self, db: Session, cart_id: int):
        items = db.query(CartItemModel).filter_by(cart_id=cart_id).all()
        for item in items:
            db.delete(item)
        db.commit()
        return {"message": f"Cart {cart_id} cleared successfully"}