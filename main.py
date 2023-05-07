from fastapi import FastAPI, HTTPException, status
from obj.usuario import Usuario
from dao.usuariodao import UsuarioDAO

app = FastAPI()

dao = UsuarioDAO()

@app.post("/usuarios", status_code=status.HTTP_201_CREATED)
def crear_usuario(usuario: Usuario):
    resultado = dao.crearUsuario(usuario)
    if resultado == 0:
        return {"mensaje": f"Usuario creado: {usuario.username}"}
    elif resultado == -1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El usuario ya existe en la base de datos")
    else:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Error al crear el usuario")

@app.get("/usuarios/{username}", status_code=status.HTTP_200_OK)
def obtener_usuario(username: str):
    usuario = dao.obtenerUsuario(username)
    if usuario:
        return usuario.dict()
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no encontrado en la base de datos")

@app.put("/usuarios/{username}", status_code=status.HTTP_200_OK)
def actualizar_usuario(username: str, campos: dict):
    resultado = dao.actualizarUsuario(username, campos)
    if resultado:
        return {"mensaje": f"Usuario actualizado: {username}"}
    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al actualizar el usuario") 


@app.delete("/usuarios/{username}", status_code=status.HTTP_200_OK)
def eliminar_usuario(username: str):
    resultado = dao.eliminarUsuario(username)
    if resultado:
        return {"mensaje": f"Usuario eliminado: {username}"}
    else:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al eliminar el usuario")
