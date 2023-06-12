import logging
from dao.mongoConector import Conector
from pymongo.errors import PyMongoError
from pymongo.database import Database
from obj.cancion import Cancion
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
    def buscar_cancion(self, cancion:Cancion) -> str:
        try:
            query = {
                "artista": {"$regex": cancion.artista, "$options": "i"},
                "nombre": {"$regex": cancion.nombre, "$options": "i"}
            }
            existing_cancion = self.db.canciones.find_one(query, collation={"locale": "en", "strength": 1})
            if existing_cancion is not None:
                idCancion = str(existing_cancion["_id"])
                return idCancion
        except PyMongoError as e:
            logging.error(f"Error al buscar la canción: {e}")
