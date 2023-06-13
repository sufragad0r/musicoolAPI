# Como correr la api
## Corrrer el contenedor de mongo db y el cliente mongo express
+ Primero se tendra que crear un archivo .env con las credenciales de twilio
```bash
ACCOUNT_SID=
AUTH_TOKEN=
```
Despues ejecutar el docker compose
```bash
docker compose up -d
```
## Documentacion de la api
http://127.0.0.1:8000/docs
## Cliente de mongo db
http://localhost:8200/db/musicooldb/usuarios

## Api rest
http://localhost:8000/docs

# Generalidades
+ Se manejan dos volumenes 
  + Uno para la biblioteca donde se guardan las imagenes de las canciones y las canciones en si
  + El otro para la persistencia de bases de datos de mongo





# Servidor grpc (No se implemento al final)
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