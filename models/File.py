from pydantic import BaseModel


class File(BaseModel):
    id: str
    name: str
    url: str|None
    user_id: str
    created_at: str


