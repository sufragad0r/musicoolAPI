from pydantic import BaseModel

class OTP(BaseModel):
    username: str
    codigo: str