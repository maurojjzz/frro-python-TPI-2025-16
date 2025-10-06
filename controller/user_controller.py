from data.models import Usuario
from data.repositories.user_repository import insertar_usuario
from data.repositories.user_repository import validoMailUser
from data.repositories.user_repository import getComidaUsuario

from werkzeug.security import generate_password_hash

def registrar_usuario(nombre, apellido, email, contrasena):

    # Validaciones de campos vacíos
    if not nombre or not apellido or not email or not contrasena:
        return {"success": False, "error": "Todos los campos son obligatorios"}

    # Validación de formato de email
    import re
    email_regex = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    if not re.match(email_regex, email):
        return {"success": False, "error": "El formato del correo es inválido"}

    # Validación de longitud de contraseña
    if len(contrasena) < 6:
        return {"success": False, "error": "La contraseña debe tener al menos 6 caracteres"}

    # Validación de email duplicado
    if validoMailUser(email):
        return {"success": False, "error": "El correo ya está registrado"}

    nuevo_usuario = Usuario(
        nombre=nombre,
        apellido=apellido,
        email=email,
        contrasena=generate_password_hash(contrasena)
    )
    try:
        usuario_creado = insertar_usuario(nuevo_usuario)
        return {"success": True, "usuario": usuario_creado}
    except Exception as e:
        return {"success": False, "error": f"Error interno al crear el usuario: {str(e)}"}


def obtener_historial_comidas(id_usuario):
    user = getComidaUsuario(id_usuario)
    if not user:
        raise ValueError("Usuario no encontrado o sin comidas registradas")
    return user
