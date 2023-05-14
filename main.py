from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, HTTPBasicCredentials, HTTPBasic
from datetime import datetime, timedelta
from jose import JWTError, jwt
from obj.usuario import Usuario
from obj.otp import OTP
from obj.token import Token, TokenData
from obj.autorizacionotp import autorizacionOTP
from dao.usuariodao import UsuarioDAO
from dao.otpdao import OTPDAO
from sec.sec import verificarPassword, obtener_password_hash, autenticarUsuario, crearToken, obtenerUsuarioToken,ACCESS_TOKEN_EXPIRE_MINUTES, validar_credenciales
from auth2.sms import generarCodigoOTP, SMS

app = FastAPI(title="Musicool", version="ALPHA")

security = HTTPBasic()



dao = UsuarioDAO()

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
        - `True` : Solicitar otp con un limite de 3 minutos
    **Excepciones:**
    - HTTPException(status_code=401, detail="Usuario o contraseña incorrectos"): si el usuario no existe o la contraseña es incorrecta.
    """
    user = autenticarUsuario(username=form_data.username, password=form_data.password, dao=dao)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario o contraseña incorrectos")
    
    otpDAO = OTPDAO()
    otpUsuario = OTP(username=form_data.username, codigo=generarCodigoOTP(), expiracion=(datetime.now() + timedelta(minutes=5)))
        
    if otpDAO.crearUsuarioOTP(otpUsuario):
        smsOTP = SMS()
        smsOTP.mandarMensajeOTP(codigoOTP = otpUsuario.codigo, numeroDestino=user.telefono)
        
        return {"solicitarOTP" : True,
                "info": "OK."}
    
    return {"solicitarOTP" : False,
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

    **Excepciones:**
    - HTTPException(status_code=401, detail="Usuario o contraseña incorrectos"): si el usuario no existe o la contraseña es incorrecta.
    """
    if not OTPDAO().autenticarOTP(username=form_data.username, otp= form_data.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Codigo invalido")
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = crearToken(data={"sub": form_data.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}
    
    
@app.post("/usuarios", 
          status_code=status.HTTP_201_CREATED, 
          summary="Crear usuario", 
          tags=["Usuarios"])
def crear_usuario(usuario: Usuario, credentials: HTTPBasicCredentials = Depends(security)):
    """
    Crea un nuevo usuario en la base de datos.

    **Parámetros**:
    `usuario`: Un objeto `Usuario` con la información del nuevo usuario.

    **Retorna**: 
    - Un mensaje que indica si el usuario fue creado exitosamente.

    **Excepciones**: 
    - HTTPException: si el usuario ya existe en la base de datos o si hay un error al crearlo.
    """
    if not validar_credenciales(credentials):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Este cliente no esta autorizado para utilizar la api")
    hashed_password = obtener_password_hash(usuario.password)
    usuario.password = hashed_password
    resultado = dao.crearUsuario(usuario)
    if resultado == 0:
        return {"mensaje": f"Usuario creado: {usuario.username}"}
    elif resultado == -1:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El usuario ya existe en la base de datos")
    else:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Error al crear el usuario")
    
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
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Este cliente no esta autorizado para utilizar la api")
    usuario = dao.obtenerUsuario(username)
    if usuario is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El usuario no se encuentra en la base de datos")
    return usuario

@app.put("/usuarios/{username}", 
         status_code=status.HTTP_200_OK,
         summary="Actualizar usuario",
         tags=["Usuarios"])
async def actualizar_usuario(username: str, usuario: Usuario, current_user: Usuario = Depends(obtenerUsuarioToken), credentials: HTTPBasicCredentials = Depends(security)):
    """
    Actualiza un usuario existente en la base de datos.

    **Parámetros**:
    - `username`: nombre de usuario del usuario a actualizar (path)
    - `usuario`: información del usuario a actualizar (body)
    - `current_user`: usuario autenticado actualmente

    **Retorna**:
    - Mensaje de éxito si se actualizó correctamente

    **Excepciones**:
    - HTTP 401: si el usuario autenticado no tiene permisos para actualizar este usuario
    - HTTP 404: si el usuario a actualizar no se encuentra en la base de datos
    - HTTP 503: si hay un error al actualizar el usuario
    """
    if current_user.username != username and not validar_credenciales(credentials):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No está autorizado para actualizar este usuario")
    hashed_password = obtener_password_hash(usuario.password)
    usuario.password = hashed_password
    resultado = dao.actualizarUsuario(username, dict(usuario))
    if resultado == 0:
        return {"mensaje": f"Usuario actualizado: {usuario.username}"}
    elif resultado == -1:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El usuario no se encuentra en la base de datos")
    else:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Error al actualizar el usuario")

@app.delete("/usuarios/{username}", 
            status_code=status.HTTP_200_OK,
            summary="Eliminar usuario",
            tags=["Usuarios"])
async def eliminar_usuario(username: str, current_user: Usuario = Depends(obtenerUsuarioToken), credentials: HTTPBasicCredentials = Depends(security)):
    """
    Elimina un usuario existente en la base de datos.

    **Parámetros**:
    - `username` (str): Nombre de usuario a eliminar.
    - `current_user` (Usuario, opcional): Usuario autenticado actualmente. Se obtiene mediante el token de autenticación.

    **Retorna**:
    - dict: Diccionario que contiene el mensaje de éxito en caso de que se elimine el usuario.

    **Excepciones**:
    - HTTPException: Si el usuario actualmente autenticado no tiene permiso para eliminar el usuario.
    - HTTPException: Si no se puede encontrar el usuario especificado en la base de datos.
    - HTTPException: Si se produce un error al eliminar el usuario.
    """
    if current_user.username != username and not validar_credenciales(credentials):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    if current_user.username != username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No está autorizado para eliminar este usuario")
    resultado = dao.eliminarUsuario(username)
    if resultado == 0:
        return {"mensaje": f"Usuario eliminado: {username}"}
    elif resultado == -1:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El usuario no se encuentra en la base de datos")
    else:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Error al eliminar el usuario")