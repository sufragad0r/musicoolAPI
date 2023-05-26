import logging
from dao.mongoConector import Conector
from pymongo.errors import PyMongoError
from pymongo.database import Database
from obj.cancion import Cancion

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
            result = self.db.canciones.insert_one(cancion.dict())
            if result.inserted_id:
                return str(result.inserted_id)
        except PyMongoError as e:
            logging.error(f"Error al crear la canción: {e}")
        return None