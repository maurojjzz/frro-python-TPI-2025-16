from controller.cloudinary_service import subir_imagen_a_cloudinary

def subir_imagen_controller(file, id_usuario):
    if file.mimetype not in ['image/jpeg', 'image/png']:
        return ({"success": False, "error": "El archivo debe ser una imagen JPEG o PNG"})

    max_size_mb = 5
    if file.content_length and file.content_length > max_size_mb * 1024 * 1024:
        return {
            "success": False,
            "error": f"El archivo no debe superar los {max_size_mb} MB"
        }

    return subir_imagen_a_cloudinary(file, id_usuario)