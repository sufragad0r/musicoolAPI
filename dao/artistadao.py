import logging
from obj.artista import Artista
from dao.mongoConector import Conector
from pymongo.errors import PyMongoError
from pymongo.database import Database
from pymongo.collection import Collection

logging.basicConfig(
    level=logging.DEBUG,
    filename='usuarioDAO.log',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class ArtistaDAO:
    db: Database = None

    def __init__(self) -> None:
        try:
            self.db = Conector().conectarBD()
        except PyMongoError as e:
            logging.error(f"Error al conectar a la base de datos: {e}")
            

    def crear_artista(self, artistaNuevo: Artista) -> int:
        try:
            datos: Collection = self.db.artistas

            if datos.find_one({"username": artistaNuevo.username}):
                logging.warning(f"Artista ya existente en la BD")
                return -1

            datos.insert_one(dict(artistaNuevo))
            logging.info(f"Artista creado: {artistaNuevo.username}")
            return 0

        except PyMongoError as e:
            logging.error(f"Error al crear el artista: {e}")
            return -2

    def obtener_artista(self, username: str) -> Artista:
        try:
            datos: Collection = self.db.artistas

            usuarioDict = datos.find_one({"username": username})
            if usuarioDict:
                usuario = Artista(username=usuarioDict["username"], nombreComercial=usuarioDict["nombreComercial"], mailComercial=usuarioDict["mailComercial"])
                logging.info(f"Artista obtenido: {username}")
                return usuario

            logging.warning(f"Artista no encontrado en la BD: {username}")
            return None

        except PyMongoError as e:
            logging.error(f"Error al obtener el artista: {e}")
            return None
    
    def actualizar_artista(self, username: str, campos: dict) -> int:
        try:
            datos: Collection = self.db.artistas

            if not datos.find_one({"username": username}):
                logging.warning(f"Artista no encontrado en la BD: {username}")
                return -1

            datos.update_one({"username": username}, {"$set": campos})
            logging.info(f"Artista actualizado: {username}")
            return 0

        except PyMongoError as e:
            logging.error(f"Error al actualizar el artista: {e}")
            return -2

    def eliminar_artista(self, username: str) -> int:
        try:
            datos: Collection = self.db.artistas

            if not datos.find_one({"username": username}):
                logging.warning(f"Artista no encontrado en la BD: {username}")
                return -1

            datos.delete_one({"username": username})
            logging.info(f"Artista eliminado: {username}")
            return 0

        except PyMongoError as e:
            logging.error(f"Error al eliminar el usuario: {e}")
            return -2