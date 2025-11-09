import os
import json
import requests
import base64
import mimetypes
from dotenv import load_dotenv

load_dotenv()

FATSECRET_CLIENT_ID = os.getenv('FATSECRET_CLIENT_ID')
FATSECRET_CLIENT_SECRET = os.getenv('FATSECRET_CLIENT_SECRET')
URL_TOKEN_ACCESS_FATSECRET = os.getenv('URL_TOKEN_ACCESS_FATSECRET')
URL_API_FATSECRET = os.getenv('URL_API_FATSECRET')
GEMINI_API_URL = os.getenv('GEMINI_API_URL')
GEMINI_API_TOKEN = os.getenv('GEMINI_API_TOKEN')


def get_access_token():
    """Intenta obtener token con scope image-recognition; si el server responde invalid_scope,
    reintenta sin scope para no romper el flujo y permitir fallback.
    """
    url = URL_TOKEN_ACCESS_FATSECRET
    auth = (FATSECRET_CLIENT_ID, FATSECRET_CLIENT_SECRET)
    data = {
        "grant_type": "client_credentials",
        "scope": "image-recognition"
    }
    response = requests.post(url, auth=auth, data=data)

    # Si la cuenta no soporta el scope, algunos servidores devuelven 400 invalid_scope
    if response.status_code == 400:
        try:
            err = response.json()
        except Exception:
            err = {}
        if isinstance(err, dict) and err.get('error') == 'invalid_scope':
            # reintentar sin scope
            data.pop('scope', None)
            response = requests.post(url, auth=auth, data=data)

    response.raise_for_status()
    return response.json().get("access_token")


def reconocer_imagen(url_imagen):
    """Reconoce una imagen con FatSecret; si falla por permisos/scope, cae a un fallback con Gemini
    que devuelve una estructura compatible con 'food_response' y nutrición estimada.
    """
    try:
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
        
        # Parsear JSON primero (puede ser 200 OK pero con error dentro)
        try:
            data_json = api_res.json()
        except Exception:
            data_json = None
        
        # Detectar errores en el cuerpo JSON (incluso si HTTP 200)
        if isinstance(data_json, dict) and 'error' in data_json:
            err_obj = data_json['error']
            if isinstance(err_obj, dict):
                msg = err_obj.get('message', str(err_obj))
                code = err_obj.get('code', '')
            else:
                msg = str(err_obj)
                code = ''
            # Si falta scope, lanzar para activar fallback
            if 'Missing scope' in msg or code == '14':
                raise RuntimeError(f"FatSecret error code {code}: {msg}")
        
        # Si no es 200, lanzar
        api_res.raise_for_status()
        
        return data_json if data_json is not None else api_res.json()
    except Exception:
        # Fallback: Gemini + estimación de macros
        fallback = _reconocer_y_estimar_con_gemini(url_imagen)
        if fallback:
            return fallback
        raise


# ------------------ Fallback con Gemini y estimación de nutrición ------------------

_NUTRI_LOOKUP = {
    # valores aproximados por porción estándar
    "milanesa": {"calories": 420, "protein": 28, "fat": 22, "carbohydrate": 24, "cholesterol": 95},
    "empanada": {"calories": 250, "protein": 10, "fat": 12, "carbohydrate": 24, "cholesterol": 35},
    "pizza": {"calories": 285, "protein": 12, "fat": 10, "carbohydrate": 36, "cholesterol": 22},
    "hamburguesa": {"calories": 300, "protein": 17, "fat": 14, "carbohydrate": 26, "cholesterol": 60},
    "papas fritas": {"calories": 365, "protein": 4, "fat": 17, "carbohydrate": 48, "cholesterol": 0},
    "ensalada": {"calories": 120, "protein": 3, "fat": 7, "carbohydrate": 12, "cholesterol": 5},
    "asado": {"calories": 350, "protein": 30, "fat": 24, "carbohydrate": 0, "cholesterol": 95},
    "pollo": {"calories": 230, "protein": 27, "fat": 12, "carbohydrate": 0, "cholesterol": 85},
    "pescado": {"calories": 200, "protein": 22, "fat": 10, "carbohydrate": 0, "cholesterol": 70},
    "pasta": {"calories": 220, "protein": 8, "fat": 4, "carbohydrate": 42, "cholesterol": 0},
    "arroz": {"calories": 205, "protein": 4, "fat": 0, "carbohydrate": 45, "cholesterol": 0},
    "sándwich": {"calories": 280, "protein": 13, "fat": 9, "carbohydrate": 35, "cholesterol": 45},
    "sandwich": {"calories": 280, "protein": 13, "fat": 9, "carbohydrate": 35, "cholesterol": 45},
}


def _estimar_nutricion(nombre: str):
    n = nombre.lower()
    # match directo
    for k, v in _NUTRI_LOOKUP.items():
        if k in n:
            return v
    # heurísticas simples
    if any(w in n for w in ["ensalada", "verdura", "vegetal"]):
        return {"calories": 120, "protein": 3, "fat": 7, "carbohydrate": 12, "cholesterol": 5}
    if any(w in n for w in ["pizza", "empanada", "tarta"]):
        return {"calories": 270, "protein": 11, "fat": 9, "carbohydrate": 35, "cholesterol": 25}
    if any(w in n for w in ["milanesa", "carne", "asado", "bife", "lomo"]):
        return {"calories": 380, "protein": 27, "fat": 22, "carbohydrate": 4, "cholesterol": 90}
    if any(w in n for w in ["pollo", "pescado"]):
        return {"calories": 220, "protein": 24, "fat": 10, "carbohydrate": 0, "cholesterol": 80}
    if any(w in n for w in ["papa", "arroz", "pasta", "fideos"]):
        return {"calories": 210, "protein": 6, "fat": 3, "carbohydrate": 42, "cholesterol": 0}
    # defecto
    return {"calories": 200, "protein": 8, "fat": 8, "carbohydrate": 22, "cholesterol": 30}


def _build_inline_image_part(url: str):
    try:
        resp = requests.get(url, timeout=20)
        resp.raise_for_status()
        content_type = resp.headers.get('Content-Type', '')
        if content_type.startswith('image/'):
            mime_type = content_type.split(';')[0]
        else:
            mime_type = mimetypes.guess_type(url)[0] or 'image/jpeg'
        b64_data = base64.b64encode(resp.content).decode('utf-8')
        return {"inline_data": {"mime_type": mime_type, "data": b64_data}}
    except Exception:
        return None


def _reconocer_y_estimar_con_gemini(imagen_url: str):
    """Llama a Gemini una sola vez para:
    1. Detectar alimentos
    2. Generar título argentino
    3. Estimar nutrición
    
    Devuelve: {"food_response": [...], "titulo_generado": "..."}
    """
    try:
        if not GEMINI_API_URL or not GEMINI_API_TOKEN:
            return None
        
        prompt = """
Sos un chef argentino experto. Analizá la imagen y devolvé SOLO un JSON con esta estructura exacta:

{
  "alimentos": ["item1", "item2", ...],
  "titulo": "Nombre del plato en estilo argentino"
}

### INSTRUCCIONES PARA "alimentos":
- Detectar máximo 6 alimentos visibles en la foto.
- Usar nombres simples en español: "asado", "papas", "ensalada", "milanesa", etc.

### INSTRUCCIONES PARA "titulo":
1. **PRIORIDAD A LA FOTO**: Observá bien la imagen y nombrá el plato principal que ves.
2. **PLATO PRINCIPAL PRIMERO**: asado, milanesa, empanadas, pizza, pasta, pollo, etc.
3. **NOMBRES DIRECTOS Y SIMPLES**: Sin adjetivos decorativos. Máximo 8 palabras.
4. **ESTILO ARGENTINO**: Usar términos como "a la parrilla", "casero", "napolitana", "de la casa".
5. **NUNCA INVENTAR**: Si ves carne y papas, decí "Asado con papas" o "Bife con guarnición de papas". NO inventes "cordero" ni "salchichas" si no están.

### EJEMPLOS CORRECTOS:
- Foto de milanesa con ensalada → {"alimentos": ["milanesa", "ensalada"], "titulo": "Milanesa con ensalada"}
- Foto de asado con papas → {"alimentos": ["asado", "papas"], "titulo": "Asado con papas"}
- Foto de empanadas → {"alimentos": ["empanada"], "titulo": "Empanadas caseras"}

Respondé SOLO el JSON, sin texto extra ni markdown.
"""
        
        parts = [{"text": prompt}]
        inline_part = _build_inline_image_part(imagen_url)
        if inline_part:
            parts.append(inline_part)
        
        payload = {
            "contents": [{"parts": parts}],
            "generationConfig": {"temperature": 0.3}
        }
        
        resp = requests.post(
            f"{GEMINI_API_URL}?key={GEMINI_API_TOKEN}",
            headers={"Content-Type": "application/json; charset=utf-8"},
            json=payload,
            timeout=30,
        )
        resp.raise_for_status()
        data = resp.json()
        text = data["candidates"][0]["content"]["parts"][0]["text"].strip()
        
        # Parsear JSON (limpiar markdown si existe)
        try:
            result = json.loads(text)
        except Exception:
            # Limpiar ``` y extraer objeto
            t = text.strip('`').strip()
            if t.startswith('json'):
                t = t[4:].strip()
            i, j = t.find('{'), t.rfind('}')
            if i != -1 and j != -1 and j > i:
                result = json.loads(t[i:j+1])
            else:
                return None
        
        # Validar estructura
        if not isinstance(result, dict) or 'alimentos' not in result or 'titulo' not in result:
            return None
        
        nombres = result.get('alimentos', [])
        titulo = result.get('titulo', '').strip()
        
        if not isinstance(nombres, list):
            return None
        
        nombres = [str(n).strip() for n in nombres if str(n).strip()]
        
        # Construir food_response
        food_response = []
        for n in nombres:
            est = _estimar_nutricion(n)
            food_response.append({
                "food_entry_name": n,
                "eaten": {
                    "food_name_singular": n,
                    "total_nutritional_content": est
                }
            })
        
        return {
            "food_response": food_response,
            "titulo_generado": titulo if titulo else None
        }
    except Exception:
        return None


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
