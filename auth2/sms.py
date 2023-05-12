import logging
from twilio.base.exceptions import TwilioException
from twilio.rest import Client

ACCOUNT_SID = "ACa1798984f2c792be94d69386d82b96d7"
AUTH_TOKEN = "c878f0f4321d428ecf8f3bb0b35bf743"

class SMS:
    def __init__(self) -> None:
        self._cliente : Client = Client(ACCOUNT_SID, AUTH_TOKEN)
    
    def mandarMensajeOTP(self,codigoOTP: str, numeroDestino : str) -> None:
        try:
            self._cliente.messages.create(
                body=f"El codigo de acceso es: {codigoOTP}",
                from_= "+522282105531",
                to=numeroDestino)
        except TwilioException as e:
            logging.exception(f"Ha ocurrido un error al mandar el mensaje al número {numeroDestino}: {str(e)}")
