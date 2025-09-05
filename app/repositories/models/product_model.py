from sqlalchemy import Column, Integer, String, Float
from app.repositories.database import Base

class ProductModel(Base):
    __tablename__ = "product"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    price = Column(Float)
    description = Column(String)
    category = Column(String)
    stock = Column(Integer)
    image = Column(String)