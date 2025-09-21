from flask import session
from data.repositories.login_repository import loguearUsuario
from werkzeug.security import check_password_hash

def login_usuario (email,contrasena):
     usuario=loguearUsuario(email)
     if not usuario:
        raise ValueError ('El mail ingresado es incorrecto')
     if not check_password_hash(usuario.contrasena,contrasena):
         raise ValueError ('La contraseña ingresado es incorrecta')
     session['usuario']={
         'id':usuario.id,
         'nombre':usuario.nombre,
         'email':usuario.email
     }
 
     return usuario
