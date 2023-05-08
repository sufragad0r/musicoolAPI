from fastapi import FastAPI, HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from obj.usuario import Usuario
from obj.token import Token, TokenData
from dao.usuariodao import UsuarioDAO

app = FastAPI()

dao = UsuarioDAO()

SECRET_KEY = "b9283fe52786894f37fd73b300fd8abcdaadb03d930c108808431c9f84f4cf8a"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verificarPassword(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def obtener_password_hash(password):
    return pwd_context.hash(password)

def autenticarUsuario(username: str, password: str):
    user = dao.obtenerUsuario(username)
    if not user:
        return False
    if not verificarPassword(password, user.password):
        return False
    return user

def crearToken(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def obtenerUsuarioToken(token: str = Depends(oauth2_scheme)):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalido")
        token_data = TokenData(username=username)
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token invalido")
    user = dao.obtenerUsuario(token_data.username)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario no encontrado")
    return user

@app.post("/token", 
          response_model=Token, 
          summary="Obtener token de acceso", 
          tags=["Autenticación"])
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    """
    Obtener un token de acceso para el usuario autenticado.

    **Parámetros:**
    - `form_data`: objeto OAuth2PasswordRequestForm: formulario de solicitud de contraseña con los siguientes campos:
        - `username` (str): nombre de usuario.
        - `password` (str): contraseña del usuario.

    **Retorna:**
    - Token: token de acceso generado, con los siguientes campos:
        - access_token (str): token de acceso.
        - token_type (str): tipo de token (en este caso, "bearer").

    **Excepciones:**
    - HTTPException(status_code=401, detail="Usuario o contraseña incorrectos"): si el usuario no existe o la contraseña es incorrecta.
    """
    user = autenticarUsuario(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario o contraseña incorrectos")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = crearToken(data={"sub": user.username}, expires_delta=access_token_expires)
    return {"access_token": access_token, "token_type": "bearer"}

@app.post("/usuarios", 
          status_code=status.HTTP_201_CREATED, 
          summary="Crear usuario", 
          tags=["Usuarios"])
def crear_usuario(usuario: Usuario):
    """
    Crea un nuevo usuario en la base de datos.

    **Parámetros**:
    `usuario`: Un objeto `Usuario` con la información del nuevo usuario.

    **Retorna**: 
    - Un mensaje que indica si el usuario fue creado exitosamente.

    **Excepciones**: 
    - HTTPException: si el usuario ya existe en la base de datos o si hay un error al crearlo.
    """
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
async def obtener_usuario(username: str, current_user: Usuario = Depends(obtenerUsuarioToken)):
    """
    Obtiene la información del usuario especificado.

    - `username`: Nombre de usuario del usuario a buscar.
    - `current_user`: Usuario autenticado (se obtiene del token en la petición).
    """
    usuario = dao.obtenerUsuario(username)
    if usuario is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El usuario no se encuentra en la base de datos")
    return usuario

@app.put("/usuarios/{username}", 
         status_code=status.HTTP_200_OK,
         summary="Actualizar usuario",
         tags=["Usuarios"])
async def actualizar_usuario(username: str, usuario: Usuario, current_user: Usuario = Depends(obtenerUsuarioToken)):
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
    if current_user.username != username:
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
            summary="Actualizar usuario",
            tags=["Usuarios"])
async def eliminar_usuario(username: str, current_user: Usuario = Depends(obtenerUsuarioToken)):
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
    if current_user.username != username:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No está autorizado para eliminar este usuario")
    resultado = dao.eliminarUsuario(username)
    if resultado == 0:
        return {"mensaje": f"Usuario eliminado: {username}"}
    elif resultado == -1:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El usuario no se encuentra en la base de datos")
    else:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="Error al eliminar el usuario")