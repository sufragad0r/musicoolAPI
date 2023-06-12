from pydantic import BaseModel
from datetime import datetime


class CancionBytes(BaseModel):
    bytes: str
    artista: str
    nombre: str
    fechaDePublicacion: str


class Cancion(BaseModel):
    nombre: str
    artista: str
    fechaDePublicacion: str
