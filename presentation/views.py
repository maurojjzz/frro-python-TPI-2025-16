from flask import Blueprint, render_template, jsonify, request
import os
from dotenv import load_dotenv
from controller.imagen import subir_imagen_controller

views_bp = Blueprint('views', __name__)

load_dotenv()

@views_bp.route('/')
def index():
    api_url= os.getenv('API_URL')
    return render_template('index.html', api_url=api_url)


@views_bp.route('/hello/<name>')
def hello(name):
    return f"Hello {name}!"


@views_bp.route('/subir-imagen', methods=['POST'])
def subir_imagen():    
    if 'imagen' not in request.files:
        return jsonify({"success": False, "error": "No se ha proporcionado ninguna imagen"}), 400
    
    file = request.files['imagen']
    
    id_usuario = 1  # es temporal dsp lo sacamos del token si esta loguedo
    
    resultado_subida = subir_imagen_controller(file, id_usuario)
    
    if resultado_subida['success']:
        return jsonify({
            "success": True,
            "url": resultado_subida['url'],
            "public_id": resultado_subida['public_id'],
            "message": resultado_subida['message']
        }), 200
    else:
        return jsonify({
            "success": False,
            "error": resultado_subida['error']
        }), 500

