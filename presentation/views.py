from flask import Blueprint, render_template, jsonify, request, redirect, url_for, current_app,session
from controller.user_controller import registrar_usuario, obtener_historial_comidas
from controller.login_controller import login_usuario

views_bp = Blueprint('views', __name__)

@views_bp.route('/')
def home():
    return render_template('home.html')

@views_bp.route('/index')
def index():
    usuario=session['usuario']
    return render_template('index.html',usuario=usuario)

@views_bp.route('/hello/<name>')
def hello(name):
    return f"Hello {name}!"

@views_bp.route('/login',methods=['GET','POST'])
def login ():
    if request.method=='POST':
        email=request.form['email']
        contrasena=request.form['contrasena']
    
        try:
         login_usuario (email,contrasena)
         return redirect(url_for('views.index'))
        except ValueError as ve:
            return f"Error: {ve}"   
        except Exception as e:
            return f"Error inesperado: {e}"
    return render_template('login.html')

@views_bp.route('/register', methods=['GET', 'POST'])

def register():
    if request.method == 'POST':
        nombre = request.form['nombre']
        apellido = request.form['apellido']
        email = request.form['email']
        contrasena = request.form['contrasena']

        resultado = registrar_usuario(nombre, apellido, email, contrasena)

        if resultado['success']:
           
            return redirect(url_for('views.login'))
        else:
           
            status_code = 400 if "correo" in resultado['error'] else 500
            return render_template('register.html', error=resultado['error']), status_code

    return render_template('register.html')


@views_bp.route('/historial_comidas', methods=['GET'])
def historial_comidas():
    usuario = session['usuario']   
    try:
        user = obtener_historial_comidas(usuario["id"])
        return render_template('historial_comidas.html', usuario=user)
    except ValueError as ve:
        return render_template('historial_comidas.html', error=str(ve))

@views_bp.route('/logout',methods=['GET','POST'])
def logout():
    session.clear()
    return redirect(url_for('views.login'))