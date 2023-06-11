# Imagen base
FROM python:3.9

# Establecer el directorio de trabajo en el contenedor
WORKDIR /app

# Copiar los archivos del proyecto al contenedor
COPY ./requirements.txt /code/requirements.txt

# Instalar las dependencias del proyecto
RUN pip install --no-cache-dir --upgrade -r /code/requirements.txt

COPY ./auth2 /code/app
COPY ./dao /code/app
COPY ./fm /code/app
COPY ./obj /code/app
COPY ./sec /code/app

ENV TWILIO_SID valor1
ENV TWILIO_TOKEN valor2

# Exponer el puerto en el que se ejecuta la aplicación FastAPI
EXPOSE 8000

# Comando para iniciar la aplicación FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
