from flask import Blueprint, render_template, jsonify, request, redirect, url_for
from controller.user_controller import registrar_usuario


views_bp = Blueprint('views', __name__)

@views_bp.route('/')
def home():
    return render_template('home.html')

@views_bp.route('/index')
def index():
    return render_template('index.html')

@views_bp.route('/hello/<name>')
def hello(name):
    return f"Hello {name}!"

@views_bp.route('/login')
def login ():
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
        except Exception as e:
            return f"Error al registrar: {e}"
    return render_template('register.html')