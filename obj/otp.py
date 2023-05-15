from pydantic import BaseModel
from datetime import datetime

class OTP(BaseModel):
    username: str
    codigo: str
    expiracion: datetime