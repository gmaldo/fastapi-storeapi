from sqlalchemy import Column, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from app.repositories.database import Base


class OrderModel(Base):
    __tablename__ = "order"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    total = Column(Float, nullable=False)
    date = Column(DateTime, default=datetime.utcnow, nullable=False)
    
    # Relaciones
    user = relationship("UserModel", back_populates="orders")  # N:1
    items = relationship("OrderItemModel", back_populates="order", cascade="all, delete-orphan")  # 1:N


class OrderItemModel(Base):
    __tablename__ = "order_item"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("order.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("product.id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)  # Precio al momento de la compra
    
    # Relaciones
    order = relationship("OrderModel", back_populates="items")
    product = relationship("ProductModel")