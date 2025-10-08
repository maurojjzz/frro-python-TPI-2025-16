from data.cloudinary import cloudinary_configuracion
import cloudinary.uploader
from datetime import datetime

cloudinary_configuracion()


def subir_imagen_a_cloudinary(imagen, id_usuario):
    """Sube una imagen a Cloudinary y devuelve la URL"""
    try:
        timestamp = int(datetime.now().timestamp())
        public_id = f"comida_{timestamp}"
        
        resultado = cloudinary.uploader.upload(
            imagen,
            public_id=public_id,
            folder=f"mi_plato_ia/user_{id_usuario}",
            overwrite=False,
            resource_type="image",
            transformation=[{'quality': 'auto', 'fetch_format': 'auto'},
                            {'width': 800, 'height': 600, 'crop': 'limit'}
                            ]
        )
        
        if 'secure_url' in resultado:
            return {
                'success': True,
                'url': resultado['secure_url'],
                'public_id': resultado['public_id'],
                'message': "Imagen subida exitosamente"
            }
        else:
            return {
                'success': False,
                'error': "Error en la respuesta de Cloudinary"
            }
        
    except Exception as e:
        return {
            'success': False,
            'error': f"Error al subir la imagen: {str(e)}"
        }