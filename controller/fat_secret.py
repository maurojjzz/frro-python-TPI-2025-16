import os
import requests
import base64
from dotenv import load_dotenv

load_dotenv()

FATSECRET_CLIENT_ID = os.getenv('FATSECRET_CLIENT_ID')
FATSECRET_CLIENT_SECRET = os.getenv('FATSECRET_CLIENT_SECRET')
URL_TOKEN_ACCESS_FATSECRET = os.getenv('URL_TOKEN_ACCESS_FATSECRET')
URL_API_FATSECRET = os.getenv('URL_API_FATSECRET')


def get_access_token():
    url = URL_TOKEN_ACCESS_FATSECRET
    auth = (FATSECRET_CLIENT_ID, FATSECRET_CLIENT_SECRET)
    data = {
        "grant_type": "client_credentials",
        "scope": "image-recognition"
    }
    response = requests.post(url, auth=auth, data=data)
    response.raise_for_status()

    return response.json()["access_token"]


def reconocer_imagen(url_imagen):

    response = requests.get(url_imagen)
    response.raise_for_status()

    imagen_b64 = base64.b64encode(response.content).decode('utf-8')

    token = get_access_token()

    api_url = URL_API_FATSECRET
    headers = {"Authorization": f"Bearer {token}"}
    payload = {
        "image_b64": imagen_b64,
        "region": "AR",
        "language": "es",
        "include_food_data": True
    }

    api_res = requests.post(api_url, json=payload, headers=headers)
    api_res.raise_for_status()
    return api_res.json()


def procesar_datos_fasecret(reconocimiento: dict) -> dict:
    try:
        total_calorias = 0
        total_proteinas = 0
        total_grasas = 0
        total_carbohidratos = 0
        total_colesterol = 0

        alimentos = []

        if 'food_response' in reconocimiento:
            for alimento in reconocimiento['food_response']:
                nutricion = alimento.get('eaten', {}).get(
                    'total_nutritional_content', {})

                if nutricion:
                    total_calorias += float(nutricion.get('calories', 0))
                    total_proteinas += float(nutricion.get('protein', 0))
                    total_grasas += float(nutricion.get('fat', 0))
                    total_carbohidratos += float(
                        nutricion.get('carbohydrate', 0))
                    total_colesterol += float(nutricion.get('cholesterol', 0))
                    alimentos.append(alimento)

        return {
            "success": True,
            "calorias": round(total_calorias, 1),
            "proteinas": round(total_proteinas, 1),
            "grasas": round(total_grasas, 1),
            "carbohidratos": round(total_carbohidratos, 1),
            "colesterol": round(total_colesterol, 1),
        }

    except Exception as e:
        return {"success": False, "error": f"Error al procesar datos de FatSecret: {str(e)}"}
