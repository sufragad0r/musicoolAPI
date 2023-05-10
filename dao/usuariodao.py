import logging
from obj.usuario import Usuario
from dao.mongoConector import Conector
from pymongo.errors import PyMongoError
from pymongo.database import Database
from pymongo.collection import Collection

logging.basicConfig(
    level=logging.DEBUG,
    filename='usuarioDAO.log',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class UsuarioDAO:
    db: Database = None

    def __init__(self) -> None:
        try:
            self.db = Conector().conectarBD()
        except PyMongoError as e:
            logging.error(f"Error al conectar a la base de datos: {e}")
            

    def crearUsuario(self, usuarioNuevo: Usuario) -> int:
        try:
            datos: Collection = self.db.usuariosColeccion

            if datos.find_one({"username": usuarioNuevo.username}):
                logging.warning(f"Usuario ya existente en la BD")
                return -1

            datos.insert_one(dict(usuarioNuevo))
            logging.info(f"Usuario creado: {usuarioNuevo.username}")
            return 0

        except PyMongoError as e:
            logging.error(f"Error al crear el usuario: {e}")
            return -2

    def obtenerUsuario(self, username: str) -> Usuario:
        try:
            datos: Collection = self.db.usuariosColeccion

            usuarioDict = datos.find_one({"username": username})
            if usuarioDict:
                usuario = Usuario(username=usuarioDict["username"],password=usuarioDict["password"])
                logging.info(f"Usuario obtenido: {username}")
                return usuario

            logging.warning(f"Usuario no encontrado en la BD: {username}")
            return None

        except PyMongoError as e:
            logging.error(f"Error al obtener el usuario: {e}")
            return None
    
    def actualizarUsuario(self, username: str, campos: dict) -> int:
        try:
            datos: Collection = self.db.usuariosColeccion

            if not datos.find_one({"username": username}):
                logging.warning(f"Usuario no encontrado en la BD: {username}")
                return -1

            datos.update_one({"username": username}, {"$set": campos})
            logging.info(f"Usuario actualizado: {username}")
            return 0

        except PyMongoError as e:
            logging.error(f"Error al actualizar el usuario: {e}")
            return -2

    def eliminarUsuario(self, username: str) -> int:
        try:
            datos: Collection = self.db.usuariosColeccion

            if not datos.find_one({"username": username}):
                logging.warning(f"Usuario no encontrado en la BD: {username}")
                return -1

            datos.delete_one({"username": username})
            logging.info(f"Usuario eliminado: {username}")
            return 0

        except PyMongoError as e:
            logging.error(f"Error al eliminar el usuario: {e}")
            return -2