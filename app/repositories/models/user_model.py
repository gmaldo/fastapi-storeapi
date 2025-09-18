from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from app.repositories.database import Base


class UserModel(Base):
    __tablename__ = "user"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    
    # Relaciones
    cart = relationship("CartModel", back_populates="user", uselist=False)  # 1:1
    orders = relationship("OrderModel", back_populates="user")  # 1:N