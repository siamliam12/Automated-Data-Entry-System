from auth_bearer import JWTBearer
from functools import wraps
from fastapi.security import OAuth2PasswordBearer,OAuth2PasswordRequestForm
@app.post('/register')
def register_user(user:schemas.UserCreationModel,session:Session=Depends(get_session)):
    existing_user = session.query(models.User).filter_by(email=user.email).first()
    if existing_user:
        raise HTTPException(status_code=400,detail="Email already registered")
    encrypted_password = get_hashed_password(user.password)
    new_user = models.User(Username=user.Username,email=user.email,download_dir=user.download_dir,password=encrypted_password)
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return {"message":f"New user {user.Username} added successfully"}
@app.post('/login')
def login(request:schemas.requestdetails,db:Session=Depends(get_session)):
    user = db.query(User).filter(User.email == request.email).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Invalid Credentials")
    hashed_pass = user.password
    if not verify_password(request.password,hashed_pass):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Invalid Credentials")
    access = create_access_token(user.id)
    refresh = create_refresh_token(user.id)
    token_db = models.TokenTable(user_id=user.id,email=user.email,download_dir=user.download_dir,access_token=access,refresh_token=refresh, status=True)
    db.add(token_db)
    db.commit()
    db.refresh(token_db)
    return {
        "access_token":access,
        "refresh_token":refresh
    }
@app.post('/logout')
def logout(dependencies=Depends(JWTBearer()), db: Session = Depends(get_session)):
    token=dependencies
    payload = jwt.decode(token, JWT_SECRET_KEY, ALGORITHM)
    user_id = payload['sub']
    token_record = db.query(models.TokenTable).all()
    info=[]
    for record in token_record :
        print("record",record)
        if (datetime.utcnow() - record.created_date).days >1:
            info.append(record.user_id)
    if info:
        existing_token = db.query(models.TokenTable).where(TokenTable.user_id.in_(info)).delete()
        db.commit()
    existing_token = db.query(models.TokenTable).filter(models.TokenTable.user_id == user_id, models.TokenTable.access_toke==token).first()
    if existing_token:
        existing_token.status=False
        db.add(existing_token)
        db.commit()
        db.refresh(existing_token)
    return {"message":"Logout Successfully"} 
@app.get('/getusers')
def getusers( dependencies=Depends(JWTBearer()),session: Session = Depends(get_session)):
    user = session.query(models.User).all()
    return user
@app.post('/change-password')
def change_password(request: schemas.ChangePassword, db: Session = Depends(get_session)):
    user = db.query(models.User).filter(models.User.email==request.email).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Invalid Credentials")
    if not verify_password(request.old_password,user.password):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Invalid old Password")
    cencrypted_password = get_hashed_password(request.new_password)
    user.password = cencrypted_password
    db.commit()
    return {"message": "Password changed successfully"}
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")
def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return schemas.UserInDB(**user_dict)
def authenticate_user(db, username, password):
    user = get_user(db, username)
    if not user:
        return False
    if not verify_password(password,user.hashed_password):
        return False
    return user 
# Verify token function
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)],db: Session = Depends(get_session)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        Username: str = payload.get("sub")
        email: str = payload.get("email","")
        download_dir: str = payload.get("download_dir","")
        if Username is None:
            raise credentials_exception
        token_data = schemas.TokenData(Username=Username,email=email, download_dir=download_dir)
    except JWTError:
        raise credentials_exception
    user = get_user(db, username=token_data.Username)
    if user is None:
        raise credentials_exception
    return user
async def get_current_active_user(
    current_user: User=Depends(get_current_user)
)->User:
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user
@app.post('/token',response_model=schemas.TokenSchema,)
async def login_for_acess_token(form_data: OAuth2PasswordRequestForm = Depends(),db: Session = Depends(get_session)):
    user = authenticate_user(db,form_data.usermane,form_data.password)
    if not user:
        raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub":user.username},expires_delta=access_token_expires)
    return {"access_token":access_token,"token_type":"bearer"}
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # 30 minutes
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7 # 7 days
ALGORITHM = "HS256"
JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')  # should be kept secret
JWT_REFRESH_SECRET_KEY = os.environ.get('JWT_REFRESH_SECRET_KEY')
# current_user: Annotated[User, Depends(get_current_active_user)], token: str = Depends(oauth2_scheme)
class TokenSchema(BaseModel):
    access_token : str
    refresh_token: str
class ChangePassword(BaseModel):
    email : str
    old_password : str
    new_password : str
class TokenCreate(BaseModel):
    user_id : str
    access_token : str
    refresh_token : str
    status : bool
    created_at : datetime.datetime
class TokenData(BaseModel):
    Username: str 
    email: str
    download_dir: str
class UserInDB(UserCreationModel):
    hashed_password: str
class TokenTable(Base):
    __tablename__ = "token"
    user_id = Column(Integer)
    access_token = Column(String(450),primary_key=True)
    refresh_token = Column(String(450),nullable=False)
    status = Column(Boolean)
    created_at = Column(DateTime,default=datetime.datetime.now)
    email = Column(String,index=True)
    download_dir = Column(String,index=True)
import jwt
from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import os
from datetime import datetime
app = FastAPI()
ACCESS_TOKEN_EXPIRE_MINUTES = 30  # 30 minutes
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7  # 7 days
ALGORITHM = "HS256"
JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')  # should be kept secret
JWT_REFRESH_SECRET_KEY = os.environ.get('JWT_REFRESH_SECRET_KEY')
def decode_jwt(jwttoken: str):
    try:
        payload = jwt.decode(jwttoken, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        if payload['exp'] < datetime.utcnow().timestamp():
            return None  # Token has expired
        return payload
    except jwt.ExpiredSignatureError:
        return None  # Token has expired
    except jwt.InvalidTokenError:
        return None  # Invalid token
class JWTBearer(HTTPBearer):
    def __init__(self, auto_error: bool = True):
        super().__init__(auto_error=auto_error)

    async def __call__(self, request: Request):
        credentials: HTTPAuthorizationCredentials = await super().__call__(request)
        if credentials:
            if credentials.scheme != "Bearer":
                raise HTTPException(status_code=403, detail="Invalid Authentication Scheme")
            if not self.verify_jwt(credentials.credentials):
                raise HTTPException(status_code=403, detail="Invalid token or expired token")
            return credentials.credentials
        else:
            raise HTTPException(status_code=403, detail="Invalid Authorization Code")
    def verify_jwt(self, jwtoken: str) -> bool:
        try:
            payload = decode_jwt(jwtoken)
            return payload is not None
        except jwt.ExpiredSignatureError:
            return False
        except jwt.InvalidTokenError:
            return False
jwt_bearer = JWTBearer()
class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    Username = Column(String(50),nullable=False)
    email = Column(String(100),unique=True,nullable=False)
    password = Column(String(100),nullable=False)
    download_dir = Column(String(100),nullable=False)
class UserCreationModel(BaseModel):
    Username : str
    email : str
    password : str
    download_dir: str

class requestdetails(BaseModel):
    email : str
    password : str
import os
from passlib.context import CryptContext
from datetime import datetime,timedelta
from typing import Union,Any
from jose import jwt
from dotenv import load_dotenv

load_dotenv()

ACCESS_TOKEN_EXPIRE_MINUTES = 30  # 30 minutes
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7 # 7 days
ALGORITHM = "HS256"
JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')  # should be kept secret
JWT_REFRESH_SECRET_KEY = os.environ.get('JWT_REFRESH_SECRET_KEY')

password_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
def get_hashed_password(password:str)->str:
    return password_context.hash(password)

def verify_password(password:str,hashed_password:str)->bool:
    return password_context.verify(password,hashed_password)

def create_access_token(subject:Union[str,Any],expires_delta:int= None)->str:
    if expires_delta is not None:
        expires_delta = datetime.utcnow() + expires_delta
    else:
        expires_delta = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode = {"exp":expires_delta,"sub":str(subject)}
    encoded_jwt = jwt.encode(to_encode,JWT_SECRET_KEY,ALGORITHM)
    return encoded_jwt

def create_refresh_token(subject:Union[str,Any],expires_delta:int= None)->str:
    if expires_delta is not None:
        expires_delta = datetime.utcnow() + expires_delta
    else:
        expires_delta = datetime.utcnow() + timedelta(minutes=REFRESH_TOKEN_EXPIRE_MINUTES)
    to_encode = {"exp":expires_delta,"sub":str(subject)}
    encoded_jwt = jwt.encode(to_encode,JWT_REFRESH_SECRET_KEY,ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.JWTError:
        return None