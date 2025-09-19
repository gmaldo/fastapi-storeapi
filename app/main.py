from fastapi import FastAPI
from app.controllers import product_router, user_router,cart_router,order_router
from app.repositories.database import Base, engine
# Import all models to ensure they're registered with SQLAlchemy
from app.repositories.models import *

# creo mi instancia de FastAPI
app = FastAPI()
Base.metadata.create_all(bind=engine)

app.include_router(router=product_router)
app.include_router(router=user_router)
app.include_router(router=cart_router)
app.include_router(router=order_router)