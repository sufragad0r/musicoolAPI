from pydantic import BaseModel
from datetime import datetime

class Usuario(BaseModel):
    username: str
    password: str
    telefono: str