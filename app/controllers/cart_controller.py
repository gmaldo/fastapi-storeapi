from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.repositories.database import get_db
from app.services.cart_service import CartService
from app.services.product_service import ProductService
from app.services.order_service import OrderService
from app.schemas.cart_schema import Cart, CartWithItems
from app.schemas.cart_item_schema import AddToCart
from app.schemas.order_schema import Order


router = APIRouter(
    prefix="/carts",
    tags=["carts"]
)

cart_service = CartService()
product_service = ProductService()
order_service = OrderService()


@router.get("/", response_model=List[Cart])
def get_all_carts(db: Session = Depends(get_db)):
    """
    Obtener todos los carritos
    """
    try:
        # Necesitarás agregar este método al CartService
        carts = cart_service.get_all_carts(db)
        return carts
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving carts"
        )


@router.get("/{cart_id}")
def get_cart(cart_id: int, db: Session = Depends(get_db)):
    """
    Obtener carrito por ID con detalles de productos
    """
    try:
        # Obtener carrito básico
        cart = cart_service.cart_repository.get_cart(db, cart_id)
        # Obtener detalles completos usando el user_id del carrito
        cart_details = cart_service.get_cart_with_product_details(db, cart.user_id)
        return cart_details
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving cart"
        )


@router.get("/user/{user_id}")
def get_user_cart(user_id: int, db: Session = Depends(get_db)):
    """
    Obtener carrito de un usuario específico con detalles de productos
    """
    try:
        cart_details = cart_service.get_cart_with_product_details(db, user_id)
        return cart_details
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving user cart"
        )


@router.post("/{cart_id}/{product_id}")
def add_product_to_cart(
    cart_id: int, 
    product_id: int, 
    quantity: int = 1,
    db: Session = Depends(get_db)
):
    """
    Agregar producto al carrito
    """
    try:
        # Obtener el carrito para obtener el user_id
        cart = cart_service.cart_repository.get_cart(db, cart_id)
        
        # Usar el servicio para agregar el item
        item_data = AddToCart(product_id=product_id, quantity=quantity)
        cart_item = cart_service.add_item_to_cart(db, cart.user_id, item_data)
        
        return {
            "message": "Product added to cart successfully",
            "cart_item": cart_item,
            "cart_id": cart_id
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error adding product to cart"
        )


@router.delete("/{cart_id}/{product_id}")
def remove_product_from_cart(
    cart_id: int, 
    product_id: int, 
    db: Session = Depends(get_db)
):
    """
    Eliminar producto del carrito
    """
    try:
        # Obtener el carrito para obtener el user_id
        cart = cart_service.cart_repository.get_cart(db, cart_id)
        
        # Buscar el cart_item específico
        cart_items = cart_service.cart_item_repository.get_cart_items(db, cart_id)
        cart_item = None
        
        for item in cart_items:
            if item.product_id == product_id:
                cart_item = item
                break
        
        if not cart_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Product not found in cart"
            )
        
        # Remover el item
        result = cart_service.remove_item_from_cart(db, cart.user_id, cart_item.id)
        
        return {
            "message": "Product removed from cart successfully",
            "removed_item": result["removed_item"],
            "cart_id": cart_id
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error removing product from cart"
        )


@router.post("/purchase")
def purchase_cart(user_id: int, db: Session = Depends(get_db)):
    """
    Procesar compra del carrito: crear orden, reducir stock y vaciar carrito
    """
    try:
        # 1. Crear orden desde el carrito (esto incluye validaciones)
        order_result = order_service.create_order_from_cart(db, user_id)
        
        # 2. Reducir stock de todos los productos
        for item_data in order_result["cart_items_processed"]:
            try:
                product_service.reduce_product_stock(
                    db, 
                    item_data["product_id"], 
                    item_data["quantity"]
                )
            except Exception as stock_error:
                # Si hay error reduciendo stock, cancelar orden
                try:
                    order_service.cancel_order(db, order_result["order"].id)
                except:
                    pass
                raise HTTPException(
                    status_code=400,
                    detail=f"Error updating stock: {str(stock_error)}"
                )
        
        # 3. Vaciar el carrito después de la compra exitosa
        cart_service.clear_user_cart(db, user_id)
        
        return {
            "success": True,
            "message": "Purchase completed successfully",
            "order": order_result["order"],
            "items_purchased": order_result["items_count"],
            "total_amount": order_result["total_amount"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error processing purchase: {str(e)}"
        )