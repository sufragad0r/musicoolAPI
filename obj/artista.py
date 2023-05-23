from pydantic import BaseModel

class Artista(BaseModel):
    username: str
    nombreComercial : str
    mailComercial :  str