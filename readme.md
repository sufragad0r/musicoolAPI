# Como correr la api
## Corrrer el contenedor de mongo db, el cliente mongo express y la api de musicool
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
http://localhost:8000/docs
## Cliente de mongo db
http://localhost:8200/db/musicooldb/usuarios



# Generalidades
+ Se manejan dos volumenes 
  + Uno para la biblioteca donde se guardan las imagenes de las canciones y las canciones en si
  + El otro para la persistencia de bases de datos de mongo
  
Cuando la api rest agrega una nueva cancion o imagen a la biblioteca, en la maquina donde se ejecute docker
aparecera la carpeta biblioteca actualizada

Este mismo proceso pasa con la carpeta mongo-data solo que quien modifica la carpeta es
el contenedor que contiene mongodb

Mongo-express solo es un cliente mas de mongodb que le sirvio al equipo de desarrollo para poder hacer pruebas
El contenedor que contiene la api-rest de musicool se contruye por el dockerFile del proyecto
los demás servicios estan especificados en el docker compose así como la orquestación del mismo






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