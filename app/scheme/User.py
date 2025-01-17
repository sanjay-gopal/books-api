from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    token_type: str

class UserRequest(BaseModel):
    username: str
    password: str