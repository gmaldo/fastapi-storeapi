from fastapi import FastAPI
from app.controllers import product_router
from app.repositories.database import Base,engine
# creo mi instancia de FastAPI

app = FastAPI()
Base.metadata.create_all(bind=engine)

app.include_router(router=product_router)