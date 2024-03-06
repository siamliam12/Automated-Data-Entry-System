from fastapi import FastAPI,Depends,HTTPException,status,File,UploadFile
from scripts.email_extractor import email_extractor
from scripts.image_manipulator import ImageConverter
from scripts.text_extractor import text
import schemas
import models
from models import User
import crud
from database import engine,sessionlocal
from sqlalchemy.orm import Session
import os
from typing import Optional,List

app = FastAPI()
models.Base.metadata.create_all(engine)
def get_session():
    db = sessionlocal()
    try:
        yield db
    finally:
        db.close()


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


def get_user_data(username:Optional[str]=None,db:Session=Depends(get_session))->schemas.UserSchema:
    user = crud.get_user_by_username(db,username)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user

@app.post('/users',response_model=schemas.UserSchema)
def create_user(user:schemas.UserSchema,db:Session=Depends(get_session)):
    existing_user =  db.query(models.User).filter(models.User.username==user.username).first()
    if existing_user:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="User already exists")
    db = sessionlocal()
    db_user = models.User(**user.dict())
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@app.get('/get-data')
async def get_data(db:Session=Depends(get_session)):
    data = db.query(models.Data).all()
    return {"data": data}
@app.get('/get-data/{id}')
async def get_data(id:int,db:Session=Depends(get_session)):
    data = db.query(models.Data).filter(models.Data.id == id).first()
    if data is None:
        raise HTTPException(status_code=404, detail="Item not found")
    return {"data": data}
@app.put('/update-data/{id}')
async def update_data(id:int,data:schemas.DataSchema,db:Session=Depends(get_session)):
    db_data = db.query(models.Data).filter(models.Data.id == id).first()
    if data is None:
        raise HTTPException(status_code=404, detail="Item not found")
    db_data.name = data.name
    db_data.age = data.age
    db_data.date = data.date
    db_data.complaint = data.complaint
    db_data.diagnosis = data.diagnosis
    db_data.prescription_info = data.prescription_info
    db.commit()
    return {"data": "Data has been updated successfully"}
@app.delete('/delete-data/{id}')
async def delete_data(id:int,db:Session=Depends(get_session)):
    data = db.query(models.Data).filter(models.Data.id == id).first()
    if data is None:
        raise HTTPException(status_code=404, detail="Item not found")
    db.delete(data)
    db.commit()
    return {"message": "Data has been deleted successfully"}

@app.get('/attachment-search-by-sender')
async def attachment(sender,user:schemas.UserSchema = Depends(get_user_data)):
    download_dir = user.download_dir
    search_criteria = email_extractor.search_by_sender(sender)
    attachments = email_extractor.attachment_download(search_criteria,download_dir)
    return {"Message":"Attachments has been downloaded successfully"}
    
@app.get('/attachment-search-by-date')
async def attachment(subject,start_date,end_date,user:schemas.UserSchema = Depends(get_user_data)):
    download_dir =user.download_dir 
    search_criteria = email_extractor.set_search_rules(subject,start_date,end_date)
    attachments = email_extractor.attachment_download(search_criteria,download_dir)
    return {"Message":f"Attachments has been downloaded successfully {search_criteria}"}


@app.get('/converter')
async def converter(image_type,user:schemas.UserSchema = Depends(get_user_data)):
    converter = ImageConverter()
    download_dir =user.download_dir 
    jpg = os.path.join(download_dir,"jpg")
    png = os.path.join(download_dir,"png")
    if image_type == "png":
       converter.convert_from_png(png,jpg)
    if image_type == "webp":
        webp = os.path.join(download_dir,"webp")
        converter.convert_from_webp(webp,jpg)
    if image_type == "jfif":
        jfif = os.path.join(download_dir,"jfif")
        converter.convert_from_webp(jfif,jpg)
    return {"Message":f"Image Successfully Converted from {image_type} to jpg={png}"}
# files:List[UploadFile]=File(...)
@app.post('/text-extractor')
async def text_extractor(user:schemas.UserSchema = Depends(get_user_data),db:Session=Depends(get_session)):
    download_dir = user.download_dir
    path = os.path.join(download_dir,'jpg')
    data = text.extractor(path)
    print(data)
    try:
        new_data = models.Data(name=data['name'],age=data['age'],date=data['date'],complaint=data['complaint'],diagnosis=data['diagnosis'],prescription_info=data['prescription_info'])
        db.add(new_data)
        db.commit()
        db.refresh(new_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to save data: {str(e)}")
    return {"message":f"Data has been saved successfully"}