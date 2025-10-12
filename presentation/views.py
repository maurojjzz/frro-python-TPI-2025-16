from flask import Blueprint, render_template, jsonify, request, redirect, url_for, session, flash
import os
from dotenv import load_dotenv
from controller.consumo_controller import ConsumoController
from controller.imagen import subir_imagen_controller
from controller.fat_secret import reconocer_imagen, procesar_datos_fasecret
from controller.generador_titulo import extraer_nombres_de_fatsecret, generar_titulo_con_openai
from controller.comida import crear_comida
from data.repositories.comida_repository import ComidaRepository
from controller.user_controller import registrar_usuario, obtener_historial_comidas
from controller.login_controller import login_usuario

views_bp = Blueprint('views', __name__)

load_dotenv()


@views_bp.route('/')
def index():
    api_url = os.getenv('API_URL')
    usuario = session.get('usuario')
    ultimas_comidas = []
    if usuario:
        try:
            ultimas_comidas = ComidaRepository.traer_ultimas_tres_comidas(usuario['id']) or []
        except Exception:
            ultimas_comidas = []
    return render_template('index.html', api_url=api_url, usuario=usuario, ultimas_comidas=ultimas_comidas)


@views_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        contrasena = request.form['contrasena']

        try:
            login_usuario(email, contrasena)
            return redirect(url_for('views.index'))
        except ValueError as ve:
            flash(str(ve), 'error')
        except Exception as e:
            flash(f"Error inesperado: {str(e)}", 'error')
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
            flash('Usuario registrado exitosamente. Por favor, inicie sesión.', 'success')
            return redirect(url_for('views.login'))
        else:
            flash(f"Error al registrar usuario: {resultado['error']}", 'error')
            return render_template('register.html')

    return render_template('register.html')


@views_bp.route('/subir-imagen', methods=['POST'])
def subir_imagen():
    if 'imagen' not in request.files:
        return jsonify({"success": False, "error": "No se ha proporcionado ninguna imagen"}), 400

    file = request.files['imagen']

    usuario = session.get('usuario')
    if not usuario:
        return jsonify({"success": False, "error": "Usuario no autenticado"}), 401

    id_usuario = usuario['id']

    resultado_subida = subir_imagen_controller(file, id_usuario)

    if resultado_subida['success']:
        try:
            reconocimiento = reconocer_imagen(resultado_subida['url'])

            nombres_alimentos = extraer_nombres_de_fatsecret(reconocimiento)
            titulo_atractivo = generar_titulo_con_openai(nombres_alimentos)

            analisis_nutricion = procesar_datos_fasecret(reconocimiento)

            food_db = crear_comida({
                "nombre": titulo_atractivo,
                "descripcion": f"Comida reconocida: {', '.join(nombres_alimentos)}",
                "calorias": analisis_nutricion.get("calorias", 0),
                "grasas": analisis_nutricion.get("grasas", 0),
                "proteinas": analisis_nutricion.get("proteinas", 0),
                "carbohidratos": analisis_nutricion.get("carbohidratos", 0),
                "colesterol": analisis_nutricion.get("colesterol", 0),
                "imagen_url": resultado_subida['url'],
                "usuario_id": id_usuario
            })

            return jsonify({
                "success": True,
                "url": resultado_subida['url'],
                "public_id": resultado_subida['public_id'],
                "message": resultado_subida['message'],
                "titulo_atractivo": titulo_atractivo,
                "alimentos_identificadoos": nombres_alimentos,
                "reconocimiento": reconocimiento,
                "comida_id": food_db.get("comida_id")
            }), 200
        except Exception as e:
            return jsonify({
                "success": False,
                "error": f"Error al reconocer la imagen: {str(e)}"
            }), 500
    else:
        return jsonify({
            "success": False,
            "error": resultado_subida['error']
        }), 500


@views_bp.route('/historial_comidas', methods=['GET'])
def historial_comidas():
    usuario = session['usuario']
    try:
        user = obtener_historial_comidas(usuario["id"])
        return render_template('historial_comidas.html', usuario=user)
    except ValueError as ve:
        return render_template('historial_comidas.html', error=str(ve))


@views_bp.route('/logout', methods=['GET', 'POST'])
def logout():
    session.clear()
    flash('Has cerrado sesión exitosamente.', 'success')
    return redirect(url_for('views.login'))


@views_bp.route('/obtener-historial-html')
def obtener_historial_html():
    usuario = session.get('usuario')
    if not usuario:
        return jsonify({"error": "No autenticado"}), 401
    
    try:
        ultimas_comidas = ComidaRepository.traer_ultimas_tres_comidas(usuario['id']) or []
        return render_template('partials/historial_partial.html', ultimas_comidas=ultimas_comidas)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@views_bp.route('/inicializar-historial')
def inicializar_historial():
    usuario = session.get('usuario')
    if not usuario:
        return jsonify({"error": "No autenticado"}), 401
    
    try:
        # ✅ INICIALIZAR TODO EL HISTORIAL DEL USUARIO
        semanas = ConsumoController.inicializar_consumos_historicos(usuario['id'])

        print(f'✅ Historial inicializado: {len(semanas)} semanas procesadas')
        return redirect(url_for('views.index'))
        
    except Exception as e:
        print(f'❌ Error al inicializar historial: {str(e)}')
        return redirect(url_for('views.index'))