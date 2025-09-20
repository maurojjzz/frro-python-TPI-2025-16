import os
import requests
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_URL = os.getenv('GEMINI_API_URL')
GEMINI_API_TOKEN = os.getenv('GEMINI_API_TOKEN')


def generar_titulo_con_openai(nombre_alimentos):
    try:
        prompt = f"""
            Eres un chef argentino experto en gastronomía. 
            Crea el **nombre del plato** en español (variante Argentina) para estos ingredientes: {", ".join(nombre_alimentos)}

            ### REGLAS ESTRICTAS:
            1. **PLATO PRINCIPAL**: Detectar si hay empanadas, milanesas, pizza, asado, pasta, sandwich de miga, pollo, pescado, etc. Ese es el núcleo del nombre.
            2. **PRIORIZAR ORDEN**: [Plato principal] → [acompañamiento] → [salsa] → [bebida].
            3. **NOMBRE DIRECTO**: No inventar adjetivos decorativos ni descripciones largas. Ejemplo: 
            - "Spaghetti con salsa de tomate"
            - "Lasaña de salsa blanca"
            - "Sándwich de miga mixto"
            4. **NUNCA LISTAR INGREDIENTES** crudos si corresponden a un plato típico. Si los ingredientes forman un plato reconocido, nombrar directamente el plato.
            5. **CULTURA ARGENTINA**: Mantener términos propios: "a la parrilla", "napolitana", "casero", "de la casa".
            6. **UTF-8 CORRECTO**: Todas las palabras deben aparecer con acentos correctos (ej: “milanesa”, “lasaña”, “sándwich”).

            ### JERARQUÍA DE ALIMENTOS (de mayor a menor importancia):
            1. Platos principales: asado, empanadas, milanesa, pizza, pasta, pollo, pescado.
            2. Acompañamientos: ensalada, papas, puré, verduras, guarnición.
            3. Salsas: criolla, tomate, blanca, chimichurri, mayonesa.
            4. Bebidas: vino, agua, soda, cerveza, jugo.

            ### EJEMPLOS CORRECTOS:
            - ["empanada", "salsa criolla", "vino tinto"] → "Empanadas con salsa criolla y vino tinto"
            - ["pan", "jamón", "queso", "mayonesa"] → "Sándwich de miga mixto"
            - ["carne", "papa", "zanahoria", "cebolla"] → "Estofado de carne con papas y zanahorias"
            - ["pizza", "queso", "salsa tomate"] → "Pizza con muzzarella y salsa de tomate"
            - ["vino blanco", "vino tinto", "queso"] → "Degustación de vinos con quesos regionales"

            ### PARA TUS INGREDIENTES: {", ".join(nombre_alimentos)}
            Analiza: ¿Cuál es el plato principal? ¿Hay acompañamientos, salsas o bebidas? Nombra el plato completo de forma simple y clara.

            ### FORMATEO FINAL:
            - Solo el nombre del plato (máx. 8 palabras).
            - Nada de adornos extra.
            - Asegurarse que se vea natural en una carta de restaurante argentino.
            """

        headers = {
            "Content-Type": "application/json; charset=utf-8",
        }

        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.7,
            },
        }

        response = requests.post(
            f"{GEMINI_API_URL}?key={GEMINI_API_TOKEN}",
            headers=headers,
            json=payload,
            timeout=30
        )
        print(response)

        if response.status_code == 200:
            resultado = response.json()
            titulo = resultado["candidates"][0]["content"]["parts"][0]["text"].strip(
            )

            titulo = titulo.replace('"', '').replace("'", "").strip()
            return titulo
        else:
            print(
                f"Error al generar el título con Gemini: {response.status_code}")
            return generar_titulo_simple(nombre_alimentos)
    except Exception as e:
        print(f"Error al generar el título con Gemini: {str(e)}")
        return generar_titulo_simple(nombre_alimentos)


def generar_titulo_simple(nombres_alimentos):
    if not nombres_alimentos:
        return "Delicioso plato gourmet"

    if len(nombres_alimentos) == 1:
        return f"Plato de {nombres_alimentos[0]}"
    elif len(nombres_alimentos) == 2:
        return f"{nombres_alimentos[0]} con {nombres_alimentos[1]}"
    else:
        return f"Combinacion de {', '.join(nombres_alimentos[:-1])} y {nombres_alimentos[-1]}"


def extraer_nombres_de_fatsecret(respuesta_fatsecret):
    if not respuesta_fatsecret or 'food_response' not in respuesta_fatsecret:
        return []

    nombres = []

    for item in respuesta_fatsecret["food_response"]:
        entry_name = item.get("food_entry_name", "").strip()
        singular_name = item.get("eaten", {}).get(
            "food_name_singular", "").strip()

        if entry_name and len(entry_name.split()) > 1:
            nombre_elegido = entry_name
        else:
            nombre_elegido = singular_name or entry_name

        if nombre_elegido:
            nombre_limpio = nombre_elegido.split('(')[0].strip()
            if nombre_limpio:
                nombres.append(nombre_limpio)

    return nombres
