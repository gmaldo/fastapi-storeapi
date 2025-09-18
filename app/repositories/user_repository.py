from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.repositories.models.user_model import UserModel


class UserRepository:

    def get_users(self, db: Session):
        return db.query(UserModel).all()

    def get_user(self, db: Session, user_id: int):
        user = db.query(UserModel).filter_by(id=user_id).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    def get_user_by_email(self, db: Session, email: str):
        user = db.query(UserModel).filter_by(email=email).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        return user

    def create_user(self, db: Session, user: UserModel):
        # Verificar si el email ya existe
        existing_user = db.query(UserModel).filter_by(email=user.email).first()
        if existing_user:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        new_user = UserModel(
            name=user.name,
            email=user.email
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user

    def update_user(self, db: Session, user_id: int, user: UserModel):
        db_user = db.query(UserModel).filter_by(id=user_id).first()
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Verificar si el nuevo email ya existe (solo si es diferente al actual)
        if user.email != db_user.email:
            existing_user = db.query(UserModel).filter_by(email=user.email).first()
            if existing_user:
                raise HTTPException(status_code=400, detail="Email already registered")
        
        db_user.name = user.name
        db_user.email = user.email
        db.commit()
        db.refresh(db_user)
        return db_user

    def delete_user(self, db: Session, user_id: int):
        db_user = db.query(UserModel).filter_by(id=user_id).first()
        if not db_user:
            raise HTTPException(status_code=404, detail="User not found")
        
        db.delete(db_user)
        db.commit()
        return db_user