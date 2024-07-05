import datetime

from uuid import uuid4
from tinydb import Query

from models.User import User
from database import db
from utils.bcrypt import hash_password


class UserRepository:

    @staticmethod
    def find_one_by_id(id: str) -> User:
        try:
            user = db.table("users").search(Query().id == id)[0]
            return user
        except IndexError:
            raise IndexError("User not found")
        
    @staticmethod
    def find_one_by_email(email: str) -> User:
        try:
            user = db.table("users").search(Query().email == email)[0]
            return user
        except IndexError:
            raise IndexError("User not found")
    
    @staticmethod
    def find_all() -> list[User]:
        users = db.table("users").all()
        return users
    
    @staticmethod
    def create(email: str, password: str) -> User:
        now = datetime.datetime.now()
        user = User(
            id=str(uuid4()),
            email = email,
            password = hash_password(password),
            created_at = now.strftime("%m/%d/%Y, %H:%M:%S")
        )
        db.table("users").insert({
            "id": user.id,
            "email": user.email,
            "password": user.password,
            "created_at": user.created_at
        })
        return user.model_dump()
    
    @staticmethod
    def remove(id: str) -> bool:
        db.table("users").remove(Query().id == id)
        return True
    
    @staticmethod
    def update(id: str, newFields: dict) -> bool:
        db.table("users").update(newFields, Query().id == id)
        return True

