from fastapi import HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict
from app.repositories.models.order_models import OrderItemModel


class OrderItemRepository:

    def get_order_items(self, db: Session, order_id: int):
        return db.query(OrderItemModel).filter_by(order_id=order_id).all()

    def get_order_item(self, db: Session, item_id: int):
        item = db.query(OrderItemModel).filter_by(id=item_id).first()
        if not item:
            raise HTTPException(status_code=404, detail="Order item not found")
        return item

    def create_order_item(self, db: Session, order_id: int, product_id: int, quantity: int, price: float):
        if quantity <= 0:
            raise HTTPException(status_code=400, detail="Quantity must be greater than 0")
        if price <= 0:
            raise HTTPException(status_code=400, detail="Price must be greater than 0")
        
        new_order_item = OrderItemModel(
            order_id=order_id,
            product_id=product_id,
            quantity=quantity,
            price=price
        )
        db.add(new_order_item)
        db.commit()
        db.refresh(new_order_item)
        return new_order_item

    def create_multiple_order_items(self, db: Session, order_items_data: List[Dict]):
        """
        Crear múltiples order items en una sola transacción
        order_items_data: Lista de diccionarios con keys: order_id, product_id, quantity, price
        """
        order_items = []
        for item_data in order_items_data:
            if item_data['quantity'] <= 0:
                raise HTTPException(status_code=400, detail="Quantity must be greater than 0")
            if item_data['price'] <= 0:
                raise HTTPException(status_code=400, detail="Price must be greater than 0")
            
            order_item = OrderItemModel(**item_data)
            db.add(order_item)
            order_items.append(order_item)
        
        db.commit()
        for item in order_items:
            db.refresh(item)
        return order_items

    def update_order_item(self, db: Session, item_id: int, quantity: int, price: float):
        db_item = db.query(OrderItemModel).filter_by(id=item_id).first()
        if not db_item:
            raise HTTPException(status_code=404, detail="Order item not found")
        
        if quantity <= 0:
            raise HTTPException(status_code=400, detail="Quantity must be greater than 0")
        if price <= 0:
            raise HTTPException(status_code=400, detail="Price must be greater than 0")
        
        db_item.quantity = quantity
        db_item.price = price
        db.commit()
        db.refresh(db_item)
        return db_item

    def delete_order_item(self, db: Session, item_id: int):
        db_item = db.query(OrderItemModel).filter_by(id=item_id).first()
        if not db_item:
            raise HTTPException(status_code=404, detail="Order item not found")
        
        db.delete(db_item)
        db.commit()
        return db_item