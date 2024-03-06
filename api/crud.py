from sqlalchemy.orm  import Session
import models,schemas

def get_user_by_username(db:Session,username:str)->schemas.UserSchema:
    return db.query(models.User).filter(models.User.username==username).first()

def create_data(db:Session,data:dict):
    try:
        new_data = models.Data(name=data.name,age=data.age,date=data.date,complaint=data.complaint,diagnosis=data.diagnosis,prescription_info=data.prescription_info)
        db.add(new_data)
        db.commit()
        db.refresh(new_data)
        return new_data
    except Exception as e:
        db.rollback()
        raise e