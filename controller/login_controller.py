from flask import session
from data.repositories.login_repository import loguearUsuario
from werkzeug.security import check_password_hash
from controller.consumo_controller import ConsumoController
from datetime import datetime, date


def login_usuario(email, contrasena):
   usuario = loguearUsuario(email)
   if not usuario:
        raise ValueError('El mail ingresado es incorrecto')
   if not check_password_hash(usuario.contrasena, contrasena):
        raise ValueError('La contraseña ingresado es incorrecta')

   try:
      ConsumoController.actualizar_consumo_semanal(usuario.id)
   except Exception as e:
      print(f"Error al actualizar consumo semanal: {str(e)}")
   
   session['usuario'] = {
      'id': usuario.id,
      'nombre': usuario.nombre,
      'email': usuario.email
   }

   return usuario
