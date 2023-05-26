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
            

    def crear_usuario(self, usuarioNuevo: Usuario) -> int:
        try:
            datos: Collection = self.db.usuarios

            if datos.find_one({"username": usuarioNuevo.username}):
                logging.warning(f"Usuario ya existente en la BD")
                return -1

            datos.insert_one(dict(usuarioNuevo))
            logging.info(f"Usuario creado: {usuarioNuevo.username}")
            return 0

        except PyMongoError as e:
            logging.error(f"Error al crear el usuario: {e}")
            return -2

    def obtener_usuario(self, username: str) -> Usuario:
        try:
            datos: Collection = self.db.usuarios

            usuarioDict = datos.find_one({"username": username})
            if usuarioDict:
                usuario = Usuario(username=usuarioDict["username"],password=usuarioDict["password"],telefono=usuarioDict["telefono"], rol=usuarioDict["rol"])
                logging.info(f"Usuario obtenido: {username}")
                return usuario

            logging.warning(f"Usuario no encontrado en la BD: {username}")
            return None

        except PyMongoError as e:
            logging.error(f"Error al obtener el usuario: {e}")
            return None
    
    def actualizar_usuario(self, username: str, campos: dict) -> int:
        try:
            datos: Collection = self.db.usuarios

            if not datos.find_one({"username": username}):
                logging.warning(f"Usuario no encontrado en la BD: {username}")
                return -1

            datos.update_one({"username": username}, {"$set": campos})
            logging.info(f"Usuario actualizado: {username}")
            return 0

        except PyMongoError as e:
            logging.error(f"Error al actualizar el usuario: {e}")
            return -2

    def eliminar_usuario(self, username: str) -> int:
        try:
            datos: Collection = self.db.usuarios

            if not datos.find_one({"username": username}):
                logging.warning(f"Usuario no encontrado en la BD: {username}")
                return -1

            datos.delete_one({"username": username})
            logging.info(f"Usuario eliminado: {username}")
            return 0

        except PyMongoError as e:
            logging.error(f"Error al eliminar el usuario: {e}")
            return -2
    
    def obtener_rol(self, username:str) -> str:
        try:
            datos: Collection = self.db.usuarios

            usuarioDict = datos.find_one({"username": username})
            if usuarioDict:
                rol = usuarioDict["rol"]
                logging.info(f"Rol obtenido: {username}")
                return rol

            logging.warning(f"Usuario no encontrado en la BD: {username}")
            return ""

        except PyMongoError as e:
            logging.error(f"Error al obtener el rol del usuario: {e}")
            return ""