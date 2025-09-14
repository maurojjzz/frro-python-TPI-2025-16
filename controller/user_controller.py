from data.models import Usuario
from data.database import SessionLocal

from werkzeug.security import generate_password_hash

def registrar_usuario(nombre, apellido, email, contrasena):
    db = SessionLocal()
    try:
      
        contrasena_hash = generate_password_hash(contrasena)

   
        nuevo_usuario = Usuario(
            nombre=nombre,
            apellido=apellido,
            email=email,
            contrasena=contrasena_hash
        )

  
        db.add(nuevo_usuario)
        db.commit()
        db.refresh(nuevo_usuario)  
        return nuevo_usuario
    except Exception as e:
        db.rollback()  
        raise e
    finally:
        db.close()
