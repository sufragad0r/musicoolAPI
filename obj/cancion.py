from pydantic import BaseModel

class Cancion(BaseModel):
    bytes: str
    nombre: str
    artista: str
    fecha_de_publicacion: str
    url: str
