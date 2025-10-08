from data.models import Usuario
from data.database import SessionLocal
from werkzeug.security import check_password_hash

def loguearUsuario (email):
    db=SessionLocal()

    try:
        return   db.query(Usuario).filter(Usuario.email == email).first()
       

    finally:
        db.close()