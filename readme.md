# Como correr la api
## Crear el entorno virtual
En windows 
```bash
python -m venv venv
```
En linux
```bash
python3 -m venv venv
```

## Activar el entorno virtal
linux
```bash
source venv/bin/activate
```
En windows
```bash
venv\Scripts\activate.bat
```
## Instalar los requerimientos
En windows y linux
```bash
pip install -r requirements.txt
```
## Corrrer el contenedor de mongo db y el cliente mongo express
```bash
docker compose up -d
```
## Documentacion de la api
http://127.0.0.1:8000/docs
## Cliente de mongo db
http://localhost:8200/db/musicooldb/usuarios