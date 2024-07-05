import datetime

from uuid import uuid4
from tinydb import where

from models.Query import Query
from database import db


class QueryRepository:

    @staticmethod
    def find_one_by_id(id: str) -> Query:
        try:
            query = db.table("queries").search(where("id") == id)[0]
            return query
        except IndexError:
            raise IndexError("Query not found")
        
    @staticmethod
    def find_one_unanswered_query(user_id: str, file_id: str) -> Query:
        try:
            query = db.table("queries").search((where("user_id") == user_id) & (where("file_id") == file_id) & (where("answer") == None))[0]
            return query
        except IndexError:
            raise IndexError("All query answered")
        
    @staticmethod
    def find_all_by_user_id(user_id: str) -> Query:
        queries = db.table("queries").search(where("user_id") == user_id)
        return queries
        
    @staticmethod
    def find_all_by_file_id(file_id: str) -> list[Query]:
        queries = db.table("queries").search(where("file_id") == file_id)
        return queries
    
    @staticmethod
    def find_all_by_user_id_and_file_id(file_id: str, user_id: str) -> list[Query]:
        queries = db.table("queries").search((where("file_id") == file_id) & (where("user_id") == user_id))
        return queries
    
    # @staticmethod
    # def find_all() -> list[Session]:
    #     sessions = db.table("sessions").all()
    #     return sessions
    
    @staticmethod
    def create(question: str, file_id: str, user_id: str, answer: str) -> Query:
        now = datetime.datetime.now()
        query = Query(
            id=str(uuid4()),
            file_id = file_id,
            user_id=user_id,
            question = question,
            answer=answer,
            status="pending",
            created_at = now.strftime("%m/%d/%Y, %H:%M:%S")
        )
        db.table("queries").insert({
            "id": query.id,
            "file_id": query.file_id,
            "user_id": query.user_id,
            "question": query.question,
            "answer": query.answer,
            "status": query.status,
            "created_at": query.created_at
        })
        return query.model_dump()
    
    @staticmethod
    def remove(id: str) -> bool:
        db.table("queries").remove(where("id") == id)
        return True
    
    @staticmethod
    def update(id: str, newFields: dict) -> bool:
        db.table("queries").update(newFields, where("id") == id)
        return True

