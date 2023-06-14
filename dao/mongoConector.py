import os

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

    def __init__(self, uri: str = "mongodb://dev:dev@mongodb:27017/?authSource=admin") -> None:
        try:
            mongo_host = os.environ.get("MONGO_HOST", "mongodb")
            mongo_port = os.environ.get("MONGO_PORT", "27017")
            uri = f"mongodb://dev:dev@{mongo_host}:{mongo_port}/?authSource=admin"
            self._host: MongoClient = MongoClient(uri)
            logging.info("Conexión exitosa a la base de datos.")
        except (ConnectionFailure, InvalidURI, ConfigurationError, OperationFailure) as e:
            logging.error(f"Error al conectarse a la base de datos: {e}")

    def conectarBD(self) -> Database:
        try:
            db = self._host.musicooldb
            logging.info("Conexión a la bd exitosa.")
            return db
        except (AttributeError, OperationFailure) as e:
            logging.error(f"Error al conectar a la base de datos: {e}")
