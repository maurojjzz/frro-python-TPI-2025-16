import cloudinary
import cloudinary.uploader
import cloudinary.api
from dotenv import load_dotenv
import os

load_dotenv()

def cloudinary_configuracion():
    """Configura las credenciales de Cloudinary"""
    try:
        cloudinary.config(
            cloud_name=os.getenv('CLOUDINARY_CLOUD_NAME'),
            api_key=os.getenv('CLOUDINARY_API_KEY'),
            api_secret=os.getenv('CLOUDINARY_API_SECRET'),
            secure=True
        )
        print("Cloudinary configurado correctamente")
        return True
    except Exception as e:
        print(f"Error al configurar Cloudinary: {str(e)}")
        return False