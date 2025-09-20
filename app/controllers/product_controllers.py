from fastapi import APIRouter,Depends
from sqlalchemy.orm import Session

from app.repositories.database import get_db
from app.services import ProductService
from app.schemas import Product, ProductCreate, ProductUpdate

router  = APIRouter(prefix="/products", tags=["Products"])
service = ProductService()

@router.get("/")
def get_products(db: Session = Depends(get_db)):
    return service.get_products(db)

@router.get("/{product_id}")
def get_product(product_id: int,db: Session = Depends(get_db),):
    return service.get_product(db,product_id)

@router.post("/")
def create_product(product: ProductCreate,db: Session = Depends(get_db)):
    return service.create_product(db,product)

@router.put("/{product_id}")
def update_product(product_id: int, product: ProductUpdate, db: Session = Depends(get_db)):
    print("Hola")
    return service.update_product(db, product_id, product)

@router.delete("/{product_id}")
def delete_product(product_id: int,db: Session = Depends(get_db)):
    return service.delete_product(db,product_id)

@router.post("/example")
def create_example_products(db: Session = Depends(get_db)):
    """
    Crear productos de muestra para testing
    """
    try:
        example_products = [
            {
                "name": "iPhone 17 Pro",
                "price": 1500000,
                "description": "Último iPhone con chip Pro y diseño de titanio",
                "category": "Electrónicos",
                "stock": 1,
                "image": "https://example.com/iphone17pro.jpg"
            },
            {
                "name": "MacBook Air M4",
                "price": 3500000,
                "description": "MacBook Air de 13 pulgadas con chip M4, 8GB RAM, 256GB SSD",
                "category": "Electrónicos",
                "stock": 2,
                "image": "https://example.com/macbookair.jpg"
            },
            {
                "name": "Zapatillas Nike Air Max 270",
                "price": 160000,
                "description": "Zapatillas cómodas para correr con tecnología Air Max",
                "category": "Calzado",
                "stock": 3,
                "image": "https://example.com/airmax270.jpg"
            },
            {
                "name": "Zapatillas Adidas Ultraboost 22",
                "price": 190000,
                "description": "Zapatillas premium para correr con suela intermedia Boost",
                "category": "Calzado",
                "stock": 3,
                "image": "https://example.com/ultraboost.jpg"
            },
            {
                "name": "Jeans Levi's 501 Original",
                "price": 100000,
                "description": "Jeans clásicos de corte recto en denim premium",
                "category": "Ropa",
                "stock": 1,
                "image": "https://example.com/levis501.jpg"
            },
            {
                "name": "Sudadera Champion",
                "price": 60000,
                "description": "Sudadera cómoda de mezcla de algodón con logo",
                "category": "Ropa",
                "stock": 2,
                "image": "https://example.com/champion-hoodie.jpg"
            },
            {
                "name": "Auriculares Sony WH-1000XM5",
                "price": 100000,
                "description": "Auriculares inalámbricos premium con cancelación de ruido",
                "category": "Electrónicos",
                "stock": 3,
                "image": "https://example.com/sony-headphones.jpg"
            },
            {
                "name": "Vaso Térmico Stanley 40oz",
                "price": 45000,
                "description": "Vaso térmico de acero inoxidable con asa",
                "category": "Hogar",
                "stock": 1,
                "image": "https://example.com/stanley-tumbler.jpg"
            },
            {
                "name": "Kindle Paperwhite",
                "price": 500000,
                "description": "Lector electrónico resistente al agua con pantalla de 6.8 pulgadas",
                "category": "Electrónicos",
                "stock": 3,
                "image": "https://example.com/kindle.jpg"
            },
            {
                "name": "Botella Térmica Yeti Rambler 20oz",
                "price": 35000,
                "description": "Botella de acero inoxidable con aislamiento de doble pared al vacío",
                "category": "Hogar",
                "stock": 1,
                "image": "https://example.com/yeti-rambler.jpg"
            }
        ]
        
        created_products = []
        successful_count = 0
        errors = []
        
        for product_data in example_products:
            try:
                
                # Crear ProductCreate schema
                from app.schemas.product_schema import ProductCreate
                product_create = ProductCreate(**product_data)
                
                # Crear producto usando el service
                new_product = service.create_product(db, product_create)
                created_products.append({
                    "id": new_product.id,
                    "name": new_product.name,
                    "price": new_product.price,
                    "category": new_product.category
                })
                successful_count += 1
                
            except Exception as e:
                errors.append(f"Error creating '{product_data['name']}': {str(e)}")
        
        return {
            "message": f"Example products creation completed",
            "successful_count": successful_count,
            "total_attempted": len(example_products),
            "created_products": created_products,
            "errors": errors if errors else None
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating example products: {str(e)}"
        )