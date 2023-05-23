import logging
from obj.otp import OTP
from dao.mongoConector import Conector
from pymongo.errors import PyMongoError
from pymongo.collection import Collection
from datetime import datetime

logging.basicConfig(
    level=logging.DEBUG,
    filename='usuarioDAO.log',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
 
class OTPDAO :
    db = Database = None
    
    def __init__(self) -> None:
        try:
            self.db = Conector().conectarBD()
        except PyMongoError as e:
            logging.error(f"Error al conectar a la base de datos: {e}")
    
    def crear_usuarioOTP(self, otp: OTP) -> bool:
        try:
            datos: Collection = self.db.otp

            if datos.find_one({"username": otp.username}):
                logging.warning(f"Usuario ya existente en la BD")
                return False

            datos.insert_one(dict(otp))
            logging.info(f"Usuario creado: {otp.username}")
            return True

        except PyMongoError as e:
            logging.error(f"Error al crear el usuario: {e}")
            return False
        
    def obtenerUsuarioOTP(self, otp: OTP) -> OTP:
        try:
            datos: Collection = self.db.otp

            OTPDict = datos.find_one({"username": otp.username})
            if OTPDict:
                usuario = OTP(username=OTPDict["username"], codigo=OTPDict["codigo"])
                logging.info(f"Usuario obtenido: {otp.username}")
                return usuario

            logging.warning(f"Usuario no encontrado en la BD: {otp.username}")
            return None

        except PyMongoError as e:
            logging.error(f"Error al obtener el usuario: {e}")
            return None
        
    def actualizarUsuarioOTP(self, username: str, otp: str) -> bool:
        try:
            datos: Collection = self.db.otp

            if not datos.find_one({"username": username}):
                logging.warning(f"Usuario no encontrado en la BD: {username}")
                return False

            datos.update_one({"username": username}, {"otp": otp})
            logging.info(f"otp actualizado de: {username}")
            return True

        except PyMongoError as e:
            logging.error(f"Error al actualizar el OTP de: {e}")
            return False
    
    def eliminarOTP(self, username: str) -> bool:
        try:
            datos: Collection = self.db.otp

            if not datos.find_one({"username": username}):
                logging.warning(f"Usuario no encontrado en la BD: {username}")
                return False

            datos.delete_one({"username": username})
            logging.info(f"Usuario eliminado: {username}")
            return 0

        except PyMongoError as e:
            logging.error(f"Error al eliminar el usuario: {e}")
            return -2

    def autenticar_OTP(self, username: str, otp: str) -> bool:
        try:
            datos: Collection = self.db.otp

            OTPDict = datos.find_one({"username": username})

            if not OTPDict:
                logging.warning(f"OTP no encontrado en la BD: {username}")
                return False
            
            if datetime.now() > OTPDict["expiracion"]:
                logging.warning(f"Codigo otp de: {username} vencido")
                self.eliminarOTP(username)
                return False

            if otp == OTPDict["codigo"]:
                logging.info(f"OTP obtenido: {username}")
                self.eliminarOTP(username)
                return True

        except PyMongoError as e:
            logging.error(f"Error al obtener el usuario: {e}")
            return False