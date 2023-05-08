from datetime import timedelta, datetime
from passlib.context import CryptContext
from dao.usuariodao import UsuarioDAO
from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from obj.token import TokenData

SECRET_KEY = "b9283fe52786894f37fd73b300fd8abcdaadb03d930c108808431c9f84f4cf8a"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verificarPassword(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def obtener_password_hash(password):
    return pwd_context.hash(password)

def autenticarUsuario(username: str, password: str, dao : UsuarioDAO = UsuarioDAO()):
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

async def obtenerUsuarioToken(token: str = Depends(OAuth2PasswordBearer(tokenUrl="token"))):
    try:
        dao = UsuarioDAO()
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