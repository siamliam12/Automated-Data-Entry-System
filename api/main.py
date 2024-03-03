from fastapi import FastAPI,Depends,HTTPException,status
from fastapi.security import OAuth2PasswordBearer
from fastapi.security import HTTPBasicCredentials, HTTPBasic
from auth_bearer import JWTBearer
from functools import wraps
from utils import create_access_token,create_refresh_token,verify_password,get_hashed_password,verify_token
from scripts.email_extractor import email_extractor
from scripts.image_manipulator import converter
from scripts.text_extractor import text
import schemas
import models
from models import User,TokenTable
from database import Base,engine,sessionlocal
from sqlalchemy.orm import Session
import jwt
from datetime import datetime
import os
from jose import jwt,JWTError
from typing import Optional,Annotated

Base.metadata.create_all(engine)
def get_session():
    session = sessionlocal()
    try:
        yield session
    finally:
        session.close()

app = FastAPI()

ACCESS_TOKEN_EXPIRE_MINUTES = 30  # 30 minutes
REFRESH_TOKEN_EXPIRE_MINUTES = 60 * 24 * 7 # 7 days
ALGORITHM = "HS256"
JWT_SECRET_KEY = os.environ.get('JWT_SECRET_KEY')  # should be kept secret
JWT_REFRESH_SECRET_KEY = os.environ.get('JWT_REFRESH_SECRET_KEY')

@app.get('/')
async def index():
    routes = [
        {
            "data":"All routes",
            "Get Data":"/get-data",
            "Download Attachments":"/attachment",
            "Image converter":"/converter",
            "Text Extractor":"/text-extractor",
        }
    ]
    return {"message":routes}


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
    token_db = models.TokenTable(user_id=user.id,access_token=access,refresh_token=refresh, status=True)
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

def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return schemas.UserInDB(**user_dict)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Verify token function
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = schemas.TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(models.User, username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)]
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user

@app.get('/get-data')
async def get_data():
    pass
# current_user: Annotated[User, Depends(get_current_active_user)], token: str = Depends(oauth2_scheme)
@app.get('/attachment-search-by-sender')
async def attachment(sender,dependencies=Depends(JWTBearer()),current_user:User=Depends(get_current_user)):
    download_dir = current_user.download_dir
    search_criteria = email_extractor.search_by_sender(sender)
    attachments = email_extractor.attachment_download(search_criteria,download_dir)
    return {"Message":"Attachments has been downloaded successfully"}
    
@app.get('/attachment-search-by-date')
async def attachment(subject,start_date,end_date,download_dir):
    search_criteria = email_extractor.set_search_rules(subject,start_date,end_date)
    attachments = email_extractor.attachment_download(search_criteria,download_dir)
    return {"Message":"Attachments has been downloaded successfully"}


@app.get('/converter')
async def converter():
   pass

@app.get('/text-extractor')
async def text_extractor():
    pass