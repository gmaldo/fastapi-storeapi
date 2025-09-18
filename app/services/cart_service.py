from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import List

from app.repositories.cart_repository import CartRepository
from app.repositories.cart_item_repository import CartItemRepository
from app.repositories.product_repository import ProductRepository
from app.schemas.cart_schema import Cart, CartWithItems
from app.schemas.cart_item_schema import CartItem, CartItemWithProduct, AddToCart, CartItemUpdate


class CartService:
    def __init__(self):
        self.cart_repository = CartRepository()
        self.cart_item_repository = CartItemRepository()
        self.product_repository = ProductRepository()

    def get_all_carts(self, db: Session) -> List[Cart]:
        """Obtener todos los carritos"""
        # Nota: Necesitarás agregar este método al CartRepository también
        try:
            carts = self.cart_repository.get_all_carts(db)
            return [Cart.from_orm(cart) for cart in carts]
        except Exception:
            raise HTTPException(
                status_code=500,
                detail="Error retrieving carts"
            )

    def get_user_cart(self, db: Session, user_id: int) -> CartWithItems:
        """Obtener carrito del usuario con todos sus items"""
        cart = self.cart_repository.get_cart_by_user_id(db, user_id)
        cart_items = self.cart_item_repository.get_cart_items(db, cart.id)
        
        # Convertir a schemas
        cart_schema = Cart.from_orm(cart)
        items_schema = [CartItem.from_orm(item) for item in cart_items]
        
        # Crear CartWithItems manualmente
        return CartWithItems(
            id=cart_schema.id,
            user_id=cart_schema.user_id,
            items=items_schema
        )

    def get_cart_with_product_details(self, db: Session, user_id: int) -> dict:
        """Obtener carrito con detalles completos de productos"""
        cart = self.cart_repository.get_cart_by_user_id(db, user_id)
        cart_items = self.cart_item_repository.get_cart_items(db, cart.id)
        
        items_with_products = []
        total_amount = 0.0
        total_items = 0
        
        for item in cart_items:
            # Obtener detalles del producto
            product = self.product_repository.get_product(db, item.product_id)
            
            item_total = product.price * item.quantity
            total_amount += item_total
            total_items += item.quantity
            
            items_with_products.append({
                "id": item.id,
                "cart_id": item.cart_id,
                "product_id": item.product_id,
                "quantity": item.quantity,
                "product": {
                    "id": product.id,
                    "name": product.name,
                    "price": product.price,
                    "description": product.description,
                    "category": product.category,
                    "stock": product.stock,
                    "image": product.image
                },
                "item_total": item_total
            })
        
        return {
            "cart": Cart.from_orm(cart),
            "items": items_with_products,
            "summary": {
                "total_items": total_items,
                "total_amount": total_amount
            }
        }

    def add_item_to_cart(self, db: Session, user_id: int, item_data: AddToCart) -> CartItem:
        """Agregar item al carrito del usuario"""
        # Verificar que el producto existe y hay stock disponible
        product = self.product_repository.get_product(db, item_data.product_id)
        
        if product.stock < item_data.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient stock. Available: {product.stock}, Requested: {item_data.quantity}"
            )
        
        # Obtener o crear carrito
        cart = self.cart_repository.get_cart_by_user_id(db, user_id)
        
        # Agregar item al carrito
        cart_item = self.cart_item_repository.add_item_to_cart(
            db, cart.id, item_data.product_id, item_data.quantity
        )
        
        return CartItem.from_orm(cart_item)

    def update_cart_item_quantity(self, db: Session, user_id: int, item_id: int, update_data: CartItemUpdate) -> CartItem:
        """Actualizar cantidad de un item del carrito"""
        # Verificar que el item pertenece al usuario
        cart = self.cart_repository.get_cart_by_user_id(db, user_id)
        item = self.cart_item_repository.get_cart_item(db, item_id)
        
        if item.cart_id != cart.id:
            raise HTTPException(status_code=403, detail="Item does not belong to user's cart")
        
        # Verificar stock disponible
        product = self.product_repository.get_product(db, item.product_id)
        if product.stock < update_data.quantity:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient stock. Available: {product.stock}, Requested: {update_data.quantity}"
            )
        
        # Actualizar cantidad
        updated_item = self.cart_item_repository.update_cart_item_quantity(
            db, item_id, update_data.quantity
        )
        
        return CartItem.from_orm(updated_item)

    def remove_item_from_cart(self, db: Session, user_id: int, item_id: int) -> dict:
        """Remover item específico del carrito"""
        # Verificar que el item pertenece al usuario
        cart = self.cart_repository.get_cart_by_user_id(db, user_id)
        item = self.cart_item_repository.get_cart_item(db, item_id)
        
        if item.cart_id != cart.id:
            raise HTTPException(status_code=403, detail="Item does not belong to user's cart")
        
        removed_item = self.cart_item_repository.remove_item_from_cart(db, item_id)
        
        return {
            "message": "Item removed from cart successfully",
            "removed_item": CartItem.from_orm(removed_item)
        }

    def clear_user_cart(self, db: Session, user_id: int) -> dict:
        """Vaciar completamente el carrito del usuario"""
        cart = self.cart_repository.get_cart_by_user_id(db, user_id)
        result = self.cart_item_repository.clear_cart(db, cart.id)
        
        return {
            "message": f"Cart cleared successfully for user {user_id}",
            "cart_id": cart.id
        }

    def get_cart_total(self, db: Session, user_id: int) -> dict:
        """Calcular total del carrito"""
        cart_details = self.get_cart_with_product_details(db, user_id)
        
        return {
            "cart_id": cart_details["cart"].id,
            "user_id": user_id,
            "total_items": cart_details["summary"]["total_items"],
            "total_amount": cart_details["summary"]["total_amount"]
        }

    def validate_cart_for_checkout(self, db: Session, user_id: int) -> dict:
        """Validar carrito antes del checkout"""
        cart_details = self.get_cart_with_product_details(db, user_id)
        
        if not cart_details["items"]:
            raise HTTPException(status_code=400, detail="Cart is empty")
        
        # Verificar stock de todos los items
        issues = []
        for item in cart_details["items"]:
            product = item["product"]
            if product["stock"] < item["quantity"]:
                issues.append({
                    "product_id": product["id"],
                    "product_name": product["name"],
                    "requested": item["quantity"],
                    "available": product["stock"]
                })
        
        if issues:
            raise HTTPException(
                status_code=400, 
                detail={
                    "message": "Some items have insufficient stock",
                    "issues": issues
                }
            )
        
        return {
            "valid": True,
            "cart_summary": cart_details["summary"]
        }