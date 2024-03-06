from sqlalchemy import Column,Integer,String,DateTime,Boolean
# from database import Base
import datetime
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    pass

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True,index=True)
    username = Column(String,unique=True,index=True)
    download_dir = Column(String)

class Data(Base):
    __tablename__ = "data"
    id = Column(Integer, primary_key=True,index=True)
    name = Column(String)
    age = Column(Integer)
    date = Column(String)
    complaint = Column(String)
    diagnosis = Column(String)
    prescription_info = Column(String)