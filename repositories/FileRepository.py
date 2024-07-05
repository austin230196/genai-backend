import datetime

from uuid import uuid4
from tinydb import where

from models.File import File
from database import db


class FileRepository:
    @staticmethod
    def find_one_by_id(id: str) -> File:
        try:
            file = db.table("files").search(where("id") == id)[0]
            return file
        except IndexError:
            raise IndexError("File not found")
        
    @staticmethod
    def find_one_by_name(name: str) -> File:
        try:
            file = db.table("files").search(where("name") == name)[0]
            return file
        except IndexError:
            raise IndexError("File not found")
        
    @staticmethod
    def find_all_by_user_id(user_id: str) -> File:
        files = db.table("files").search(where("user_id") == user_id)
        return files
    
    @staticmethod
    def find_all() -> list[File]:
        files = db.table("files").all()
        return files
    
    @staticmethod
    def create(user_id: str, name: str, url) -> File:
        now = datetime.datetime.now()
        file = File(
            id=str(uuid4()),
            url=url,
            name = name,
            user_id=user_id,
            created_at = now.strftime("%m/%d/%Y, %H:%M:%S")
        )
        db.table("files").insert({
            "id": file.id,
            "url": file.url,
            "name": file.name,
            "user_id": file.user_id,
            "created_at": file.created_at
        })
        return file.model_dump()
    
    @staticmethod
    def remove(id: str) -> bool:
        db.table("files").remove(where("id") == id)
        return True
    
    @staticmethod
    def update(id: str, newFields: dict) -> bool:
        db.table("files").update(newFields, where("id") == id)
        return True
