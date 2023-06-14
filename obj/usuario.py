from pydantic import BaseModel

class Usuario(BaseModel):
    username: str
    password: str
    telefono: str
    rol: str