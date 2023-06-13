# Utiliza la imagen base de Python
FROM python:3.9

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

# Agrega las variables de entorno
ENV ACCOUNT_SID=<valor_account_sid>
ENV AUTH_TOKEN=<valor_auth_token>
# Comando para iniciar tu aplicación FastAPI
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]