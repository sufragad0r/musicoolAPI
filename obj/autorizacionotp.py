from pydantic import BaseModel

class autorizacionOTP(BaseModel):
    solicitarOTP: str
    info: str
