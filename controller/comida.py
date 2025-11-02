from sqlite3 import Date
from data.models import Comida
from data.database import SessionLocal
from datetime import datetime
from sqlalchemy.orm import Session

from controller.consumo_controller import ConsumoController


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
            fecha_consumo= datetime.now().date(),
            imagen_url=datos.get("imagen_url"),
            usuario_id=datos["usuario_id"]
        )
        db.add(nueva_comida)
        db.commit()
        db.refresh(nueva_comida)
        db.close()
        
        ConsumoController.actualizar_consumo_diario(datos["usuario_id"], datetime.now().date())

        return {
            "success": True,
            "comida_id": nueva_comida.id,
            "message": "Comida creada exitosamente"
        }
    except Exception as e:
        return {"success": False, "error": f"Error al crear comida: {str(e)}"}

