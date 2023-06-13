from pydantic import BaseModel

class Comentario(BaseModel):
    idCancion: str
    autor: str
    comentario: str
    fechaDeComentario: str