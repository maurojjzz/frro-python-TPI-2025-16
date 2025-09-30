from data.models import Comida
from data.database import SessionLocal
from datetime import datetime
from sqlalchemy.orm import Session


def crear_comida(datos: dict) -> dict:
    try:
        db: Session = SessionLocal()
        nueva_comida = Comida(
            nombre=datos["nombre"],
            descripcion=datos["descripcion"],
            calorias=datos["calorias"],
            grasas=datos["grasas"],
            proteinas=datos["proteinas"],
            carbohidratos=datos["carbohidratos"],
            colesterol=datos["colesterol"],
            fecha_consumo=datetime.strptime(
                datos["fecha_consumo"], "%Y-%m-%d").date(),
            imagen_url=datos.get("imagen_url"),
            usuario_id=datos["usuario_id"]
        )
        db.add(nueva_comida)
        db.commit()
        db.refresh(nueva_comida)
        db.close()

        return {
            "success": True,
            "comida_id": nueva_comida.id,
            "message": "Comida creada exitosamente"
        }
    except Exception as e:
        return {"success": False, "error": f"Error al crear comida: {str(e)}"}


