import random

def generarCodigoOTP() -> str:
    return f"{random.randint(100000,999999)}"