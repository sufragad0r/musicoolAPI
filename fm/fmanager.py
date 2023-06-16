import base64
import os
import logging

from fastapi import UploadFile

logging.basicConfig(filename='fmanager.log', level=logging.ERROR)

RUTA_BIBLIOTECA: str = "Biblioteca"

def generar_stream_bytes_mp3(file_path: str) -> None:
    try:
        with open(file_path, "rb") as file:
            mp3_bytes = file.read()
            mp3_base64 = base64.b64encode(mp3_bytes).decode("utf-8")
            json_data = {"Bytes": mp3_base64}
            return json_data
    except Exception as e:
        print(f"Error al generar los bytes del archivo MP3: {e}")

def guardar_bytes_como_mp3(cancion: dict, mp3_file_path: str) -> None:
    try:
        mp3_bytes = base64.b64decode(cancion["bytes"])  # Decodificar los datos en base64
        with open(mp3_file_path, "wb") as mp3_file:
            mp3_file.write(mp3_bytes)  # Guardar los bytes en un archivo MP3
    except Exception as e:
        print(f"Error al guardar los bytes como archivo MP3: {e}")

def verificar_carpeta_existente(ruta: str, nombre_carpeta: str) -> bool:
    try:
        ruta_carpeta = os.path.join(ruta, nombre_carpeta)
        return os.path.exists(ruta_carpeta) and os.path.isdir(ruta_carpeta)
    except Exception as e:
        print(f"Error al verificar la existencia de la carpeta: {e}")
        return False

def crear_carpeta(ruta: str, nombre_carpeta: str) -> None:
    try:
        ruta_carpeta = os.path.join(ruta, nombre_carpeta)
        os.makedirs(ruta_carpeta, exist_ok=True)
    except Exception as e:
        print(f"Error al crear la carpeta: {e}")

class FManager:
    def __init__(self) -> None:
        self.rutaBiblioteca = RUTA_BIBLIOTECA



    async def guardar_imagen(self, documento: UploadFile, nombre_documento: str):
        image_path = f"{self.rutaBiblioteca}/{nombre_documento}.jpg"
        with open(image_path, "wb") as buffer:
            buffer.write(await documento.read())

    async def guardar_cancion(self, documento: UploadFile, nombre_documento: str):
        image_path = f"{self.rutaBiblioteca}/{nombre_documento}.mp3"
        with open(image_path, "wb") as buffer:
            buffer.write(await documento.read())
