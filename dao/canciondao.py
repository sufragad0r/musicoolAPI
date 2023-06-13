import logging

from bson import ObjectId
from bson.errors import InvalidId

from dao.mongoConector import Conector
from pymongo.errors import PyMongoError
from pymongo.database import Database
from obj.cancion import Cancion, CancionResultado
from datetime import date

logging.basicConfig(
    level=logging.DEBUG,
    filename='cancionDAO.log',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


class CancionDAO:
    db: Database = None
    collection_name = 'canciones'

    def __init__(self) -> None:
        try:
            self.db = Conector().conectarBD()
        except PyMongoError as e:
            logging.error(f"Error al conectar a la base de datos: {e}")

    def crear_cancion(self, cancion: Cancion) -> str:
        try:
            query = {
                "artista": cancion.artista,
                "nombre": cancion.nombre
            }
            existing_cancion = self.db.canciones.find_one(query)
            if existing_cancion:
                logging.warning(
                    "No se puede crear la canción: Ya existe una canción con el mismo artista y nombre de canción")
                return None
            cancion.fechaDePublicacion = date.today().strftime("%Y-%m-%d")
            result = self.db.canciones.insert_one(cancion.dict())
            if result.inserted_id:
                return str(result.inserted_id)
        except PyMongoError as e:
            logging.error(f"Error al crear la canción: {e}")
        return None

    def buscar_cancion(self, cancion: Cancion) -> CancionResultado:
        try:
            query = {
                "artista": {"$regex": cancion.artista, "$options": "i"},
                "nombre": {"$regex": cancion.nombre, "$options": "i"}
            }
            existing_cancion = self.db.canciones.find_one(query, projection={"_id": 1, "nombre": 1, "artista": 1,
                                                                             "fechaDePublicacion": 1},
                                                          collation={"locale": "en", "strength": 1})
            if existing_cancion is not None:
                cancionRes = CancionResultado(id=str(existing_cancion["_id"]), nombre=existing_cancion["nombre"],
                                              artista=existing_cancion["artista"],
                                              fechaDePublicacion=existing_cancion["fechaDePublicacion"])
                return cancionRes
            return None
        except PyMongoError as e:
            logging.error(f"Error al buscar la canción: {e}")

    def comentarCancion(self, id_cancion, autor, comentario):
        comentario = {"autor": autor, "comentario": comentario}
        query = {"_id": id_cancion}
        update = {"$push": {"foro": comentario}}
        try:
            self.db.canciones.update_one(query, update)
            return True
        except Exception as e:
            print(f"Error al comentar la canción: {e}")
            return None

    def buscar_foro(self, id_cancion):
        registro = self.db.canciones.find_one({"_id": ObjectId(id_cancion)})
        comentarios = registro["foro"]
        return comentarios

    def buscar_id_cancion(self, id: str) -> bool:
        try:
            filtro = {"_id": ObjectId(id)}
            resultado = self.db.canciones.find_one(filtro)
            return resultado is not None
        except InvalidId as e:
            logging.error(f"ID inválido: {e}")
            return False
        except PyMongoError as e:
            logging.error(f"Error al buscar la canción: {e}")
            return False
