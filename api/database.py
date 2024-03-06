from sqlalchemy import create_engine
# from sqlalchemy.ext.declarative import declarative_base
# from models import Base
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os

load_dotenv()

#postgres url connection string
DATABASE_URL =  "postgresql://umhwxbhi:4XLoDGoOktCfamnIZ4KrR_oC4fhjnWSa@floppy.db.elephantsql.com/umhwxbhi"
#create a postgres engine instance
engine = create_engine(DATABASE_URL)
 #create declarative base meta instance

# Base = declarative_base()
# base = Base()
#create session local class for session maker
sessionlocal = sessionmaker(bind=engine,expire_on_commit=False)
