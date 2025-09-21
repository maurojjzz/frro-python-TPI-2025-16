from flask import Blueprint, render_template, jsonify, request, redirect, url_for, current_app,session
from controller.user_controller import registrar_usuario
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

        try:
            registrar_usuario(nombre, apellido, email, contrasena)
            
            return redirect(url_for('views.login'))
        except ValueError as ve:
            return f"Error: {ve}"   
        except Exception as e:
            return f"Error inesperado: {e}"
    return render_template('register.html')