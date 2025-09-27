from pydantic import BaseModel
from typing import Optional

class UserInfo(BaseModel):
    name: Optional[str] = None
    school: Optional[str] = None
    home: Optional[str] = None

class MessageRequest(BaseModel):
    text: str
    user_info: UserInfo

class MessageResponse(BaseModel):
    reply: str
