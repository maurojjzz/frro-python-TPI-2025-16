from sqlalchemy.orm import Session
from data.database import SessionLocal
from data.models import Comida
from sqlalchemy import func
from datetime import date
from typing import Dict


class ComidaRepository:

    @staticmethod
    def obtener_totales_dia(usuario_id: int, fecha: date) -> Dict[str, float]:
        db: Session = SessionLocal()
        try:
            resultado = db.query(
                func.sum(Comida.proteinas).label("proteinas"),
                func.sum(Comida.grasas).label("grasas"),
                func.sum(Comida.carbohidratos).label("carbohidratos"),
                func.sum(Comida.calorias).label("calorias"),
                func.sum(Comida.colesterol).label("colesterol")
            ).filter(
                Comida.usuario_id == usuario_id,
                Comida.fecha_consumo == fecha
            ).first()

            return {
                "proteinas": resultado.proteinas or 0,
                "grasas": resultado.grasas or 0,
                "carbohidratos": resultado.carbohidratos or 0,
                "calorias": resultado.calorias or 0,
                "colesterol": resultado.colesterol or 0
            }
        finally:
            db.close()
            
    @staticmethod
    def obtener_consumos_diarios_rango(usuario_id:int, fecha_inicio:date, fecha_fin:date):
        db = SessionLocal()
        try:
            resultados= db.query(
                Comida.fecha_consumo,
                func.sum(Comida.proteinas).label("proteinas"),
                func.sum(Comida.grasas).label("grasas"),
                func.sum(Comida.carbohidratos).label("carbohidratos"),
                func.sum(Comida.calorias).label("calorias"),
                func.sum(Comida.colesterol).label("colesterol")
            ).filter(
                Comida.usuario_id == usuario_id,
                Comida.fecha_consumo.between(fecha_inicio, fecha_fin)
            ).group_by(Comida.fecha_consumo).all()

            return [
                {
                    "fecha": fecha,
                    "proteinas": proteinas or 0,
                    "grasas": grasas or 0,
                    "carbohidratos": carbohidratos or 0,
                    "calorias": calorias or 0,
                    "colesterol": colesterol or 0
                }
                for fecha, proteinas, grasas, carbohidratos, calorias, colesterol in resultados
            ]
        finally:
            db.close()