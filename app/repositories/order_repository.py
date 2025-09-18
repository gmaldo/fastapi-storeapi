from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.repositories.models.order_models import OrderModel


class OrderRepository:

    def get_orders(self, db: Session):
        return db.query(OrderModel).all()

    def get_order(self, db: Session, order_id: int):
        order = db.query(OrderModel).filter_by(id=order_id).first()
        if not order:
            raise HTTPException(status_code=404, detail="Order not found")
        return order

    def get_orders_by_user(self, db: Session, user_id: int):
        return db.query(OrderModel).filter_by(user_id=user_id).all()

    def create_order(self, db: Session, user_id: int, total: float):
        if total <= 0:
            raise HTTPException(status_code=400, detail="Order total must be greater than 0")
        
        new_order = OrderModel(
            user_id=user_id,
            total=total
        )
        db.add(new_order)
        db.commit()
        db.refresh(new_order)
        return new_order

    def update_order_total(self, db: Session, order_id: int, total: float):
        db_order = db.query(OrderModel).filter_by(id=order_id).first()
        if not db_order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        if total <= 0:
            raise HTTPException(status_code=400, detail="Order total must be greater than 0")
        
        db_order.total = total
        db.commit()
        db.refresh(db_order)
        return db_order

    def delete_order(self, db: Session, order_id: int):
        db_order = db.query(OrderModel).filter_by(id=order_id).first()
        if not db_order:
            raise HTTPException(status_code=404, detail="Order not found")
        
        db.delete(db_order)
        db.commit()
        return db_order