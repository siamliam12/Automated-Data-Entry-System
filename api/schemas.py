from pydantic import BaseModel
import datetime
from typing import Optional
class UserSchema(BaseModel):
    username : str
    download_dir: str
class DataSchema(BaseModel):
    name : str
    age : int
    date:str
    complaint : str
    diagnosis :str
    prescription_info :str
