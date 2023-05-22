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

#Servidor grpc
Crear los protos
+ Para crear los protos es necesario instalar protoc
https://github.com/protocolbuffers/protobuf/releases
+ Correr el siguiente comando
````bash
protoc --go_out=. --go-grpc_out=. cancion.proto
````
+ Ejecutar el servidor
````bash
cd grpc-musicool/servidor
go run main.go
````