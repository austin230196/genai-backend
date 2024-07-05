from pydantic import BaseModel


class Query(BaseModel):
    id: str
    question: str
    answer: str|None
    file_id: str
    user_id: str
    status: str
    created_at: str



