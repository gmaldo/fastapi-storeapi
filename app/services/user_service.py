from sqlalchemy.orm import Session
from fastapi import HTTPException
from typing import List

from app.repositories.user_repository import UserRepository
from app.repositories.cart_repository import CartRepository
from app.schemas.user_schema import User, UserCreate, UserUpdate
from app.repositories.models.user_model import UserModel


class UserService:
    def __init__(self):
        self.user_repository = UserRepository()
        self.cart_repository = CartRepository()

    def get_all_users(self, db: Session) -> List[User]:
        """Obtener todos los usuarios"""
        users = self.user_repository.get_users(db)
        return [User.from_orm(user) for user in users]

    def get_user_by_id(self, db: Session, user_id: int) -> User:
        """Obtener usuario por ID"""
        user = self.user_repository.get_user(db, user_id)
        return User.from_orm(user)

    def get_user_by_email(self, db: Session, email: str) -> User:
        """Obtener usuario por email"""
        user = self.user_repository.get_user_by_email(db, email)
        return User.from_orm(user)

    def create_user(self, db: Session, user_data: UserCreate) -> User:
        """Crear nuevo usuario y su carrito automáticamente"""
        # Crear el modelo para el repository
        user_model = UserModel(
            name=user_data.name,
            email=user_data.email
        )
        
        # Crear usuario
        created_user = self.user_repository.create_user(db, user_model)
        
        # Crear carrito automáticamente para el nuevo usuario
        try:
            self.cart_repository.create_cart(db, created_user.id)
        except HTTPException:
            # Si ya existe carrito, continuar (no debería pasar, pero por seguridad)
            pass
        
        return User.from_orm(created_user)

    def update_user(self, db: Session, user_id: int, user_data: UserUpdate) -> User:
        """Actualizar usuario existente"""
        # Obtener datos actuales del usuario
        current_user = self.user_repository.get_user(db, user_id)
        
        # Crear modelo con datos actualizados
        updated_data = current_user.__dict__.copy()
        
        # Actualizar solo los campos proporcionados
        if user_data.name is not None:
            updated_data['name'] = user_data.name
        if user_data.email is not None:
            updated_data['email'] = user_data.email
        
        user_model = UserModel(
            name=updated_data['name'],
            email=updated_data['email']
        )
        
        updated_user = self.user_repository.update_user(db, user_id, user_model)
        return User.from_orm(updated_user)

    def delete_user(self, db: Session, user_id: int) -> dict:
        """Eliminar usuario (esto también eliminará su carrito por cascade)"""
        deleted_user = self.user_repository.delete_user(db, user_id)
        return {
            "message": f"User {deleted_user.name} deleted successfully",
            "deleted_user": User.from_orm(deleted_user)
        }

    def check_user_exists(self, db: Session, user_id: int) -> bool:
        """Verificar si un usuario existe"""
        try:
            self.user_repository.get_user(db, user_id)
            return True
        except HTTPException:
            return False