from pydantic import BaseModel
import datetime

class UserCreationModel(BaseModel):
    Username : str
    email : str
    password : str
    download_dir: str

class requestdetails(BaseModel):
    email : str
    password : str

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
    username: str | None = None

class UserInDB(UserCreationModel):
    hashed_password: str