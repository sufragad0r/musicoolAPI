import logging
from twilio.base.exceptions import TwilioException
from twilio.rest import Client
import os
import random

ACCOUNT_SID = os.environ.get("TWILIO_SID") 
AUTH_TOKEN = os.environ.get("TWILIO_TOKEN")

def generarCodigoOTP() -> str:
    return f"{random.randint(100000,999999)}"

class SMS:
    def __init__(self) -> None:
        self._cliente : Client = Client(ACCOUNT_SID, AUTH_TOKEN)
    
    def mandarMensajeOTP(self,codigoOTP: str, numeroDestino : str) -> None:
        try:
            self._cliente.messages.create(
                body=f"El codigo de acceso es: {codigoOTP}",
                from_= "+12545664494",
                to=numeroDestino)
        except TwilioException as e:
            logging.exception(f"Ha ocurrido un error al mandar el mensaje al número {numeroDestino}: {str(e)}")
