import os.path
from typing import Optional
from fastapi import FastAPI, HTTPException, status, Depends, Header, File, UploadFile
from fastapi.security import OAuth2PasswordRequestForm, HTTPBasicCredentials, HTTPBasic
from datetime import datetime, timedelta
from obj.usuario import Usuario
from obj.artista import Artista
from obj.otp import OTP
from obj.token import Token
from obj.cancion import Cancion, CancionBytes
from obj.autorizacionotp import autorizacionOTP
from dao.usuariodao import UsuarioDAO
from dao.artistadao import ArtistaDAO
from dao.otpdao import OTPDAO
from dao.canciondao import CancionDAO
from sec.sec import obtener_password_hash, autenticar_usuario, crear_token, ACCESS_TOKEN_EXPIRE_MINUTES, \
    validar_credenciales, originesPerimitidos, validar_token, obtener_username
from auth2.sms import generarCodigoOTP, SMS
from fastapi.middleware.cors import CORSMiddleware
from fm.fmanager import FManager
from fastapi.responses import FileResponse

app = FastAPI(title="Musicool", version="ALPHA")

security = HTTPBasic()

app.add_middleware(
    CORSMiddleware,
    allow_origins=originesPerimitidos,
)


@app.post("/login",
          response_model=autorizacionOTP,
          summary="Login para el sistema",
          tags=["Login"])
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Verificar login del usuario

    **Parámetros:**
    - `form_data`: objeto OAuth2PasswordRequestForm: formulario de solicitud de contraseña con los siguientes campos:
        - `username` (str): nombre de usuario.
        - `password` (str): contraseña del usuario.

    **Retorna:**
    - solicitarOTP:
        - `False` : Error al autenticar usuario
        - `True` : Envia codigo otp con una expiracion de 5 minutos
    
    **Excepciones:**
    - HTTPException(status_code=401, detail="Usuario o contraseña incorrectos"): si el usuario no existe o la contraseña es incorrecta.
    """
    usuario = autenticar_usuario(username=form_data.username, password=form_data.password)
    if not usuario:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario o contraseña incorrectos")

    otpDAO = OTPDAO()
    otpUsuario = OTP(username=form_data.username, codigo=generarCodigoOTP(),
                     expiracion=(datetime.now() + timedelta(minutes=5)))

    if otpDAO.crear_usuarioOTP(otpUsuario):
        smsOTP = SMS()
        smsOTP.mandar_mensajeOTP(codigoOTP=otpUsuario.codigo, numeroDestino=usuario.telefono)

        return {"solicitarOTP": True,
                "info": "OK."}

    return {"solicitarOTP": False,
            "info": "Error al solicitar la autorizacion OTP"}


@app.post("/login/auth",
          response_model=Token,
          summary="Validacion OTP para obtener un token de autentificacion",
          tags=["Login"])
async def login_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Obtener un token de acceso para el usuario autenticado.

    **Parámetros:**
    - `form_data`: objeto OAuth2PasswordRequestForm: formulario de solicitud de contraseña con los siguientes campos:
        - `username` (str): nombre de usuario.
        - `password` (str): codigo OTP del usuario.

    **Retorna:**
    - Token: token de acceso generado, con los siguientes campos:
        - access_token (str): token de acceso.
        - token_type (str): tipo de token (en este caso, "bearer").
        - rol (str): rol del usuario (artista, escucha)

    **Excepciones:**
    - HTTPException(status_code=401, detail="Usuario o contraseña incorrectos"): si el usuario no existe o la contraseña es incorrecta.
    """
    if not OTPDAO().autenticar_OTP(username=form_data.username, otp=form_data.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Codigo invalido")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = crear_token(data={"sub": form_data.username}, expires_delta=access_token_expires)
    dao = UsuarioDAO()
    usuario = dao.obtener_usuario(form_data.username)
    return {"access_token": access_token, "token_type": "bearer", "rol": usuario.rol}


@app.post("/usuarios",
          status_code=status.HTTP_201_CREATED,
          summary="Crear usuario",
          tags=["Usuarios"])
def crear_usuario(usuario: Usuario, credentials: HTTPBasicCredentials = Depends(security)):
    """
    Crea un nuevo usuario en la BD.

    **Parámetros**:
    `usuario`: Un objeto `Usuario` con la información del nuevo usuario.

    **Retorna**: 
    - Un mensaje que indica si el usuario fue creado exitosamente.

    **Excepciones**: 
    - HTTPException: Si el usuario ya existe en la base de datos o si hay un error al crearlo.
    """
    dao = UsuarioDAO()

    if not validar_credenciales(credentials):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Cliente no autorizado")

    hashed_password = obtener_password_hash(usuario.password)
    usuario.password = hashed_password

    resultado = dao.crear_usuario(usuario)
    if resultado == 0:
        return {"mensaje": f"Usuario creado: {usuario.username}"}
    elif resultado == -1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Usuario existente en la BD")
    else:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Error al crear usuario")


@app.get("/usuarios/{username}",
         status_code=status.HTTP_200_OK,
         response_model=Usuario,
         summary="Obtener usuario",
         tags=["Usuarios"])
async def obtener_usuario(username: str, credentials: HTTPBasicCredentials = Depends(security)):
    """
    Obtiene la información del usuario especificado.

    - `username`: Nombre de usuario del usuario a buscar.
    - `current_user`: Usuario autenticado (se obtiene del token en la petición).
    """
    if not validar_credenciales(credentials):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Cliente no autorizado")

    dao = UsuarioDAO()
    usuario = dao.obtener_usuario(username)

    if usuario is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no existente")

    return usuario


@app.put("/usuarios/actualizar",
         status_code=status.HTTP_200_OK,
         summary="Actualizar usuario",
         tags=["Usuarios"])
async def actualizar_usuario(usuarioActualizado: Usuario, token: Optional[str] = Header(None)):
    """
    Actualiza un usuario existente en la base de datos.

    **Parámetros**:
    - `usuarioActualizado`: Usuario con sus respectivos datos actualizados
    - `token`: Token de autenticacion del usuario a actualizarse

    **Retorna**:
    - Mensaje de éxito si se actualizó correctamente

    **Excepciones**:
    - HTTP 401: si el usuario autenticado no tiene permisos para actualizar este usuario
    - HTTP 404: si el usuario a actualizar no se encuentra en la base de datos
    - HTTP 503: si hay un error al actualizar el usuario
    """
    if token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token no autorizado")

    if not validar_token(token):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalido")

    dao = UsuarioDAO()
    usernameToken = obtener_username(token)

    if usuarioActualizado.username != usernameToken:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="No está autorizado para actualizar este usuario")

    hashed_password = obtener_password_hash(usuarioActualizado.password)
    usuarioActualizado.password = hashed_password
    resultado = dao.actualizar_usuario(usuarioActualizado.username, dict(usuarioActualizado))

    if resultado == 0:
        return {"mensaje": f"Usuario actualizado: {usuarioActualizado.username}"}
    elif resultado == -1:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario inexistente")
    else:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Error al actualizar el usuario")


@app.delete("/usuarios/eliminar",
            status_code=status.HTTP_200_OK,
            summary="Eliminar usuario",
            tags=["Usuarios"])
async def eliminar_usuario(username: str, token: Optional[str] = Header(None)):
    """
    Eliminar el usuario autenticado de la BD.

    **Parámetros**:
    - `username` (str): Nombre del usuario autenticado.
    - `token` (str): Token del usuario autenticado

    **Retorna**:
    - Mensaje de éxito en caso de que se elimine el usuario.

    **Excepciones**:
    - HTTPException: Si el usuario actualmente autenticado no tiene permiso para eliminar el usuario.
    - HTTPException: Si no se puede encontrar el usuario especificado en la base de datos.
    - HTTPException: Si se produce un error al eliminar el usuario.
    """
    if token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token no autorizado")

    if not validar_token(token):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalido")

    dao = UsuarioDAO()
    usernameToken = obtener_username(token)

    if usernameToken != username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail="No está autorizado para eliminar este usuario")

    resultado = dao.eliminar_usuario(username)

    if resultado == 0:
        return {"mensaje": f"Usuario eliminado: {username}"}
    elif resultado == -1:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuario no existente")
    else:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Error al eliminar el usuario")


@app.post("/artistas",
          status_code=status.HTTP_201_CREATED,
          summary="Crear artista",
          tags=["Artistas"])
def crear_artista(usuario: Artista, token: Optional[str] = Header(None)):
    """
    Crea un nuevo artista en la base de datos.

    **Parámetros**:
    `usuario`: Un objeto `Artista` con la información del nuevo artista.

    **Retorna**: 
    - Un mensaje que indica si el artista fue creado exitosamente.

    **Excepciones**: 
    - HTTPException: si el artista ya existe en la base de datos o si hay un error al crearlo.
    """
    daoArtista = ArtistaDAO()
    daoUsuario = UsuarioDAO()

    if token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token no autorizado")

    if not validar_token(token):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token no autorizado")

    if obtener_username(token) != usuario.username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no autorizado")

    if daoUsuario.obtener_usuario(usuario.username).rol == "artista":
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Usuario ya es un artista")

    if daoUsuario.actualizar_usuario(usuario.username, {"rol": "artista"}) != 0:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Usuario no pudo actualizar su rol")

    resultado = daoArtista.crear_artista(usuario)
    if resultado == 0:
        return {"mensaje": f"Artista creado: {usuario.username}"}
    elif resultado == -1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El artista ya existe en la base de datos")
    else:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Error al crear el artista")


@app.post("/subir-cancion",
          status_code=status.HTTP_200_OK,
          summary="Subir cancion a la biblioteca",
          tags=["Canciones"])
async def subir_cancion(image: UploadFile = File(...), song: UploadFile = File(...), cancion_id: str = 'dafault'):
    """
    Guarda la cancion y la imagen en archivo en el servidor.

    **Parámetros**:
    - `image`: Una imagen solo aceptamos jpg.
    - `song`: Una canción solo aceptamos mp4.
    - `cancion_id`: este id debe ser unico para cada canción e imagen en caso de que se le pase uno repetido se sobreescribira el archivo

    **Retorna**:
    - Un mensaje que indica si la cancion y la imagen fue guardado con  exito.

    **Excepciones**:
    - HTTPException: si los formatos son invalidos.
    """
    if image.content_type != 'image/jpeg':
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                            detail="Solo se pueden guardar imagenes jpg al sistema")
    if song.content_type != 'audio/mpeg':
        raise HTTPException(status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                            detail="Solo se pueden guardar canciones mp4 al sistema")
    try:
        manager = FManager()
        await manager.guardar_imagen(image, cancion_id)
        await manager.guardar_cancion(song, cancion_id)
        return {"mensaje": f"La cancion: {song.filename} la imagen {image.filename}  se han guardado con exito"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error del servidor")


@app.post("/registrar-cancion",
          status_code=status.HTTP_201_CREATED,
          summary="Registar cancion en la base de datos",
          tags=["Canciones"])
def registrar_cancion(cancion: Cancion, token: Optional[str] = Header(None)):
    """
    Crea un nueva cancion en la base de datos.

    **Parámetros**:
    - `cancion`: Un objeto Cancion con la información de la nueva cancion.
    - `token`: Un token de autentificacion barrer

    **Retorna**:
    - Un id unico de la cancion para poder guardarlo en la ruta subir-cancion.

    **Excepciones**:
    - HTTPException: si el token de usuario artista no es valido.
    """

    daoCancion = CancionDAO()
    if token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token no autorizado")
    if not validar_token(token):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token no autorizado")

    resultado = daoCancion.crear_cancion(cancion)
    if resultado != None:
        return {f"{resultado}"}
    elif resultado == -1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error al guradar la cancion")
    raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Registro duplicado")


@app.get("/obtener-cancion",
          status_code=status.HTTP_200_OK,
          summary="Obtiene la cancion que coincida con el id",
          tags=["Canciones"]
          )
async def obtener_cancion(id: str, token: Optional[str] = Header(None)):
    """
       Obtiene la canción de la biblioteca de musicool.

       **Parámetros**:
       - `id`: Id unico de la canción se puede obtener en los metodos de busqueda.
       - `token`: Un token de autentificacion barrer

       **Retorna**:
       - La canción.

       **Excepciones**:
       - HTTPException: si no se encuentra un archivo con el id especificado.
       """
    if token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token no autorizado")
    if not validar_token(token):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token no autorizado")
    ruta_cancion = 'Biblioteca/'+id+'.mp4'
    if os.path.exists(ruta_cancion):
        return FileResponse(ruta_cancion, media_type="audio/mpeg")
    raise HTTPException(status_code=404, detail="Archivo no encontrado")


@app.get("/obtener-imagen",
          status_code=status.HTTP_200_OK,
          summary="Obtiene la imagen que coincida con el id",
          tags=["Canciones"]
          )
async def obtener_imagen(id: str, token: Optional[str] = Header(None)):
    """
           Obtiene la imagen de la biblioteca de musicool.

           **Parámetros**:
           - `id`: Id unico de la canción se puede obtener en los metodos de busqueda.
           - `token`: Un token de autentificacion barrer

           **Retorna**:
           - La imagen de la canción.

           **Excepciones**:
           - HTTPException: si no se encuentra un archivo con el id especificado.
           """
    if token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token no autorizado")
    if not validar_token(token):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token no autorizado")
    ruta_cancion = 'Biblioteca/'+id+'.jpg'
    if os.path.exists(ruta_cancion):
        return FileResponse(ruta_cancion, media_type="image/jpeg")
    raise HTTPException(status_code=404, detail="Archivo no encontrado")

@app.post("/buscar-cancion",
          status_code=status.HTTP_200_OK,
          summary="Retorna el id unico de las canciones para poder buscar la cancion y la imagen",
          tags=["Canciones"])
async def buscar_cancion(cancion: Cancion, token: Optional[str] = Header(None)):
    """
           Obtiene la imagen de la base de datos de musicool.

           **Parámetros**:
           - `Cancion`: Con los criterios de busqueda primero nombre de la cancion y despues artista.
           - `token`: Un token de autentificacion barrer

           **Retorna**:
           - La imagen de la canción.

           **Excepciones**:
           - HTTPException: si no se encuentra un archivo con el id especificado.
           """
    if token is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token no autorizado")
    if not validar_token(token):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token no autorizado")
    cancinDao = CancionDAO()
    idCancion = cancinDao.buscar_cancion(cancion)
    return idCancion
