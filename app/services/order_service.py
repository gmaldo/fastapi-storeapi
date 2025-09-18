from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import List, Dict
from datetime import datetime

from app.repositories.order_repository import OrderRepository
from app.repositories.order_item_repository import OrderItemRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.cart_repository import CartRepository
from app.repositories.cart_item_repository import CartItemRepository
from app.schemas.order_schema import Order, OrderCreate, OrderWithItems
from app.schemas.order_item_schema import OrderItem, OrderItemCreate


class OrderService:
    def __init__(self):
        self.order_repository = OrderRepository()
        self.order_item_repository = OrderItemRepository()
        self.product_repository = ProductRepository()
        self.cart_repository = CartRepository()
        self.cart_item_repository = CartItemRepository()

    def get_all_orders(self, db: Session) -> List[Order]:
        """Obtener todas las órdenes"""
        orders = self.order_repository.get_orders(db)
        return [Order.from_orm(order) for order in orders]

    def get_order_by_id(self, db: Session, order_id: int) -> OrderWithItems:
        """Obtener orden por ID con sus items"""
        order = self.order_repository.get_order(db, order_id)
        order_items = self.order_item_repository.get_order_items(db, order_id)
        
        # Convertir a schemas
        order_schema = Order.from_orm(order)
        items_schema = [OrderItem.from_orm(item) for item in order_items]
        
        # Crear OrderWithItems manualmente
        return OrderWithItems(
            id=order_schema.id,
            user_id=order_schema.user_id,
            total=order_schema.total,
            date=order_schema.date,
            items=items_schema
        )

    def get_orders_by_user(self, db: Session, user_id: int) -> List[Order]:
        """Obtener órdenes de un usuario específico"""
        orders = self.order_repository.get_orders_by_user(db, user_id)
        return [Order.from_orm(order) for order in orders]

    def create_order(self, db: Session, order_data: OrderCreate) -> Order:
        """Crear orden simple"""
        created_order = self.order_repository.create_order(
            db, order_data.user_id, order_data.total
        )
        return Order.from_orm(created_order)

    def create_order_from_cart(self, db: Session, user_id: int) -> Dict:
        """
        Crear orden completa desde el carrito del usuario
        Incluye validación, creación de orden, items y limpieza del carrito
        """
        try:
            # 1. Obtener carrito del usuario
            cart = self.cart_repository.get_cart_by_user_id(db, user_id)
            cart_items = self.cart_item_repository.get_cart_items(db, cart.id)
            
            if not cart_items:
                raise HTTPException(status_code=400, detail="Cart is empty")
            
            # 2. Validar stock y calcular totales
            order_items_data = []
            total_amount = 0.0
            
            for cart_item in cart_items:
                # Obtener producto actual
                product = self.product_repository.get_product(db, cart_item.product_id)
                
                # Verificar stock
                if product.stock < cart_item.quantity:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Insufficient stock for {product.name}. Available: {product.stock}, Requested: {cart_item.quantity}"
                    )
                
                # Calcular totales
                item_total = product.price * cart_item.quantity
                total_amount += item_total
                
                # Preparar datos para order items
                order_items_data.append({
                    "product_id": product.id,
                    "quantity": cart_item.quantity,
                    "price": product.price  # Precio al momento de la compra
                })
            
            # 3. Crear la orden
            created_order = self.order_repository.create_order(db, user_id, total_amount)
            
            # 4. Crear los order items
            order_items_for_creation = []
            for item_data in order_items_data:
                order_items_for_creation.append({
                    "order_id": created_order.id,
                    "product_id": item_data["product_id"],
                    "quantity": item_data["quantity"],
                    "price": item_data["price"]
                })
            
            created_order_items = self.order_item_repository.create_multiple_order_items(
                db, order_items_for_creation
            )
            
            # 5. Convertir a schemas para respuesta
            order_schema = Order.from_orm(created_order)
            items_schema = [OrderItem.from_orm(item) for item in created_order_items]
            
            order_with_items = OrderWithItems(
                id=order_schema.id,
                user_id=order_schema.user_id,
                total=order_schema.total,
                date=order_schema.date,
                items=items_schema
            )
            
            return {
                "success": True,
                "order": order_with_items,
                "items_count": len(created_order_items),
                "total_amount": total_amount,
                "cart_items_processed": order_items_data
            }
            
        except HTTPException:
            # Re-lanzar HTTPExceptions específicas
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error creating order from cart: {str(e)}"
            )

    def create_order_with_items(self, db: Session, user_id: int, items_data: List[Dict]) -> OrderWithItems:
        """
        Crear orden con items específicos (no desde carrito)
        items_data: [{"product_id": int, "quantity": int}, ...]
        """
        try:
            # 1. Validar productos y calcular total
            total_amount = 0.0
            validated_items = []
            
            for item in items_data:
                product = self.product_repository.get_product(db, item["product_id"])
                
                if product.stock < item["quantity"]:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Insufficient stock for {product.name}"
                    )
                
                item_total = product.price * item["quantity"]
                total_amount += item_total
                
                validated_items.append({
                    "product_id": product.id,
                    "quantity": item["quantity"],
                    "price": product.price
                })
            
            # 2. Crear orden
            created_order = self.order_repository.create_order(db, user_id, total_amount)
            
            # 3. Crear order items
            order_items_for_creation = []
            for item in validated_items:
                order_items_for_creation.append({
                    "order_id": created_order.id,
                    **item
                })
            
            created_order_items = self.order_item_repository.create_multiple_order_items(
                db, order_items_for_creation
            )
            
            # 4. Convertir a schema
            order_schema = Order.from_orm(created_order)
            items_schema = [OrderItem.from_orm(item) for item in created_order_items]
            
            return OrderWithItems(
                id=order_schema.id,
                user_id=order_schema.user_id,
                total=order_schema.total,
                date=order_schema.date,
                items=items_schema
            )
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error creating order with items: {str(e)}"
            )

    def cancel_order(self, db: Session, order_id: int) -> Dict:
        """
        Cancelar orden y restaurar stock de productos
        """
        try:
            # 1. Obtener orden y sus items
            order = self.order_repository.get_order(db, order_id)
            order_items = self.order_item_repository.get_order_items(db, order_id)
            
            # 2. Restaurar stock de cada producto
            for item in order_items:
                try:
                    # Obtener producto actual
                    product = self.product_repository.get_product(db, item.product_id)
                    # Restaurar stock
                    new_stock = product.stock + item.quantity
                    
                    # Actualizar producto (necesitarás este método en ProductService)
                    updated_data = {
                        'name': product.name,
                        'price': product.price,
                        'description': product.description,
                        'category': product.category,
                        'stock': new_stock,
                        'image': product.image
                    }
                    
                    from app.repositories.models.product_model import ProductModel
                    product_model = ProductModel(**updated_data)
                    self.product_repository.update_product(db, item.product_id, product_model)
                    
                except Exception as stock_error:
                    # Log error pero continúa con otros productos
                    print(f"Error restoring stock for product {item.product_id}: {stock_error}")
            
            # 3. Eliminar la orden (esto también eliminará los order_items por cascade)
            deleted_order = self.order_repository.delete_order(db, order_id)
            
            return {
                "success": True,
                "message": "Order cancelled successfully",
                "cancelled_order": Order.from_orm(deleted_order),
                "stock_restored": len(order_items)
            }
            
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Error cancelling order: {str(e)}"
            )

    def get_order_total(self, db: Session, order_id: int) -> Dict:
        """Obtener resumen de totales de una orden"""
        order = self.order_repository.get_order(db, order_id)
        order_items = self.order_item_repository.get_order_items(db, order_id)
        
        total_items = sum(item.quantity for item in order_items)
        
        return {
            "order_id": order.id,
            "user_id": order.user_id,
            "total_amount": order.total,
            "total_items": total_items,
            "date": order.date,
            "items_count": len(order_items)
        }