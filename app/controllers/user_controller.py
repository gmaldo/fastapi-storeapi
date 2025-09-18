from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.repositories.database import get_db
from app.services.user_service import UserService
from app.schemas.user_schema import User, UserCreate


router = APIRouter(
    prefix="/users",
    tags=["users"]
)

user_service = UserService()


@router.get("/", response_model=List[User])
def get_all_users(db: Session = Depends(get_db)):
    """
    Obtener todos los usuarios
    """
    try:
        users = user_service.get_all_users(db)
        return users
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving users"
        )


@router.get("/{user_id}", response_model=User)
def get_user(user_id: int, db: Session = Depends(get_db)):
    """
    Obtener usuario por ID
    """
    try:
        user = user_service.get_user_by_id(db, user_id)
        return user
    except HTTPException:
        # Re-lanzar HTTPExceptions del service/repository
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error retrieving user"
        )


@router.post("/", response_model=User, status_code=status.HTTP_201_CREATED)
def create_user(user_data: UserCreate, db: Session = Depends(get_db)):
    """
    Crear nuevo usuario con nombre y email.
    Automáticamente crea un carrito para el usuario.
    """
    try:
        new_user = user_service.create_user(db, user_data)
        return new_user
    except HTTPException:
        # Re-lanzar HTTPExceptions del service/repository (ej: email duplicado)
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error creating user"
        )