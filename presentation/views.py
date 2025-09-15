from flask import Blueprint, render_template, jsonify, request
from controller.cloudinary_service import subir_imagen_a_cloudinary

views_bp = Blueprint('views', __name__)


@views_bp.route('/')
def index():
    return render_template('index.html')


@views_bp.route('/hello/<name>')
def hello(name):
    return f"Hello {name}!"


@views_bp.route('/subir-imagen', methods=['POST'])
def subir_imagen():
    print("ruta subida imagenes")
    
    if 'imagen' not in request.files:
        return jsonify({"success": False, "error": "No se ha proporcionado ninguna imagen"}), 400
    
    file = request.files['imagen']
    print("Archivo recibido: ", file.filename)
    
    if file.mimetype not in ['image/jpeg', 'image/png']:
        return jsonify({"success": False, "error": "El archivo debe ser una imagen JPEG o PNG"}), 400
    
    id_usuario = 1  # es temporal dsp lo sacamos del token si esta loguedo
    
    resultado_subida = subir_imagen_a_cloudinary(file, id_usuario)
    
    if resultado_subida['success']:
        return jsonify({
            "success": True,
            "url": resultado_subida['url'],
            "public_id": resultado_subida['public_id'],
            "message": resultado_subida['message']
        })
    else:
        return jsonify({
            "success": False,
            "error": resultado_subida['error']
        }), 500

