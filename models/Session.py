from pydantic import BaseModel


class Session(BaseModel):
    id: str
    user_agent: str
    user_id: str
    expired: bool
    created_at: str



