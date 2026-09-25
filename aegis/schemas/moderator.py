from pydantic import BaseModel

class TokenEnvelope(BaseModel):
    access_token: str
    token_type: str

class ModeratorLoginRequest(BaseModel):
    username: str
    password: str