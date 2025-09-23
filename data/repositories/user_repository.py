from sqlalchemy.orm import  joinedload
from data.models import Usuario

from data.database import SessionLocal

def insertar_usuario(usuario: Usuario):
    db = SessionLocal()
    try:
        db.add(usuario)
        db.commit()
        db.refresh(usuario)
        return usuario
    except:
        db.rollback()
        raise
    finally:
        db.close()


def validoMailUser(email):
    db=SessionLocal()
    try:
        return db.query(Usuario).filter(Usuario.email == email).first() #Devuelve un usuario si hay mail coincidente sino devuelve None
    finally:
        db.close()

def getComidaUsuario(idUser):
    db=SessionLocal()
    try:
        usuario = (
    db.query(Usuario)
    .options(joinedload(Usuario.comidas))  
    .filter(Usuario.id == idUser)
    .distinct()
    .first()
)
        return usuario
    finally:
        db.close()