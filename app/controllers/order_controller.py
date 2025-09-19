from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.repositories.database import get_db
from app.services.order_service import OrderService
from app.schemas.order_schema import Order, OrderWithItems


router = APIRouter(
    prefix="/orders",
    tags=["orders"]
)

order_service = OrderService()


@router.get("/", response_model=List[Order])
def get_all_orders(db: Session = Depends(get_db)):
    """
    Obtener todas las órdenes
    """
    try:
        orders = order_service.get_all_orders(db)
        return orders
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving orders"
        )


@router.get("/{order_id}", response_model=OrderWithItems)
def get_order(order_id: int, db: Session = Depends(get_db)):
    """
    Obtener orden específica por ID con sus items
    """
    try:
        order = order_service.get_order_by_id(db, order_id)
        return order
    except HTTPException:
        # Re-lanzar HTTPExceptions del service/repository
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving order"
        )


@router.get("/user/{user_id}", response_model=List[Order])
def get_orders_by_user(user_id: int, db: Session = Depends(get_db)):
    """
    Obtener todas las órdenes de un usuario específico
    """
    try:
        orders = order_service.get_orders_by_user(db, user_id)
        return orders
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving user orders"
        )


@router.get("/{order_id}/summary")
def get_order_summary(order_id: int, db: Session = Depends(get_db)):
    """
    Obtener resumen de una orden (totales, cantidad de items, etc.)
    """
    try:
        summary = order_service.get_order_total(db, order_id)
        return summary
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving order summary"
        )