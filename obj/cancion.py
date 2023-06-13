from pydantic import BaseModel


class CancionBytes(BaseModel):
    bytes: str
    artista: str
    nombre: str
    fechaDePublicacion: str


class Cancion(BaseModel):
    nombre: str
    artista: str
    fechaDePublicacion: str


class CancionResultado(BaseModel):
    id: str
    nombre: str
    artista: str
    fechaDePublicacion: str
