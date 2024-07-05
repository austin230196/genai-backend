import datetime

from uuid import uuid4
from tinydb import where

from models.Session import Session
from database import db


class SessionRepository:

    @staticmethod
    def find_one_by_id(id: str) -> Session:
        try:
            session = db.table("sessions").search(where("id") == id)[0]
            return session
        except IndexError:
            raise IndexError("Session not found")
        
    @staticmethod
    def find_one_by_user_id(user_id: str) -> Session:
        try:
            session = db.table("sessions").search(where("user_id") == user_id)[0]
            return session
        except IndexError:
            raise IndexError("Session not found")
    
    @staticmethod
    def find_all() -> list[Session]:
        sessions = db.table("sessions").all()
        return sessions
    
    @staticmethod
    def create(user_id: str, user_agent: str) -> Session:
        now = datetime.datetime.now()
        session = Session(
            id=str(uuid4()),
            user_agent = user_agent,
            user_id=user_id,
            expired = False,
            created_at = now.strftime("%m/%d/%Y, %H:%M:%S")
        )
        db.table("sessions").insert({
            "id": session.id,
            "user_agent": session.user_agent,
            "user_id": session.user_id,
            "expired": session.expired,
            "created_at": session.created_at
        })
        return session.model_dump()
    
    @staticmethod
    def remove(id: str) -> bool:
        db.table("sessions").remove(where("id") == id)
        return True
    
    @staticmethod
    def update(id: str, newFields: dict) -> bool:
        db.table("sessions").update(newFields, where("id") == id)
        return True

