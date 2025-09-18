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
    Procesar compra del carrito: crear orden y descontar stock
    """
    try:
        # 1. Validar carrito antes del checkout
        cart_validation = cart_service.validate_cart_for_checkout(db, user_id)
        
        if not cart_validation["valid"]:
            return {
                "success": False,
                "message": "No se pudo procesar la orden",
                "details": "Cart validation failed"
            }
        
        # 2. Obtener detalles del carrito
        cart_details = cart_service.get_cart_with_product_details(db, user_id)
        
        if not cart_details["items"]:
            return {
                "success": False,
                "message": "No se pudo procesar la orden",
                "details": "Cart is empty"
            }
        
        # 3. Verificar stock nuevamente y preparar items para la orden
        order_items_data = []
        total_amount = 0.0
        
        for item in cart_details["items"]:
            product = item["product"]
            
            # Verificar stock disponible
            if product["stock"] < item["quantity"]:
                return {
                    "success": False,
                    "message": "No se pudo procesar la orden",
                    "details": f"Insufficient stock for {product['name']}. Available: {product['stock']}, Requested: {item['quantity']}"
                }
            
            # Preparar datos para order item
            order_items_data.append({
                "product_id": product["id"],
                "quantity": item["quantity"],
                "price": product["price"]  # Precio al momento de la compra
            })
            
            total_amount += product["price"] * item["quantity"]
        
        # 4. Crear la orden usando OrderService
        order_result = order_service.create_order_from_cart(db, user_id)
        
        if not order_result["success"]:
            return {
                "success": False,
                "message": "No se pudo procesar la orden",
                "details": "Failed to create order"
            }
        
        # TEMPORAL: Simulación de creación de orden
        # new_order = {
        #     "id": 1,  # Esto vendría del OrderService
        #     "user_id": user_id,
        #     "total": total_amount,
        #     "date": "2024-01-01T00:00:00",
        #     "status": "pending"
        # }
        
        # 5. Descontar stock de los productos
        for item_data in order_result["cart_items_processed"]:
            try:
                product_service.reduce_product_stock(
                    db, 
                    item_data["product_id"], 
                    item_data["quantity"]
                )
            except Exception as stock_error:
                # Si hay error descontando stock, cancelar orden y revertir
                try:
                    order_service.cancel_order(db, order_result["order"].id)
                except:
                    pass
                return {
                    "success": False,
                    "message": "No se pudo procesar la orden",
                    "details": f"Error updating stock: {str(stock_error)}"
                }
        
        # 6. Limpiar el carrito después de la compra exitosa
        cart_service.clear_user_cart(db, user_id)
        
        return {
            "success": True,
            "message": "Order processed successfully",
            "order": order_result["order"],
            "items_purchased": order_result["items_count"],
            "total_amount": order_result["total_amount"]
        }
        
    except HTTPException as he:
        return {
            "success": False,
            "message": "No se pudo procesar la orden",
            "details": he.detail
        }
    except Exception as e:
        return {
            "success": False,
            "message": "No se pudo procesar la orden",
            "details": "Internal server error"
        }