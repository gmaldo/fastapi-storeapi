from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.repositories.database import Base


class CartModel(Base):
    __tablename__ = "cart"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("user.id"), nullable=False, unique=True)
    
    # Relaciones
    user = relationship("UserModel", back_populates="cart", uselist=False)  # 1:1
    items = relationship("CartItemModel", back_populates="cart", cascade="all, delete-orphan")  # 1:N


class CartItemModel(Base):
    __tablename__ = "cart_item"

    id = Column(Integer, primary_key=True, index=True)
    cart_id = Column(Integer, ForeignKey("cart.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("product.id"), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    
    # Relaciones
    cart = relationship("CartModel", back_populates="items")
    product = relationship("ProductModel")