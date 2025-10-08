from sqlalchemy.orm import joinedload
from data.models import Usuario

from data.database import SessionLocal


def insertar_usuario(usuario: Usuario):
    db = SessionLocal()
    try:
        db.add(usuario)
        db.commit()
        db.refresh(usuario)
        return usuario
    except Exception as e:
        db.rollback()
        raise Exception(f"No se pudo insertar el usuario: {str(e)}")
    finally:
        db.close()


def validoMailUser(email):
    db = SessionLocal()
    try:
        if not email or not isinstance(email, str):
            return None
        email = email.strip().lower()
        usuario = db.query(Usuario).filter(Usuario.email == email).first()
        return usuario
    except Exception as e:
        import logging
        logging.error(f"Error al validar email de usuario: {e}")
        return None
    finally:
        db.close()

def getComidaUsuario(idUser):
    db = SessionLocal()
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