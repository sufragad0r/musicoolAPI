from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, InvalidURI, ConfigurationError, OperationFailure
from pymongo.database import Database
import logging

logging.basicConfig(
    level=logging.INFO,
    filename='conector.log',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class Conector:
    _host : MongoClient = None

    def __init__(self, uri : str ="mongodb://dev:dev@localhost/?authSource=admin") -> None:
        try:
            self._host : MongoClient = MongoClient(uri)
            logging.info("Conexión exitosa a la base de datos.")
        except (ConnectionFailure, InvalidURI, ConfigurationError, OperationFailure) as e:
            logging.error(f"Error al conectarse a la base de datos: {e}")

    def conectarUsuarios(self) -> Database:
        try:
            db = self._host.usuarios
            logging.info("Conexión a la colección 'usuarios' exitosa.")
            return db
        except (AttributeError, OperationFailure) as e:
            logging.error(f"Error al conectar a la base de datos: {e}")
