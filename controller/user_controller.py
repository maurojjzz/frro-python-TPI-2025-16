from data.models import Usuario
from data.repositories.user_repository import insertar_usuario
from data.repositories.user_repository import validoMailUser

from werkzeug.security import generate_password_hash

def registrar_usuario(nombre, apellido, email, contrasena):


    if validoMailUser(email): # si devuelve el usuario iria por el true y ejecuta el raise que me detiene la funcion (con una excepcion)con el none sigue de largo
        raise ValueError('El mail ya esta registrado')

    contrasena_hash = generate_password_hash(contrasena)

    


    nuevo_usuario = Usuario(
        nombre=nombre,
        apellido=apellido,
        email=email,
        contrasena=contrasena_hash
    )

    return insertar_usuario(nuevo_usuario)
